# claude-plugins

A repository of reusable skills and agents for Claude Code. Each skill lives under `skills/<skill-name>/` and follows a consistent structure defined by the create-skills skill.

## Project Conventions

### Writing Style

All skill documentation uses an explanation-focused style. Instead of listing good and bad examples side by side, each concept gets a paragraph explaining WHY the convention exists. Readers learn the reasoning and can apply judgment to edge cases, rather than pattern-matching against examples.

### Skill Structure

Every skill directory contains a `SKILL.md` at its root. This file uses YAML frontmatter for metadata and a markdown body for instructions. The body stays lean (under ~100 lines) by delegating deep knowledge to files in `references/`, `templates/`, and `examples/`. This separation keeps the main skill file scannable while allowing thorough coverage in supporting material.

### Description Convention

Skill descriptions use third-person perspective ("Creates a new skill" not "Create a new skill" or "You can create a skill"). This convention exists because descriptions appear in listing contexts where imperative or second-person forms read awkwardly.

### Instruction Convention

Instructions within SKILL.md bodies use imperative form ("Read the template" not "The agent should read the template"). Imperative form is direct, unambiguous, and mirrors how effective prompts are written for language models.

### Validation

Every skill should be validatable by `scripts/validate_skill.py` within its own directory or via the create-skills skill's validator. Validation catches structural issues early and enforces conventions automatically.

## Lessons Learned

<!-- This section grows over time. After completing a skill or encountering a notable issue, add an entry here explaining what happened and what was learned. Format: ### Title, then a short paragraph. -->

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Explanation-focused writing over good/bad lists | Readers internalize WHY behind conventions, enabling better judgment on edge cases |
| 2026-02-24 | Lean SKILL.md with reference delegation | Keeps the primary instruction file scannable; deep knowledge lives in dedicated references |
| 2026-02-24 | Python validation scripts per skill | Automated checks enforce conventions without relying on manual review |
