#!/usr/bin/env python3
"""End-to-end skill testing using Claude Agent SDK.

For each test case:
1. Generation phase: Load skill content as system prompt, send user prompt to
   Claude via query(). Only read-only tools are available.
2. Evaluation phase: Send generated response + expected criteria to a second
   query() with structured output. Returns pass/fail per criterion.
3. Report: Aggregate results in PASS/FAIL format matching validate_skill.py.
"""

import argparse
import asyncio
import dataclasses
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow running inside a Claude Code session (e.g. during development)
os.environ.pop("CLAUDECODE", None)

import yaml

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)


# ---------------------------------------------------------------------------
# Dataclasses for rich return types
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class GenerationResult:
    response_text: str
    conversation_trace: list[dict]
    duration_ms: int = 0
    duration_api_ms: int = 0
    cost_usd: float | None = None
    num_turns: int = 0
    session_id: str = ""
    usage: dict | None = None


@dataclasses.dataclass
class EvaluationResult:
    evaluation: dict
    duration_ms: int = 0
    duration_api_ms: int = 0
    cost_usd: float | None = None
    num_turns: int = 0
    session_id: str = ""
    usage: dict | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TRACE_CONTENT_LIMIT = 2000


def slugify(name: str) -> str:
    """Convert a name to a filesystem-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "unnamed"


def _truncate(content, limit: int = TRACE_CONTENT_LIMIT) -> str | list | None:
    """Truncate tool result content for trace storage."""
    if content is None:
        return None
    if isinstance(content, str):
        if len(content) > limit:
            return content[:limit] + f"... [truncated, {len(content)} chars total]"
        return content
    if isinstance(content, list):
        serialized = json.dumps(content)
        if len(serialized) > limit:
            return serialized[:limit] + f"... [truncated, {len(serialized)} chars total]"
        return content
    return str(content)[:limit]


# ---------------------------------------------------------------------------
# ValidationResult (same pattern as validate_skill.py)
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self):
        self.results = []  # list of (level, check_name, message)

    def add(self, level: str, check: str, message: str):
        self.results.append((level, check, message))

    def passed(self, check: str, message: str):
        self.add("PASS", check, message)

    def warn(self, check: str, message: str):
        self.add("WARN", check, message)

    def fail(self, check: str, message: str):
        self.add("FAIL", check, message)

    def print_report(self):
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for level, check, message in self.results:
            counts[level] += 1
            marker = {"PASS": "+", "WARN": "~", "FAIL": "!"}[level]
            print(f"  [{marker}] {level}: {check} — {message}")
        print()
        print(f"  Summary: {counts['PASS']} passed, {counts['WARN']} warnings, {counts['FAIL']} failures")
        return counts["FAIL"] == 0

    @property
    def has_failures(self):
        return any(level == "FAIL" for level, _, _ in self.results)

    def to_dict(self) -> dict:
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        entries = []
        for level, check, message in self.results:
            counts[level] += 1
            entries.append({"level": level, "check": check, "message": message})
        return {"results": entries, "summary": counts}


# ---------------------------------------------------------------------------
# Skill content loading
# ---------------------------------------------------------------------------

def load_full_skill_content(skill_dir: Path) -> str:
    """Load SKILL.md + all referenced files as a single string."""
    parts = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        parts.append(f"# SKILL.md\n\n{skill_md.read_text()}")

    for subdir in ["references", "templates", "examples"]:
        d = skill_dir / subdir
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix in (".md", ".py", ".yaml", ".yml"):
                    rel = f.relative_to(skill_dir)
                    parts.append(f"# {rel}\n\n{f.read_text()}")

    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Evaluation schema for structured output
# ---------------------------------------------------------------------------

EVAL_SCHEMA = {
    "type": "object",
    "properties": {
        "criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterion": {"type": "string"},
                    "passed": {"type": "boolean"},
                    "reasoning": {"type": "string"},
                },
                "required": ["criterion", "passed", "reasoning"],
                "additionalProperties": False,
            },
        },
        "overall_pass": {"type": "boolean"},
    },
    "required": ["criteria", "overall_pass"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Core test execution
# ---------------------------------------------------------------------------

async def collect_response(messages) -> tuple[str, dict | None, ResultMessage | None, list[dict]]:
    """Iterate through query messages and collect text + structured output + trace.

    Returns (text, structured_output_dict_or_None, result_message_or_None, conversation_trace).
    Structured output arrives via a ToolUseBlock named 'StructuredOutput'.
    """
    text_parts = []
    structured = None
    result_msg = None
    trace = []
    async for message in messages:
        if isinstance(message, ResultMessage):
            result_msg = message
            if message.result:
                text_parts.append(message.result)
            if message.structured_output:
                structured = message.structured_output
        elif isinstance(message, AssistantMessage):
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
                        trace.append({"role": "assistant", "type": "text", "text": block.text})
                    elif isinstance(block, ToolUseBlock):
                        if block.name == "StructuredOutput":
                            structured = block.input
                        else:
                            trace.append({
                                "role": "assistant",
                                "type": "tool_use",
                                "tool": block.name,
                                "input": block.input,
                            })
        elif isinstance(message, UserMessage):
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        trace.append({
                            "role": "tool_result",
                            "tool_use_id": block.tool_use_id,
                            "content": _truncate(block.content),
                            "is_error": bool(block.is_error),
                        })
    return "\n".join(text_parts), structured, result_msg, trace


async def generate_response(
    skill_content: str,
    user_prompt: str,
    skill_dir: Path,
    model: str = "haiku",
    max_turns: int = 5,
    max_budget_usd: float = 0.50,
) -> GenerationResult:
    """Phase 1: Generate a response using the skill as system prompt."""
    options = ClaudeAgentOptions(
        system_prompt=skill_content,
        allowed_tools=["Read", "Grep", "Glob"],
        disallowed_tools=["Write", "Edit", "Bash", "Skill", "NotebookEdit"],
        permission_mode="bypassPermissions",
        cwd=str(skill_dir),
        max_turns=max_turns,
        max_budget_usd=max_budget_usd,
        model=model,
    )

    t0 = time.monotonic()
    text, _, result_msg, trace = await collect_response(query(prompt=user_prompt, options=options))
    wall_ms = int((time.monotonic() - t0) * 1000)

    gen = GenerationResult(response_text=text, conversation_trace=trace)
    if result_msg:
        gen.duration_ms = wall_ms
        gen.duration_api_ms = result_msg.duration_api_ms
        gen.cost_usd = result_msg.total_cost_usd
        gen.num_turns = result_msg.num_turns
        gen.session_id = result_msg.session_id
        gen.usage = result_msg.usage
    return gen


async def evaluate_response(
    response: str,
    expected: list[str],
    model: str = "haiku",
) -> EvaluationResult:
    """Phase 2: Evaluate the generated response against expected criteria."""
    eval_prompt = (
        "Evaluate the following RESPONSE against each CRITERION.\n"
        "A criterion passes if the response demonstrates knowledge of or correctly "
        "addresses the concept described. Minor wording differences are acceptable — "
        "focus on whether the semantic intent of each criterion is met.\n\n"
        f"RESPONSE:\n{response}\n\n"
        f"CRITERIA:\n"
    )
    for i, criterion in enumerate(expected, 1):
        eval_prompt += f"{i}. {criterion}\n"

    options = ClaudeAgentOptions(
        system_prompt=(
            "You are a test evaluator. You receive a response and a list of criteria. "
            "For each criterion, determine if the response satisfies it. "
            "Return structured JSON with your evaluation."
        ),
        allowed_tools=[],
        permission_mode="bypassPermissions",
        max_turns=1,
        model=model,
        output_format={"type": "json_schema", "schema": EVAL_SCHEMA},
    )

    t0 = time.monotonic()
    text, structured, result_msg, _ = await collect_response(query(prompt=eval_prompt, options=options))
    wall_ms = int((time.monotonic() - t0) * 1000)

    # Prefer structured output (from StructuredOutput tool), then try parsing text
    evaluation = None
    if structured:
        if isinstance(structured, dict):
            evaluation = structured
        elif isinstance(structured, str):
            try:
                evaluation = json.loads(structured)
            except (json.JSONDecodeError, TypeError):
                pass

    if evaluation is None:
        try:
            evaluation = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            evaluation = {
                "criteria": [
                    {"criterion": c, "passed": False, "reasoning": "Evaluation failed to produce valid JSON"}
                    for c in expected
                ],
                "overall_pass": False,
            }

    ev = EvaluationResult(evaluation=evaluation)
    if result_msg:
        ev.duration_ms = wall_ms
        ev.duration_api_ms = result_msg.duration_api_ms
        ev.cost_usd = result_msg.total_cost_usd
        ev.num_turns = result_msg.num_turns
        ev.session_id = result_msg.session_id
        ev.usage = result_msg.usage
    return ev


async def run_test(
    test: dict,
    skill_content: str,
    skill_dir: Path,
    config: dict,
    result: ValidationResult,
    dry_run: bool = False,
) -> dict | None:
    """Run a single test case through generate + evaluate.

    Returns a per-test detail dict for history, or None on validation errors.
    """
    name = test.get("name", "unnamed")
    prompt = test.get("prompt", "")
    expected = test.get("expected", [])

    if not prompt:
        result.fail(name, "No prompt defined")
        return None

    if not expected:
        result.fail(name, "No expected criteria defined")
        return None

    model = config.get("model", "haiku")
    max_turns = config.get("max_turns", 5)
    max_budget_usd = config.get("max_budget_usd", 0.50)
    test_config = {"model": model, "max_turns": max_turns, "max_budget_usd": max_budget_usd}

    detail = {
        "name": name,
        "prompt": prompt,
        "expected": expected,
        "config": test_config,
        "generation": None,
        "evaluation": None,
        "error": None,
    }

    if dry_run:
        detail["level"] = "PASS"
        result.passed(name, f"All {len(expected)} criteria passed (dry-run)")
        return detail

    try:
        # Phase 1: Generate
        gen = await generate_response(
            skill_content, prompt, skill_dir,
            model=model, max_turns=max_turns, max_budget_usd=max_budget_usd,
        )

        detail["generation"] = {
            "response_text": gen.response_text,
            "conversation_trace": gen.conversation_trace,
            "duration_ms": gen.duration_ms,
            "duration_api_ms": gen.duration_api_ms,
            "cost_usd": gen.cost_usd,
            "num_turns": gen.num_turns,
            "session_id": gen.session_id,
            "usage": gen.usage,
        }

        if not gen.response_text.strip():
            detail["level"] = "FAIL"
            detail["error"] = "Generation produced empty response"
            result.fail(name, "Generation produced empty response")
            return detail

        # Phase 2: Evaluate
        ev = await evaluate_response(gen.response_text, expected, model=model)

        evaluation = ev.evaluation
        detail["evaluation"] = {
            "overall_pass": evaluation.get("overall_pass", False),
            "criteria": evaluation.get("criteria", []),
            "duration_ms": ev.duration_ms,
            "duration_api_ms": ev.duration_api_ms,
            "cost_usd": ev.cost_usd,
            "num_turns": ev.num_turns,
            "session_id": ev.session_id,
            "usage": ev.usage,
        }

        # Process results
        criteria = evaluation.get("criteria", [])
        failed_criteria = [
            c for c in criteria
            if isinstance(c, dict) and not c.get("passed", False)
        ]

        if not failed_criteria:
            detail["level"] = "PASS"
            result.passed(name, f"All {len(expected)} criteria passed")
        else:
            detail["level"] = "FAIL"
            reasons = "; ".join(
                f"{c['criterion']}: {c.get('reasoning', 'no reason')}"
                for c in failed_criteria
            )
            result.fail(name, f"{len(failed_criteria)}/{len(expected)} criteria failed — {reasons}")

    except Exception as e:
        detail["level"] = "FAIL"
        detail["error"] = str(e)
        result.fail(name, f"Error: {e}")

    return detail


# ---------------------------------------------------------------------------
# Suite and discovery
# ---------------------------------------------------------------------------

async def run_suite(
    test_file: Path,
    skill_dir: Path,
    result: ValidationResult,
    dry_run: bool = False,
) -> list[dict]:
    """Load and run all tests from a YAML test file.

    Returns list of per-test detail dicts for history.
    """
    try:
        data = yaml.safe_load(test_file.read_text())
    except yaml.YAMLError as e:
        result.fail(test_file.name, f"Invalid YAML: {e}")
        return []

    if not data or "tests" not in data:
        result.warn(test_file.name, "No tests defined")
        return []

    suite_name = data.get("suite", test_file.stem)
    config = data.get("config", {})
    print(f"  Suite: {suite_name}")

    # Resolve skill_path if specified
    skill_path = data.get("skill_path", ".")
    resolved_skill_dir = (test_file.parent / skill_path).resolve()
    if not resolved_skill_dir.is_dir():
        result.fail(suite_name, f"skill_path resolves to non-existent directory: {resolved_skill_dir}")
        return []

    # Load skill content once for all tests in the suite
    skill_content = load_full_skill_content(resolved_skill_dir)
    if not skill_content.strip():
        result.fail(suite_name, "Skill content is empty")
        return []

    details = []
    for test in data["tests"]:
        name = test.get("name", "unnamed")
        print(f"    Running: {name}...", end=" ", flush=True)
        detail = await run_test(test, skill_content, resolved_skill_dir, config, result, dry_run=dry_run)
        # Print inline status
        last = result.results[-1]
        print(f"[{last[0]}]")
        if detail is not None:
            detail["suite"] = suite_name
            details.append(detail)

    return details


def discover_test_files(skill_dir: Path) -> list[Path]:
    """Find all YAML test files in the skill's tests/ directory."""
    tests_dir = skill_dir / "tests"
    if not tests_dir.is_dir():
        return []
    return sorted(tests_dir.glob("test_*.yaml")) + sorted(tests_dir.glob("test_*.yml"))


