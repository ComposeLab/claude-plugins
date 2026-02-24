# SKILL.md Frontmatter Specification

This reference defines the YAML frontmatter fields available in SKILL.md files. Frontmatter appears between `---` delimiters at the top of the file.

## Required Fields

### `name`

The skill's identifier. Must be kebab-case (lowercase letters, digits, and hyphens). The name should match the skill's directory name. This field is used for programmatic lookups, so consistency and simplicity matter.

**Type:** string
**Example:** `create-skills`

### `description`

A one-line summary of what the skill does. Uses third-person form ("Creates..." not "Create..." or "You can create...") because descriptions appear in listing contexts where third-person reads naturally.

**Type:** string
**Example:** `Creates and validates Claude Code skill directories with proper structure and conventions.`

### `version`

Semantic version of the skill. Follows semver (MAJOR.MINOR.PATCH). Incrementing version helps track changes when skills are shared across projects.

**Type:** string
**Example:** `1.0.0`

## Optional Fields

### `triggers`

A list of natural-language phrases indicating when this skill should activate. Claude uses these as intent-recognition examples, not exact-match keywords. Three to five phrases typically provide good coverage.

**Type:** list of strings
**Example:**
```yaml
triggers:
  - "create a skill"
  - "build a plugin skill"
  - "validate my skill"
```

### `author`

The person or team who created the skill. Useful for attribution in shared repositories.

**Type:** string
**Example:** `composeLab`

### `tags`

Categorical labels for organizing and filtering skills. Tags help in repositories with many skills.

**Type:** list of strings
**Example:**
```yaml
tags:
  - tooling
  - meta
```

### `requires`

A list of dependencies this skill expects to be available. These might be other skills, tools, or runtime requirements.

**Type:** list of strings
**Example:**
```yaml
requires:
  - python3
```

### `invocation`

Controls how the skill is invoked. Subfields:

- `user_invocable` (boolean): Whether users can invoke this skill directly via `/skill-name`. Defaults to `true`.
- `auto_invoke` (boolean): Whether Claude can automatically invoke this skill when it detects matching intent. Defaults to `false`.

**Type:** object
**Example:**
```yaml
invocation:
  user_invocable: true
  auto_invoke: false
```

## Dynamic Variables

Certain placeholder values in SKILL.md can be resolved at runtime. These are enclosed in double curly braces and replaced when the skill loads.

| Variable | Resolves To |
|----------|-------------|
| `{{SKILL_NAME}}` | The skill's name from frontmatter |
| `{{SKILL_DIR}}` | Absolute path to the skill's directory |
| `{{REPO_ROOT}}` | Absolute path to the repository root |
| `{{DATE}}` | Current date in ISO format (YYYY-MM-DD) |

Dynamic variables are most useful in templates and scripts where paths need to be resolved relative to the current environment.

## Complete Example

```yaml
---
name: create-skills
description: Creates and validates Claude Code skill directories with proper structure and conventions.
version: 1.0.0
author: composeLab
triggers:
  - "create a skill"
  - "build a plugin skill"
  - "validate my skill"
  - "improve a skill"
tags:
  - tooling
  - meta
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: false
---
```
