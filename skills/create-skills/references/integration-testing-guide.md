# Integration Testing Guide

This reference explains when and how to write integration tests for skills that document external libraries. Integration tests complement scenario tests by verifying that the APIs documented in a skill actually work as described.

## Why Integration Tests Exist

Scenario tests (test_scenarios.yaml) verify that Claude follows the skill's instructions correctly — they test the skill as a prompt. But scenario tests cannot catch a reference that claims `from mq import get_cache` works when `get_cache` is not actually exported. The AI evaluator sees a plausible-looking response and marks it as passing.

Integration tests exercise the real library. They import the actual modules, call the actual methods, and assert on actual results. When an import path is wrong, the test fails immediately with an ImportError — no ambiguity, no AI evaluation needed.

The core-mq skill demonstrated this gap: all 8 scenario tests passed while multiple import paths in the references were incorrect. Only integration tests that ran `from mq import Bus, Message, setup_bus_factory` caught the real bugs.

## When Integration Tests Are Needed

Write integration tests when a skill documents an external library with importable APIs. The signal is: if your reference files contain `import` statements, `from X import Y` patterns, or code examples that a user would copy and run, those claims need verification.

Concrete indicators:
- Reference files show import paths users should use
- Code examples demonstrate calling library methods
- Config formats that the library parses (YAML schemas, env vars)
- Method signatures with specific parameters and return types

## When Integration Tests Are NOT Needed

Some skills are pure workflow coordinators — they guide a process but do not document a specific library's API. These skills need only scenario tests.

Examples that do not need integration tests:
- Meta skills like create-skills itself (documents a process, not a library)
- Workflow skills that orchestrate Claude's built-in tools (Read, Grep, Glob)
- Style guide skills that enforce conventions without referencing importable code

The key question: does the skill claim specific things are importable or callable? If no, scenario tests suffice.

## What to Test

Focus integration tests on the documented user experience, not the library's internals. Test what the skill tells users to do:

**Import paths**: If the skill says `from mq import Bus, Message, setup_bus_factory`, verify those imports work.

**Core workflows**: Mirror the steps a user follows. For core-mq, that means: write YAML config → load config → set up factory → get a bus → start → publish/consume → close. Each step in the workflow should appear in at least one test.

**Model/object creation**: If the skill documents creating objects (Messages, configs, models), test that creation works with the documented fields.

**Error cases**: If the skill documents expected errors (e.g., "raises RuntimeError if setup not called"), verify the error actually occurs.

**Config loading**: If the skill documents a config format (YAML, env vars), test that the library accepts configs matching the documented schema.

## What NOT to Test

Avoid testing library internals that the skill does not document. If the skill does not mention `DLQRouter` or `MemoryPubSub`, those classes should not appear in integration tests. The tests verify the skill's accuracy, not the library's completeness.

Avoid duplicating the library's own test suite. Integration tests for a skill are narrower — they test the specific paths the skill tells users to take.

## Test Structure

Integration tests live in the skill's `tests/` directory alongside scenario tests. Name them `test_<topic>_integration.py` to distinguish them from scenario YAML files.

Use pytest as the test framework. Structure tests into classes that mirror the documented workflows:

```python
"""Integration tests for <skill-name> skill.

Tests the real user experience: config → import → use.
"""

import pytest

# Import exactly what the skill tells users to import
from library import MainClass, Helper, setup_function


@pytest.fixture
def config_file(tmp_path):
    """Write a test config matching the documented format."""
    # Use the same YAML/config structure shown in skill references
    ...


class TestCoreWorkflow:
    """Tests the primary documented workflow end-to-end."""

    async def test_basic_usage(self, config_file):
        """User follows the getting-started steps from the skill."""
        ...


class TestModelCreation:
    """Tests creating objects the skill documents."""

    def test_minimal_creation(self):
        """Minimum required fields work."""
        ...


class TestErrorCases:
    """Tests documented error conditions."""

    async def test_missing_setup_raises(self):
        """Documented error: using library without setup."""
        ...
```

Key principles for test structure:
- Import exactly what the skill tells users to import — not internal submodules
- Use config formats matching what the skill documents, not the library's test fixtures
- Test docstrings should read like user stories: "User publishes a message, subscriber receives it"
- Use in-memory or test backends to avoid external service dependencies

## Fixtures and Cleanup

External libraries often have global state (registries, factories, singletons). Reset this state between tests to prevent test coupling. A common pattern is an `autouse` fixture that clears the library's state before and after each test.

Use `tmp_path` for any config files to avoid polluting the real filesystem. If the library reads environment variables, use `monkeypatch` to set them safely.

## Running Integration Tests

Integration tests require the target library to be installed. Run them with pytest:

```
pytest tests/test_*_integration.py -v
```

If the library is not installed, the tests will fail with ImportError — this is expected and correct. The library should be listed in the skill's requirements or the project's dependencies.
