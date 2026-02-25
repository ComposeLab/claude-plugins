# Test Writing Guide

This reference explains how to write test scenarios for Claude Code skills. Tests verify that a skill produces correct behavior when Claude uses it — complementing validation, which only checks structure and style.

## How Skill Testing Works

The test runner (`scripts/test_skill.py`) executes a two-phase process for each test case:

1. **Generation phase:** The skill's full content (SKILL.md + all references, templates, examples) is loaded as a system prompt. The test's user prompt is sent to Claude, which responds as if it were using the skill. Only read-only tools (Read, Grep, Glob) are available during generation.

2. **Evaluation phase:** The generated response is sent to a second Claude call along with the test's expected criteria. Claude evaluates whether each criterion is met and returns structured pass/fail results.

This two-phase approach means tests can verify skill behavior without executing side effects — Claude generates a response but does not modify files, run scripts, or take actions.

## YAML Format

Test files live in `tests/test_scenarios.yaml` within the skill directory. The format:

```yaml
suite: descriptive-suite-name
skill_path: ..  # relative path from tests/ to the skill directory

config:
  model: haiku        # model for generation and evaluation
  max_turns: 5        # max agentic turns during generation
  max_budget_usd: 0.50  # spending cap per test case

tests:
  - name: descriptive test name
    prompt: "A natural-language prompt simulating what a user would ask"
    expected:
      - "First criterion the response should satisfy"
      - "Second criterion the response should satisfy"
```

### Top-Level Fields

- **suite**: A descriptive name for the test suite, used in reports and history. Convention is kebab-case matching the file purpose.
- **skill_path**: Relative path from the test file to the skill directory root. Since tests live in `tests/`, this is typically `..`.
- **config**: Default configuration applied to all tests in the suite.
- **tests**: List of individual test cases.

### Config Options

- **model**: Which Claude model to use. `haiku` is recommended for speed and cost during development. Use `sonnet` for more nuanced evaluation when needed. Default: `haiku`.
- **max_turns**: Maximum agentic turns (API round-trips) during generation. Higher values allow Claude to read more files but increase cost and time. Default: `5`.
- **max_budget_usd**: Spending cap per individual test case. Prevents runaway costs. Default: `0.50`.

### Test Case Fields

- **name**: Human-readable name shown in reports. Should describe what the test verifies.
- **prompt**: The user message sent to Claude with the skill loaded. Write this as a realistic user request — something someone would actually ask the skill to do.
- **expected**: List of criteria the response must satisfy. Each criterion is a plain-language statement that the evaluator checks against the response.

## Writing Effective Prompts

Test prompts should simulate realistic user requests. They work best when they are specific enough to produce a focused response but not so prescriptive that they bypass the skill's decision-making.

A prompt like "Walk me through creating a new skill called code-review" tests whether the skill guides the full workflow. A prompt like "What are the required frontmatter fields?" tests whether the skill correctly communicates specific knowledge.

Avoid prompts that test Claude's general knowledge rather than the skill's instructions. The goal is to verify that the skill's instructions produce correct behavior, not that Claude knows things independently.

## Writing Effective Criteria

Each criterion should test one specific aspect of the response. Criteria that bundle multiple checks ("Mentions validation AND explains why it matters") make failures harder to diagnose — split them into separate criteria.

Criteria should be semantic, not lexical. "Mentions keeping the body concise or under a line limit" is better than "Contains the phrase 'under 100 lines'" because Claude might express the concept differently while still being correct.

The evaluator is generous with wording differences. Focus criteria on whether the response demonstrates the right knowledge or follows the right process, not on exact phrasing.

## How Many Tests to Write

Cover each main workflow or capability of the skill. A skill with three workflows needs at least three tests. For the primary workflow, consider additional tests for important variations or edge cases.

Aim for 4-8 tests for a typical skill. Fewer than 3 tests leaves significant behavior untested. More than 12 suggests either the skill is very complex (consider splitting it) or the tests are too granular.

## Running Tests

Run tests for a specific skill:

```
python skills/create-skills/scripts/test_skill.py <path-to-skill-dir>
```

Run tests for all skills:

```
python skills/create-skills/scripts/test_skill.py --all
```

Dry run (validate YAML and structure without calling the API):

```
python skills/create-skills/scripts/test_skill.py <path-to-skill-dir> --dry-run
```

The test runner produces a PASS/WARN/FAIL report matching the format used by `validate_skill.py`. Test history is saved automatically under `.test-history/` for tracking results over time.

## Integration Tests

Skills that document external libraries need a second layer of testing beyond scenario tests. The two layers serve different purposes:

**Scenario tests** (test_scenarios.yaml) verify that the skill instructs Claude correctly. They test the skill as a prompt — does Claude produce responses that demonstrate the right knowledge and follow the right process? These tests catch ambiguous instructions, missing references, and gaps in the skill's guidance.

**Integration tests** (test_*_integration.py) verify that the documented APIs actually work. They import the real library, call the real methods, and assert on real results. These tests catch wrong import paths, incorrect method signatures, nonexistent config fields, and other factual errors in the references.

The distinction matters because scenario tests can pass even when the references contain factual errors. An AI evaluator sees a plausible response mentioning the right concepts and marks it as passing — it cannot verify whether `from mq import get_cache` is a real import. Integration tests catch these errors immediately because Python raises ImportError on the spot.

### When to Write Integration Tests

Write integration tests when the skill's reference files contain Python code blocks with `import` statements or `from X import Y` patterns. These claims are verifiable and should be verified.

Skills that need integration tests:
- Skills documenting a library's API (core-db, core-mq)
- Skills showing config formats that a library parses
- Skills with code examples users would copy into their projects

Skills that do NOT need integration tests:
- Workflow-only skills (create-skills, code review workflows)
- Meta skills that coordinate other skills
- Skills that only use Claude's built-in tools

### Structure

Integration test files live in `tests/` alongside the scenario YAML file. Name them `test_<topic>_integration.py`. See [Integration Testing Guide](integration-testing-guide.md) for detailed guidance on structure, fixtures, and what to test.

## Iterating on Failures

When a test fails, the report shows which criteria failed and the evaluator's reasoning. Common causes:

- **Ambiguous skill instructions**: Claude interpreted the instructions differently than intended. Clarify the SKILL.md body or references.
- **Overly specific criteria**: The criterion demands exact phrasing that Claude doesn't use. Rewrite to focus on semantic intent.
- **Insufficient context**: The skill references knowledge that isn't loaded during testing. Ensure all relevant references are in the skill directory.
- **Wrong model for the task**: Haiku may miss nuances that sonnet catches. Try upgrading the model in config if criteria are semantically met but the evaluator disagrees.
