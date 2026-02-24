#!/usr/bin/env python3
"""Validate a Claude Code skill directory for structural correctness and quality heuristics."""

import argparse
import re
import sys
from pathlib import Path

import yaml


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


def parse_frontmatter(text: str):
    """Extract YAML frontmatter from markdown text."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not match:
        return None, text
    try:
        fm = yaml.safe_load(match.group(1))
        body = text[match.end():]
        return fm, body
    except yaml.YAMLError:
        return None, text


def check_skill_md_exists(skill_dir: Path, result: ValidationResult):
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        result.passed("skill-md-exists", "SKILL.md found")
        return True
    else:
        result.fail("skill-md-exists", "SKILL.md not found in skill directory")
        return False


def check_frontmatter(skill_dir: Path, result: ValidationResult):
    text = (skill_dir / "SKILL.md").read_text()
    fm, body = parse_frontmatter(text)

    if fm is None:
        result.fail("frontmatter-valid", "No valid YAML frontmatter found")
        return None, body

    result.passed("frontmatter-valid", "YAML frontmatter parsed successfully")

    # Required fields
    required = ["name", "description", "version"]
    for field in required:
        if field in fm:
            result.passed(f"frontmatter-{field}", f"Field '{field}' present")
        else:
            result.fail(f"frontmatter-{field}", f"Required field '{field}' missing from frontmatter")

    # Name is kebab-case
    if "name" in fm:
        name = fm["name"]
        if re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', str(name)):
            result.passed("name-kebab-case", f"Name '{name}' is valid kebab-case")
        else:
            result.fail("name-kebab-case", f"Name '{name}' is not kebab-case (expected lowercase, hyphens only)")

    # Name matches directory
    if "name" in fm:
        if str(fm["name"]) == skill_dir.name:
            result.passed("name-matches-dir", f"Frontmatter name matches directory name")
        else:
            result.warn("name-matches-dir", f"Frontmatter name '{fm['name']}' differs from directory '{skill_dir.name}'")

    return fm, body


def check_description_third_person(fm: dict, result: ValidationResult):
    if not fm or "description" not in fm:
        return
    desc = str(fm["description"])
    # Third-person descriptions typically start with a verb in third-person form (ends in 's')
    # or a gerund. Check that it does NOT start with imperative or second-person.
    first_word = desc.split()[0] if desc.split() else ""
    second_person_starts = ["you", "your"]
    if first_word.lower() in second_person_starts:
        result.warn("description-third-person", f"Description starts with '{first_word}' — prefer third-person ('Creates...', 'Provides...')")
    else:
        result.passed("description-third-person", "Description avoids second-person opening")


def check_triggers(fm: dict, result: ValidationResult):
    if not fm:
        return
    triggers = fm.get("triggers") or fm.get("trigger_phrases")
    if triggers and len(triggers) >= 2:
        result.passed("trigger-phrases", f"Found {len(triggers)} trigger phrases")
    elif triggers:
        result.warn("trigger-phrases", "Only 1 trigger phrase — consider adding more for discoverability")
    else:
        result.warn("trigger-phrases", "No trigger phrases found in frontmatter")


def check_body_quality(body: str, result: ValidationResult):
    lines = body.strip().split('\n')
    line_count = len(lines)

    # Line count
    if line_count > 500:
        result.fail("body-line-count", f"Body is {line_count} lines — should be under 500")
    elif line_count > 200:
        result.warn("body-line-count", f"Body is {line_count} lines — consider delegating detail to references")
    else:
        result.passed("body-line-count", f"Body is {line_count} lines")

    # No second-person in body
    second_person_pattern = re.compile(r'\b(you|your|you\'re|you\'ll|you\'ve|yourself)\b', re.IGNORECASE)
    second_person_lines = []
    for i, line in enumerate(lines, 1):
        # Skip frontmatter references, code blocks, and comments
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('#') or stripped.startswith('<!--'):
            continue
        if second_person_pattern.search(line):
            second_person_lines.append(i)

    if second_person_lines:
        sample = second_person_lines[:3]
        result.warn("no-second-person", f"Second-person language found on lines: {sample}")
    else:
        result.passed("no-second-person", "No second-person language in body")

    # Imperative form check — look for "The agent should" or "Claude should" patterns
    passive_pattern = re.compile(r'\b(the agent should|claude should|it should|the skill should)\b', re.IGNORECASE)
    passive_lines = []
    for i, line in enumerate(lines, 1):
        if passive_pattern.search(line):
            passive_lines.append(i)
    if passive_lines:
        result.warn("imperative-form", f"Non-imperative phrasing found on lines: {passive_lines[:3]} — prefer imperative ('Read...' not 'The agent should read...')")
    else:
        result.passed("imperative-form", "Instructions use imperative form")


def check_referenced_files(skill_dir: Path, body: str, result: ValidationResult):
    """Check that files referenced in the body actually exist."""
    # Match patterns like references/foo.md, templates/bar.md, scripts/baz.py, examples/qux.md
    ref_pattern = re.compile(r'(?:references|templates|examples|scripts)/[a-zA-Z0-9_-]+\.\w+')
    referenced = set(ref_pattern.findall(body))

    # Also check frontmatter area by reading full file
    full_text = (skill_dir / "SKILL.md").read_text()
    referenced.update(ref_pattern.findall(full_text))

    if not referenced:
        result.warn("referenced-files", "No file references detected in SKILL.md")
        return

    missing = []
    for ref in sorted(referenced):
        if not (skill_dir / ref).exists():
            missing.append(ref)

    if missing:
        result.fail("referenced-files", f"Referenced files not found: {missing}")
    else:
        result.passed("referenced-files", f"All {len(referenced)} referenced files exist")


def check_no_comparison_patterns(skill_dir: Path, result: ValidationResult):
    """Check that no files use good/bad comparison list patterns."""
    patterns = [
        re.compile(r'[❌✅]'),
        re.compile(r'^\s*[-*]\s*(Good|Bad|Do|Don\'t|Correct|Incorrect|Right|Wrong)\s*:', re.IGNORECASE | re.MULTILINE),
    ]
    flagged_files = []

    for md_file in skill_dir.rglob("*.md"):
        content = md_file.read_text()
        for pattern in patterns:
            if pattern.search(content):
                rel = md_file.relative_to(skill_dir)
                flagged_files.append(str(rel))
                break

    if flagged_files:
        result.warn("no-comparison-patterns", f"Good/bad comparison patterns found in: {flagged_files}")
    else:
        result.passed("no-comparison-patterns", "No good/bad comparison patterns detected")


def main():
    parser = argparse.ArgumentParser(description="Validate a Claude Code skill directory.")
    parser.add_argument("skill_dir", help="Path to the skill directory to validate")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()

    if not skill_dir.is_dir():
        print(f"Error: {skill_dir} is not a directory")
        sys.exit(1)

    print(f"Validating skill: {skill_dir.name}")
    print(f"  Path: {skill_dir}")
    print()

    result = ValidationResult()

    # Structural checks
    if not check_skill_md_exists(skill_dir, result):
        result.print_report()
        sys.exit(1)

    fm, body = check_frontmatter(skill_dir, result)
    check_description_third_person(fm, result)
    check_triggers(fm, result)

    # Quality checks
    check_body_quality(body, result)
    check_referenced_files(skill_dir, body, result)
    check_no_comparison_patterns(skill_dir, result)

    print()
    success = result.print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
