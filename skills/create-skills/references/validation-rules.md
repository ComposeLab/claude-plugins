# Validation Rules Reference

This reference documents each validation check performed by `validate_skill.py`, along with the reasoning behind it.

## Structural Checks

These checks verify that the skill has the required pieces in place. Structural failures indicate a broken skill that will not function correctly.

### skill-md-exists

**Checks:** A file named `SKILL.md` exists in the skill directory root.

**Level:** FAIL if missing.

**Why:** SKILL.md is the entry point for every skill. Without it, Claude has nothing to load when the skill activates. This is the most fundamental requirement — everything else depends on this file existing.

### frontmatter-valid

**Checks:** The file begins with `---` delimiters containing valid YAML.

**Level:** FAIL if missing or unparseable.

**Why:** Frontmatter is the machine-readable metadata layer. If it cannot be parsed, the system cannot determine the skill's name, description, or triggers. Broken YAML typically means a syntax error (missing colon, bad indentation) that is easy to fix once identified.

### frontmatter-name

**Checks:** The `name` field exists in frontmatter.

**Level:** FAIL if missing.

**Why:** The name field uniquely identifies the skill in programmatic contexts. Without it, the skill cannot be referenced by other skills, listed in registries, or matched to its directory.

### frontmatter-description

**Checks:** The `description` field exists in frontmatter.

**Level:** FAIL if missing.

**Why:** Descriptions appear in listing contexts where users or Claude scan available skills. A missing description makes the skill invisible in these contexts — it exists but cannot explain what it does.

### frontmatter-version

**Checks:** The `version` field exists in frontmatter.

**Level:** FAIL if missing.

**Why:** Version tracking enables change management. When skills are shared across projects, knowing which version is deployed helps diagnose issues and manage updates.

### name-kebab-case

**Checks:** The `name` value matches the pattern `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`.

**Level:** FAIL if invalid.

**Why:** Kebab-case is the standard naming convention for skill directories and identifiers. It avoids filesystem issues (no spaces or special characters), works across operating systems, and reads naturally in URLs and command-line contexts. Enforcing this at validation time prevents inconsistencies that would break references between skills.

## Quality Heuristics

These checks flag potential quality issues. They produce WARN rather than FAIL because legitimate exceptions exist.

### name-matches-dir

**Checks:** The frontmatter `name` matches the skill directory name.

**Level:** WARN if different.

**Why:** When the name and directory diverge, it creates confusion about which identifier to use. Someone looking at the directory expects the name to match. This is a warning rather than a failure because there are rare cases (skill renaming in progress) where a temporary mismatch is acceptable.

### description-third-person

**Checks:** The description does not start with second-person pronouns ("you", "your").

**Level:** WARN if detected.

**Why:** Descriptions appear in listing contexts where third-person reads naturally ("Creates skills" vs "You create skills"). Second-person opening is the most common deviation from this convention.

### trigger-phrases

**Checks:** At least two trigger phrases exist in frontmatter.

**Level:** WARN if fewer than two.

**Why:** Trigger phrases help Claude recognize when to activate the skill. A single phrase provides limited coverage — users express intent in varied ways. Two or more phrases give Claude enough examples to generalize. This is a warning because some highly specialized skills may legitimately have narrow triggers.

### body-line-count

**Checks:** The body (below frontmatter) is under 500 lines. Additionally warns above 200 lines.

**Level:** FAIL above 500, WARN above 200.

**Why:** The body is loaded into Claude's context on every activation. Long bodies consume context window space that could be used for the actual task. The 200-line threshold is where bodies typically benefit from delegating detail to references. The 500-line hard limit prevents runaway bodies that would crowd out working context.

### no-second-person

**Checks:** The body does not contain second-person pronouns (you, your, etc.) outside of headings and code blocks.

**Level:** WARN if detected.

**Why:** Second-person creates ambiguity in skill instructions. When Claude reads "you should validate the output," "you" could refer to Claude, the end user, or the skill author. Imperative form ("Validate the output") eliminates this ambiguity. This is a warning because quoted text or example content may legitimately contain second-person.

### imperative-form

**Checks:** The body does not contain phrases like "The agent should", "Claude should", "It should".

**Level:** WARN if detected.

**Why:** Instructions that say "The agent should read the file" add indirection. "Read the file" is direct and unambiguous. Indirect phrasing can weaken instruction-following because it describes what should happen rather than commanding it.

### referenced-files

**Checks:** Files mentioned in the body (matching patterns like `references/foo.md`, `templates/bar.md`) exist on disk.

**Level:** FAIL if any referenced file is missing.

**Why:** When the body tells Claude to "Read references/validation-rules.md" and that file does not exist, the skill breaks at runtime. This check catches broken references before they cause runtime failures. Missing references are a structural failure, not a quality issue, because they prevent the skill from functioning as designed.

### no-comparison-patterns

**Checks:** No files in the skill directory contain emoji checkmarks/crossmarks or "Good:/Bad:" list patterns.

**Level:** WARN if detected.

**Why:** The project convention uses explanation-focused writing rather than good/bad comparison lists. Comparison patterns indicate a file that teaches pattern-matching rather than understanding. This is a warning because there may be edge cases where a brief comparison is the clearest way to illustrate a point.

### test-files-exist

**Checks:** At least one `test_*.yaml` or `test_*.yml` file exists in the skill's `tests/` directory.

**Level:** WARN if missing.

**Why:** Validation checks structure; tests check behavior. A skill without tests may pass validation perfectly and still produce incorrect results when Claude uses it. This is a warning rather than a failure because skills in early development may not have tests yet, and the absence of tests does not prevent the skill from functioning — it just means behavior is unverified.
