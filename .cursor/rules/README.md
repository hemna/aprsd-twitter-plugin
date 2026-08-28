# APRSD Cursor Rules

This directory contains Cursor AI rules that enforce consistent coding patterns across all APRSD plugins and extensions.

## Available Rules

| Rule File | Description | Scope |
|-----------|-------------|-------|
| `aprsd-project-structure.mdc` | Standard project structure and organization | Always applies |
| `aprsd-plugin-patterns.mdc` | Plugin development patterns and best practices | Applies to `*_plugin.py` files |
| `aprsd-extension-patterns.mdc` | Extension development patterns | Applies to `*extension.py` files |
| `aprsd-config-patterns.mdc` | Oslo.config configuration patterns | Applies to `conf/*.py` files |
| `aprsd-pyproject-standards.mdc` | pyproject.toml standards and conventions | Applies to `pyproject.toml` files |
| `aprsd-cli-patterns.mdc` | CLI command patterns | Applies to `cli.py` files |
| `aprsd-testing-standards.mdc` | Testing standards and best practices | Applies to `test_*.py` files |

## How These Rules Work

- **Always Apply Rules**: `aprsd-project-structure.mdc` applies to every Cursor session in this project
- **File-Specific Rules**: Other rules activate when you're working with matching files (e.g., plugin rules when editing a `*_plugin.py` file)

## Deploying to Plugin/Extension Projects

To apply these rules across all your APRSD plugin and extension projects, copy this entire `.cursor/rules/` directory to each project:

```bash
# From the aprsd directory
for dir in ../aprsd-plugins/*/; do
    mkdir -p "$dir/.cursor"
    cp -r .cursor/rules "$dir/.cursor/"
done
```

Or copy manually to specific projects:

```bash
cp -r /path/to/aprsd/.cursor/rules /path/to/aprsd-joke-plugin/.cursor/
cp -r /path/to/aprsd/.cursor/rules /path/to/aprsd-admin-extension/.cursor/
# etc.
```

## Customizing Rules

If a specific plugin/extension needs custom rules:

1. Copy these base rules to the project
2. Add project-specific rules as additional `.mdc` files
3. Modify existing rules if needed (but try to keep consistency)

## Rule Syntax

Each rule file uses this format:

```markdown
---
description: Brief description of the rule
globs: **/*.py  # File pattern (optional)
alwaysApply: false  # Set to true for universal rules
---

# Rule Title

Rule content in markdown...
```

## Benefits

These rules help:

- Maintain consistent code patterns across all APRSD projects
- Provide context-aware guidance when developing plugins/extensions
- Enforce best practices automatically
- Reduce code review feedback on structural issues
- Onboard new contributors faster

## Updating Rules

When updating these rules:

1. Update in the main APRSD repository first
2. Test the changes
3. Deploy to plugin/extension projects
4. Communicate changes to the team

## See Also

- [Cursor Rules Documentation](https://docs.cursor.com/context/rules-for-ai)
- Main APRSD workspace rules in `/Users/I530566/devel/mine/hamradio/aprsd/.cursor/rules/`
