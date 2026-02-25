# claude-plugins

A local marketplace of reusable plugins and skills for Claude Code.

## Repository Structure

```
claude-plugins/
├── .claude-plugin/
│   ├── plugin.json             # Repo-level plugin manifest
│   └── marketplace.json        # Marketplace definition
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

## Installation

### 1. Add the marketplace

From a local clone:

```bash
/plugin marketplace add /path/to/claude-plugins
```

From GitHub:

```bash
/plugin marketplace add ComposeLab/claude-plugins
```

### 2. Install a plugin

```bash
/plugin install core-usage@compose-lab
```

Choose a scope when prompted:

- **User** — available in all your projects (`~/.claude/settings.json`)
- **Project** — shared with the team via version control (`.claude/settings.json`)
- **Local** — just for you, gitignored (`.claude/settings.local.json`)

### 3. Use it

Plugin skills are namespaced by plugin name:

```
/core-usage:core-db
```

## Updating Plugins

After the repo is updated (new skills, bug fixes, version bumps), run:

```bash
/plugin marketplace update compose-lab
```

To enable automatic updates so plugins stay current on each Claude Code startup, open `/plugin`, go to the **Marketplaces** tab, select `compose-lab`, and enable auto-update.

**Important:** Plugin versions must be bumped in `plugin.json` for updates to be detected.

## Development

### Quick-loading a plugin (no marketplace)

For development and testing, load a plugin directly without installing:

```bash
claude --plugin-dir ./plugins/core-usage
```

### Creating a new skill

Use the `create-skills` skill to scaffold, write, and validate new skills:

```
/create-skills
```

### Adding a new plugin to the marketplace

1. Create the plugin under `plugins/<plugin-name>/` with a `.claude-plugin/plugin.json`
2. Add an entry to `.claude-plugin/marketplace.json`
3. Bump the marketplace `metadata.version`
4. Commit and push
