# Skill Writing Guide

This reference explains the principles behind well-structured Claude Code skills. Each section covers a concept and the reasoning behind it, so authors can apply judgment rather than memorizing rules.

## What a Skill Is

A skill is a set of instructions that Claude Code loads when a user invokes it. The SKILL.md file is the entry point — Claude reads it and follows its instructions. Everything in SKILL.md is a prompt, which means clarity and structure directly affect how well Claude performs the task.

Skills differ from general documentation because their audience is a language model, not a human reader browsing docs. This distinction drives most of the conventions below.

## The Lean Body Principle

A SKILL.md body should stay under roughly 100 lines of instruction content. This constraint exists because Claude processes the entire body as context when the skill activates. Shorter bodies mean less noise, faster comprehension, and more room in the context window for the actual task.

When a skill needs deep knowledge — style guides, validation rules, API specs — that material belongs in `references/` files. The body then points Claude to the right reference at the right moment. This "just-in-time" loading pattern keeps the initial prompt focused while making deep knowledge available on demand.

The body acts as a coordinator: it defines the workflow steps and delegates specialized knowledge to supporting files. Think of it as a table of contents that Claude follows, pulling in detail as needed.

## Progressive Disclosure

Progressive disclosure means revealing information in the order it becomes relevant. In a skill, this means the body introduces the high-level workflow first, then each step points to references or templates when deeper detail is needed.

This matters because Claude processes instructions sequentially. Front-loading all the detail creates a wall of context where important workflow steps get buried among edge cases. By structuring the body as a sequence of actions — each with a pointer to deeper material — Claude can maintain focus on what to do next while having access to how to do it well.

For example, a skill that creates files might structure its body as:
1. Gather requirements from the user
2. Read the template (pointing to `templates/`)
3. Generate the file (pointing to `references/` for style guidelines)
4. Validate the result (pointing to `references/` for validation rules)

Each step is a short instruction. The depth lives elsewhere.

## Third-Person Descriptions

The `description` field in frontmatter uses third-person form: "Creates a new skill directory" rather than "Create a new skill directory" or "You can create a new skill directory."

This convention exists because descriptions appear in listing and discovery contexts — places where Claude or a user scans multiple skills to find the right one. In these contexts, third-person reads naturally as a label ("What does this skill do? It creates a new skill directory.") while imperative form reads as a command and second-person reads as conversation.

Third-person also maintains consistency with how tools and functions are typically described in programming contexts (docstrings, API docs, package descriptions).

## Imperative Instructions

Within the SKILL.md body, instructions use imperative form: "Read the template file" rather than "The agent should read the template file" or "You should read the template file."

Imperative form works best for skill instructions because it mirrors how effective prompts are written. When Claude encounters "Read the template file," the instruction is unambiguous — there is one action to take. Indirect forms like "The agent should read" add a layer of abstraction that can dilute instruction following.

Second-person ("you should") is avoided in the body for a different reason: it creates ambiguity about who "you" refers to when the skill is loaded alongside other context. Imperative form has no such ambiguity.

## Trigger Phrases

The `triggers` field in frontmatter lists natural-language phrases that indicate when this skill should activate. These phrases serve as examples for Claude to recognize user intent, not as exact-match keywords.

Effective trigger phrases:
- Cover the main use case ("create a skill")
- Include variations that a user might naturally say ("build a plugin skill", "make a new skill")
- Include adjacent tasks the skill handles ("validate my skill", "improve a skill")

Three to five trigger phrases typically provide enough coverage. Fewer than two leaves the skill hard to discover; more than seven adds noise without improving recognition.

## Frontmatter as Metadata

YAML frontmatter at the top of SKILL.md serves as machine-readable metadata. It tells the system what the skill is called, what it does, when to invoke it, and what version it is — without Claude having to parse these facts from natural language.

Separating metadata from instructions keeps each concern clean. The frontmatter answers "what is this?" while the body answers "what should Claude do?" Mixing the two makes both harder to maintain and parse.

## Reference Files

Reference files in `references/` contain deep, focused knowledge on a single topic. Each file should be self-contained enough that Claude can read it independently and gain useful understanding.

The reason for separate reference files rather than one large document is context efficiency. When a skill step says "Read references/validation-rules.md," Claude loads only the validation knowledge it needs at that moment. If all references were inlined in the body, every activation would load all knowledge regardless of relevance.

Naming conventions for reference files use descriptive kebab-case names that indicate their content: `skill-writing-guide.md`, `frontmatter-spec.md`, `validation-rules.md`. This makes it easy for both Claude and human authors to find the right file.

When the SKILL.md body points Claude to a reference, template, or example file, use markdown link syntax — `[Descriptive Title](references/file-name.md)` — rather than backtick code spans like `` `references/file-name.md` ``. Markdown links are semantically richer: the link text conveys what the file contains, while the path tells Claude where to find it. This matters because Claude uses the link text as a signal for what knowledge it is about to load, improving context comprehension. Backtick paths only communicate location, forcing Claude to infer purpose from the filename alone.

## Templates

Templates in `templates/` provide starter content with placeholders. They reduce the cognitive load of creating a new file from scratch and ensure consistent structure across skills.

A good template includes:
- All required structural elements (frontmatter, section headers)
- Placeholder values that clearly indicate what to replace (`{{SKILL_NAME}}`)
- Brief inline comments explaining what each section is for

Templates should be minimal. They provide structure, not content. An author filling in a template should focus on their specific skill's logic, not on removing boilerplate they don't need.

## Examples

Example files in `examples/` show a completed skill with annotations. They bridge the gap between abstract guidelines and concrete implementation.

Examples work best when they are realistic (not toy examples), annotated (comments explain why choices were made), and complete (all sections filled in). A single well-annotated example is more valuable than multiple shallow ones.

## Validation

Validation scripts in `scripts/` automate quality checks. They exist because manual review is inconsistent and slow, especially for structural concerns like "is the frontmatter valid YAML?" or "does every referenced file exist?"

Validation checks fall into two categories:
- **Structural**: deterministic checks like file existence, YAML parsing, kebab-case naming. These are PASS/FAIL.
- **Heuristic**: quality signals like third-person description, imperative form, line count. These are typically WARN because they have legitimate exceptions.

The distinction matters because structural failures indicate broken skills that will not work correctly, while heuristic warnings indicate style deviations that may or may not need fixing.

## Writing Style: Explain the Why

Throughout all skill documentation — references, guides, and annotations — the preferred style explains WHY a convention exists rather than listing good and bad examples.

Comparison lists (good example / bad example, with check marks and X marks) are visually scannable but shallow. They teach pattern-matching: "do it like this, not like that." When an author encounters a case not covered by the examples, they have no framework for making a decision.

Explanation-focused writing teaches the underlying principle. When an author understands that third-person descriptions exist because they read naturally in listing contexts, they can apply that reasoning to edge cases the examples never covered.

This style requires more writing effort upfront but produces documentation that ages better and handles novel situations gracefully.

## Putting It All Together

A well-structured skill has:
- Clean frontmatter with name, description, version, and triggers
- A lean body that coordinates a workflow in imperative steps
- References that contain deep knowledge, loaded on demand
- Templates that provide starting structure with placeholders
- Examples that show the concepts applied in practice
- Validation that catches structural and quality issues automatically

Each piece serves a distinct purpose. The body is the conductor; references are the musicians; templates are the sheet music; examples are recordings of performances; validation is the tuner making sure everything is in key.
