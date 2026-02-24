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
Consult `references/conventional-commits.md` for parsing rules and edge cases.

Group commits by type. Within each group, sort by scope alphabetically.

### Step 3: Generate Changelog

Read `templates/changelog-template.md` for the output format.

Generate the changelog entry with:
- Version heading with date
- Grouped sections (Features, Bug Fixes, etc.)
- Each entry showing scope and description

Omit empty sections. If a commit does not match conventional format, place it under "Other Changes."

### Step 4: Validate and Present

Verify every commit from the range appears in the output.
Present the changelog and ask if adjustments are needed.

If the user approves, write the content to CHANGELOG.md (prepend to existing content if the file exists).
