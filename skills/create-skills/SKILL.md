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
python skills/create-skills/scripts/init_skill.py <skill-name>
```

### Step 3: Write the Skill

Read [Skill Writing Guide](references/skill-writing-guide.md) for writing principles and conventions.
Read [Frontmatter Spec](references/frontmatter-spec.md) for all available frontmatter fields.

Fill in the generated SKILL.md:
- Set frontmatter fields (name, description in third-person, version, triggers)
- Write a lean body with imperative instructions
- Delegate deep knowledge to files in `references/`

Read [Example Skill](examples/example-skill.md) to see these principles applied to a concrete skill.

### Step 4: Verify References

When a skill documents an external library, verify reference accuracy against the actual source code before validating. Check that:
- Import paths work (e.g., `from mq import Bus` is a real export)
- Method signatures match the library's actual API
- Config fields and options exist in the library's config models

Read the library's source, its `__init__.py` exports, and its own examples or tests. If a reference claims something is importable, confirm it. This step prevents skills from documenting APIs that do not exist.

### Step 5: Validate

Run the validation script against the skill directory:

```
python skills/create-skills/scripts/validate_skill.py <path-to-skill-dir>
```

Read [Validation Rules](references/validation-rules.md) to understand each check and its rationale.

Address any FAIL results immediately. Review WARN results and fix those that apply.

### Step 6: Iterate

Present the validation report to the user. If issues remain, return to Step 3 with targeted fixes. Once validation passes cleanly, proceed to testing.

### Step 7: Scenario Test

Create a `tests/test_scenarios.yaml` with test cases covering the skill's key behaviors. Read [Test Writing Guide](references/test-writing-guide.md) for the YAML format, config options, and guidance on writing effective prompts and criteria.

Run the test suite:

```
python skills/create-skills/scripts/test_skill.py <path-to-skill-dir>
```

Review the results. If tests fail, examine the generation output and evaluation reasoning, then iterate on the skill instructions or test criteria.

### Step 8: Integration Test

If the skill documents an external library with importable APIs, write integration tests that exercise the real library. Read [Integration Testing Guide](references/integration-testing-guide.md) for when integration tests are needed and how to structure them.

Scenario tests verify that the skill guides correctly. Integration tests verify that the documented APIs actually work. Both are needed for skills that reference external code — scenario tests alone can pass even when import paths are wrong.

Once both test types pass, summarize what was created.

## Workflow: Validate an Existing Skill

### Step 1: Locate

Identify the skill directory path from the user's request.

### Step 2: Run Validation

```
python skills/create-skills/scripts/validate_skill.py <path-to-skill-dir>
```

### Step 3: Report

Present the structured PASS/WARN/FAIL report. For each warning or failure, explain the reasoning (consult [Validation Rules](references/validation-rules.md)) and suggest a specific fix.

## Workflow: Improve a Skill

### Step 1: Validate First

Run validation on the existing skill to establish a baseline.

### Step 2: Identify Improvements

Compare the skill against the principles in [Skill Writing Guide](references/skill-writing-guide.md). Look for:
- Body content that should be delegated to references
- Missing trigger phrases
- Frontmatter gaps
- Style deviations

### Step 3: Apply and Re-validate

Make targeted improvements. Run validation again to confirm fixes and catch regressions.
