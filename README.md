# claude-plugins

A repository of reusable plugins and skills for Claude Code.

## Repository Structure

```
claude-plugins/
├── plugins/                    # Installable Claude Code plugins
│   └── core-usage/             # Skills for internal core libraries
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── core-db/
├── skills/                     # Repo-level skills (not distributed as plugins)
│   └── create-skills/          # Skill for creating and validating other skills
└── CLAUDE.md                   # Project conventions and decision log
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| `core-usage` | Skills for working with internal core libraries (core-db, etc.) |

## Installing a Plugin

Use the `--plugin-dir` flag to load a plugin from this repo:

```bash
claude --plugin-dir /path/to/claude-plugins/plugins/core-usage
```

Multiple plugins can be loaded at once:

```bash
claude --plugin-dir ./plugins/core-usage --plugin-dir ./plugins/another-plugin
```

Once loaded, plugin skills are namespaced by plugin name. For example, the `core-db` skill in the `core-usage` plugin is invoked as `/core-usage:core-db`.

## Creating a New Skill

Use the `create-skills` skill to scaffold, write, and validate new skills:

```
/create-skills
```

This walks through capturing intent, generating the directory structure, writing the SKILL.md, and running validation.
