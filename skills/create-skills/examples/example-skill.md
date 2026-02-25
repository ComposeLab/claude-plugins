---
# The name matches the directory this file would live in.
# Kebab-case is required: lowercase, hyphens between words, no spaces or underscores.
name: format-changelog
# Third-person description: "Generates..." not "Generate..." or "You can generate..."
# This reads naturally in listing contexts: "What does it do? It generates changelogs."
description: Generates formatted changelogs from git commit history with conventional commit parsing.
version: 1.0.0
# Triggers cover the main use case and natural variations.
# Three phrases give Claude enough examples to generalize to similar requests.
triggers:
  - "generate a changelog"
  - "format my commits into a changelog"
  - "create release notes"
tags:
  - git
  - documentation
---

# format-changelog

<!--
  Notice how this body is short. It defines WHAT to do in each step,
  then points to references for HOW to do it well. This keeps the
  initial context lean.
-->

## Workflow

### Step 1: Determine Scope

<!-- Imperative form: "Ask..." not "The agent should ask..." -->

Ask the user for the version range. If not specified, default to commits since the last tag.
Read the git log for the determined range.

### Step 2: Parse Commits

Classify each commit using conventional commit format (feat, fix, chore, etc.).
<!-- Use markdown links for file references: [Title](path) not backtick `path`. -->
Consult [Conventional Commits](references/conventional-commits.md) for parsing rules and edge cases.

Group commits by type. Within each group, sort by scope alphabetically.

### Step 3: Generate Changelog

Read [Changelog Template](templates/changelog-template.md) for the output format.

Generate the changelog entry with:
- Version heading with date
- Grouped sections (Features, Bug Fixes, etc.)
- Each entry showing scope and description

Omit empty sections. If a commit does not match conventional format, place it under "Other Changes."

### Step 4: Validate and Present

Verify every commit from the range appears in the output.
Present the changelog and ask if adjustments are needed.

If the user approves, write the content to CHANGELOG.md (prepend to existing content if the file exists).

<!--
  Test scenarios live in tests/test_scenarios.yaml. Here is what a test suite
  for this skill would look like. Each test targets one workflow or capability.

  This skill is a workflow skill — it orchestrates git commands and text formatting
  but does not document an external library's API. Therefore, scenario tests are
  sufficient. If this skill documented a library (e.g., a git parsing library with
  importable classes), it would also need integration tests in tests/test_*_integration.py
  that verify the documented imports, method signatures, and config formats work.
  See references/integration-testing-guide.md for when integration tests are needed.
-->

## Example Test Suite

```yaml
suite: format-changelog-scenarios
skill_path: ..

config:
  model: haiku
  max_turns: 5
  max_budget_usd: 0.50

tests:
  - name: skill guides determining commit scope
    prompt: "I want to generate a changelog but I'm not sure what range of commits to include. How do I decide?"
    expected:
      - "Mentions using the version range or commits since the last tag"
      - "Explains how to determine the scope of commits to include"

  - name: skill parses conventional commits
    prompt: "How does the skill classify commits? What format does it expect?"
    expected:
      - "Mentions conventional commit format (feat, fix, chore, etc.)"
      - "References grouping commits by type"
      - "Mentions handling commits that don't match conventional format"

  - name: skill generates formatted output
    prompt: "Generate a changelog for my project. Walk me through what the output looks like."
    expected:
      - "Describes version heading with date"
      - "Mentions grouped sections like Features and Bug Fixes"
      - "Mentions omitting empty sections"
```