def discover_all_skills(repo_root: Path) -> list[Path]:
    """Discover all skill directories under skills/ and plugins/**/skills/."""
    skill_dirs = []

    skills_dir = repo_root / "skills"
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                skill_dirs.append(d)

    plugins_dir = repo_root / "plugins"
    if plugins_dir.is_dir():
        for skill_md in sorted(plugins_dir.rglob("SKILL.md")):
            skill_dirs.append(skill_md.parent)

    return skill_dirs


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

HISTORY_DIR_NAME = ".test-history"


def save_history(
    repo_root: Path,
    timestamp: str,
    overall_success: bool,
    dry_run: bool,
    skill_summaries: list[dict],
    all_details: list[dict],
):
    """Save structured test history under .test-history/runs/<timestamp>/."""
    history_dir = repo_root / HISTORY_DIR_NAME
    runs_dir = history_dir / "runs"
    run_dir = runs_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Compute totals
    total_cost = 0.0
    total_duration = 0
    total_tests = 0
    total_passed = 0
    total_warned = 0
    total_failed = 0
    for s in skill_summaries:
        total_cost += s.get("cost_usd", 0) or 0
        total_duration += s.get("duration_ms", 0) or 0
        counts = s.get("summary", {})
        total_passed += counts.get("PASS", 0)
        total_warned += counts.get("WARN", 0)
        total_failed += counts.get("FAIL", 0)
    total_tests = total_passed + total_warned + total_failed

    summary = {
        "timestamp": timestamp,
        "overall_success": overall_success,
        "dry_run": dry_run,
        "totals": {
            "cost_usd": round(total_cost, 6),
            "duration_ms": total_duration,
            "tests": total_tests,
            "passed": total_passed,
            "warned": total_warned,
            "failed": total_failed,
        },
        "skills": skill_summaries,
    }

    # Write summary.json
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    # Write per-test detail files organized by skill/suite
    for detail in all_details:
        skill_name = detail.pop("_skill", "unknown")
        suite_name = detail.pop("suite", "default")
        test_slug = slugify(detail.get("name", "unnamed"))
        test_dir = run_dir / skill_name / suite_name
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"{test_slug}.json"
        test_path.write_text(json.dumps(detail, indent=2) + "\n")

    # Update latest symlink
    latest_link = history_dir / "latest"
    if latest_link.is_symlink() or latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(f"runs/{timestamp}")

    print(f"  History saved: {run_dir.relative_to(repo_root)}/")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def async_main():
    parser = argparse.ArgumentParser(description="End-to-end skill testing with Claude Agent SDK.")
    parser.add_argument("skill_dir", nargs="?", help="Path to the skill directory to test")
    parser.add_argument("--all", action="store_true", help="Discover and test all skills")
    parser.add_argument("--no-history", action="store_true", help="Skip saving test history")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls; mark all tests as passed with mock results")
    args = parser.parse_args()

    if not args.all and not args.skill_dir:
        parser.error("Provide a skill directory or use --all")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent

    if args.all:
        skill_dirs = discover_all_skills(repo_root)
        if not skill_dirs:
            print("No skills found.")
            sys.exit(0)
    else:
        skill_dirs = [Path(args.skill_dir).resolve()]

    overall_success = True
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    skill_summaries = []
    all_details = []

    for skill_dir in skill_dirs:
        if not skill_dir.is_dir():
            print(f"Error: {skill_dir} is not a directory")
            overall_success = False
            continue

        test_files = discover_test_files(skill_dir)
        if not test_files:
            print(f"Testing skill: {skill_dir.name}")
            print(f"  Path: {skill_dir}")
            print(f"  No test files found in tests/")
            print()
            continue

        print(f"Testing skill: {skill_dir.name}")
        print(f"  Path: {skill_dir}")
        print()

        result = ValidationResult()
        skill_details = []

        for test_file in test_files:
            suite_details = await run_suite(test_file, skill_dir, result, dry_run=args.dry_run)
            skill_details.extend(suite_details)

        print()
        success = result.print_report()
        if not success:
            overall_success = False
        print()

        # Compute per-skill aggregates from detail dicts
        skill_cost = 0.0
        skill_duration = 0
        for d in skill_details:
            gen = d.get("generation")
            ev = d.get("evaluation")
            if gen:
                skill_cost += gen.get("cost_usd") or 0
                skill_duration += gen.get("duration_ms") or 0
            if ev:
                skill_cost += ev.get("cost_usd") or 0
                skill_duration += ev.get("duration_ms") or 0

        # Read config from first test file for the summary
        first_data = yaml.safe_load(test_files[0].read_text()) if test_files else {}
        config = first_data.get("config", {})

        skill_summaries.append({
            "skill": skill_dir.name,
            "path": str(skill_dir.relative_to(repo_root)),
            "config": config,
            "summary": result.to_dict()["summary"],
            "cost_usd": round(skill_cost, 6),
            "duration_ms": skill_duration,
        })

        # Tag details with skill name for directory organization
        for d in skill_details:
            d["_skill"] = skill_dir.name
        all_details.extend(skill_details)

    if not args.no_history and skill_summaries:
        save_history(repo_root, timestamp, overall_success, args.dry_run, skill_summaries, all_details)

    sys.exit(0 if overall_success else 1)


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
