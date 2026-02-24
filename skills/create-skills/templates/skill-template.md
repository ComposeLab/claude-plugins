---
name: {{SKILL_NAME}}
description: {{SKILL_DESCRIPTION}}
version: 1.0.0
triggers:
  - "first trigger phrase"
  - "second trigger phrase"
  - "third trigger phrase"
---

<!--
  SKILL.md Template

  This file is the entry point for the skill. Claude reads it when the skill activates.
  Keep the body lean (under ~100 lines) and delegate deep knowledge to references/.

  Use imperative form for instructions ("Read the file" not "The agent should read").
  Avoid second-person pronouns in the body.
-->

# {{SKILL_NAME}}

## Workflow

<!-- Define the high-level steps Claude follows when this skill activates. -->

### Step 1: Gather Context

<!-- What information does Claude need before starting? -->

Determine the task requirements by reading the user's request.

### Step 2: Execute

<!-- What actions does Claude take? Point to references for deep knowledge. -->

Perform the main task. Consult `references/` files for detailed guidance on specific aspects.

### Step 3: Validate

<!-- How does Claude verify the result? -->

Verify the output meets expectations.

### Step 4: Present Results

<!-- How does Claude communicate the outcome? -->

Summarize what was done and highlight any items needing attention.
