---
name: create-skills
description: Creates and validates Claude Code skill directories with proper structure and conventions.
version: 1.0.0
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

# create-skills

A lean coordinator for creating, validating, and improving Claude Code skills. Deep knowledge lives in reference files — this body defines the workflow.

## Workflow: Create a New Skill

### Step 1: Capture Intent

Determine the skill name, purpose, and key triggers from the user's request. Confirm understanding before proceeding.

### Step 2: Initialize

Run `scripts/init_skill.py` with the skill name to scaffold the directory structure and generate a starter SKILL.md from the template.

```
python scripts/init_skill.py <skill-name>
```

### Step 3: Write the Skill

Read `references/skill-writing-guide.md` for writing principles and conventions.
Read `references/frontmatter-spec.md` for all available frontmatter fields.

Fill in the generated SKILL.md:
- Set frontmatter fields (name, description in third-person, version, triggers)
- Write a lean body with imperative instructions
- Delegate deep knowledge to files in `references/`

Read `examples/example-skill.md` to see these principles applied to a concrete skill.

### Step 4: Validate

Run the validation script against the skill directory:

```
python scripts/validate_skill.py <path-to-skill-dir>
```

Read `references/validation-rules.md` to understand each check and its rationale.

Address any FAIL results immediately. Review WARN results and fix those that apply.

### Step 5: Iterate

Present the validation report to the user. If issues remain, return to Step 3 with targeted fixes. Once validation passes cleanly, summarize what was created.

## Workflow: Validate an Existing Skill

### Step 1: Locate

Identify the skill directory path from the user's request.

### Step 2: Run Validation

```
python scripts/validate_skill.py <path-to-skill-dir>
```

### Step 3: Report

Present the structured PASS/WARN/FAIL report. For each warning or failure, explain the reasoning (consult `references/validation-rules.md`) and suggest a specific fix.

## Workflow: Improve a Skill

### Step 1: Validate First

Run validation on the existing skill to establish a baseline.

### Step 2: Identify Improvements

Compare the skill against the principles in `references/skill-writing-guide.md`. Look for:
- Body content that should be delegated to references
- Missing trigger phrases
- Frontmatter gaps
- Style deviations

### Step 3: Apply and Re-validate

Make targeted improvements. Run validation again to confirm fixes and catch regressions.
