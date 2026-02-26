#!/usr/bin/env python3
"""Initialize a new skill directory with SKILL.md from template and standard subdirectories."""

import argparse
import os
import re
import sys
from pathlib import Path


def kebab_case(name: str) -> str:
    """Convert a string to kebab-case."""
    s = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return s.lower()


def main():
    parser = argparse.ArgumentParser(description="Initialize a new Claude Code skill directory.")
    parser.add_argument("name", help="Skill name (will be converted to kebab-case)")
    parser.add_argument(
        "--parent-dir",
        default=None,
        help="Parent directory for the skill (default: skills/ relative to repo root)",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to SKILL.md template (default: uses bundled template)",
    )
    args = parser.parse_args()

    skill_name = kebab_case(args.name)

    # Determine parent directory
    if args.parent_dir:
        parent = Path(args.parent_dir)
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        parent = repo_root / "skills"

    skill_dir = parent / skill_name

    if skill_dir.exists():
        print(f"FAIL: Directory already exists: {skill_dir}")
        sys.exit(1)

    # Determine template path
    if args.template:
        template_path = Path(args.template)
    else:
        template_path = Path(__file__).resolve().parent.parent / "templates" / "skill-template.md"

    if not template_path.exists():
        print(f"FAIL: Template not found: {template_path}")
        sys.exit(1)

    template_content = template_path.read_text()

    # Replace placeholders
    content = template_content.replace("{{SKILL_NAME}}", skill_name)
    content = content.replace("{{SKILL_DESCRIPTION}}", f"Provides {skill_name} functionality.")

    # Create directory structure
    subdirs = ["references", "templates", "examples", "scripts", "tests"]
    for subdir in subdirs:
        (skill_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    (skill_dir / "SKILL.md").write_text(content)

    print(f"Initialized skill: {skill_dir}")
    print(f"  Created SKILL.md from template")
    for subdir in subdirs:
        print(f"  Created {subdir}/")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_dir / 'SKILL.md'} — fill in description, triggers, and instructions")
    print(f"  2. Add reference docs to {skill_dir / 'references/'}")
    print(f"  3. Validate with: python validate_skill.py {skill_dir}")


if __name__ == "__main__":
    main()
