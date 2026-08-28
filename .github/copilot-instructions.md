# APRSD GitHub Copilot Instructions

This file provides coding standards and patterns for all APRSD plugins, extensions, and the main APRSD project.

## General Coding Principles

- Always prefer simple solutions over complex ones
- Avoid code duplication - check for existing similar functionality before adding new code
- Keep the codebase very clean and organized
- Avoid having files over 200-300 lines of code - refactor at that point
- Only make changes that are required or well understood and related to the change being requested
- When fixing bugs, don't introduce new patterns without exhausting existing implementation options first
- Mocking data is only needed for tests, never mock data for dev or prod environments
- Never add stubbing or fake data patterns to code that affects dev or prod environments
- Never overwrite `.env` files without first asking and confirming
- Always use the virtual environment provided in the project called `.venv`
- Focus on areas of code relevant to the task - don't touch unrelated code
- Write thorough tests for all major functionality

---

## Project Structure Standards

All APRSD plugins and extensions must follow this structure:

```
project-name/
├── module_name/              # Use underscores, not hyphens
│   ├── __init__.py
│   ├── conf/
│   │   ├── __init__.py
│   │   ├── opts.py          # Standard oslo.config pattern
│   │   └── main.py
│   ├── cli.py               # For config export command
│   └── [plugin/extension files]
├── tests/                    # Top-level tests folder
│   ├── __init__.py
│   └── test_*.py
├── docs/
├── pyproject.toml
├── setup.py
├── tox.ini
├── .pre-commit-config.yaml
├── Makefile
└── README.md or README.rst
```

**Key Requirements:**
- Module names use underscores (e.g., `aprsd_joke_plugin`, not `aprsd-joke-plugin`)
- All configuration goes in `conf/` subdirectory within the module
- Tests in top-level `tests/` folder, not nested in module
- Use `.venv` for virtual environment
- All plugins/extensions have a `cli.py` for config export
- Include both `pyproject.toml` and `setup.py` for maximum compatibility

---

## Plugin Development Patterns

### Plugin Base Class

All plugins must inherit from `plugin.APRSDRegexCommandPluginBase`:

```python
from aprsd import plugin, packets
from aprsd.utils import trace
import logging

LOG = logging.getLogger("APRSD")

class MyPlugin(plugin.APRSDRegexCommandPluginBase):
    """Plugin description.

    Explain what the plugin does, what commands it responds to,
    and any special configuration needed.
    """

    version = module_name.__version__
    command_regex = "^[cC]"      # Regex to match command
    command_name = "mycommand"   # One-word command name
    enabled = False
```

### Required Plugin Methods

#### setup()
Initialize plugin and set `self.enabled` flag:

```python
def setup(self):
    """Allows the plugin to do some 'setup' type checks.

    If the setup checks fail, set self.enabled = False. This
    will prevent the plugin from being called when packets are received.
    """
    self.enabled = CONF.my_plugin.enabled
    # Additional setup checks here
```

#### process()
Must use `@trace.trace` decorator and accept `Packet`:

```python
@trace.trace
def process(self, packet: packets.core.Packet):
    """Process matching packet.

    This is called when a received packet matches self.command_regex.
    Only called when self.enabled = True.
    """
    if not self.enabled:
        LOG.info("Plugin is not enabled")
        return

    message = packet.message_text

    # Your logic here

    return "response message"
```

#### help()
Return list of help strings:

```python
def help(self):
    """Return help message for the plugin."""
    return [
        f"{self.command_name}: Description of what command does",
        "Usage: command [options]",
        "Additional help lines if needed"
    ]
```

#### create_threads()
Return list of APRSDThread objects (or empty list):

```python
def create_threads(self):
    """Create and return custom APRSDThread objects.

    Create a child of aprsd.threads.APRSDThread object and return it.
    It will automatically get started.
    """
    if self.enabled:
        # return [MyAPRSDThread()]
        return []
```

### Plugin Best Practices

**Message Formatting:**
- Wrap long messages using `textwrap.wrap(text, 67, break_long_words=False)`
- APRS messages have a 67 character limit per line
- Return strings or lists of strings from `process()`

**Error Handling:**
- Always wrap external API calls in try/except blocks
- Log errors with `LOG.error()`
- Return user-friendly error messages
- Don't let exceptions bubble up from `process()`

```python
try:
    result = external_api_call()
except Exception as e:
    LOG.error(f"Error calling API: {e}")
    return "Error: Unable to fetch data"
```

**Logging:**
- Use `LOG = logging.getLogger("APRSD")` at module level
- Use appropriate log levels: DEBUG, INFO, WARNING, ERROR
- Include context in log messages

---

## Extension Development Patterns

### Extension Base Class

Extensions provide additional functionality beyond message processing:

```python
from aprsd import plugin

class MyExtension(plugin.APRSDExtensionBase):
    """Extension description.

    Extensions can add web interfaces, commands, background services, etc.
    """

    version = module_name.__version__
```

### Extension Types

**Web Extensions** (like aprsd-admin-extension, aprsd-webchat-extension):
```python
def setup(self):
    """Setup the extension."""
    self.enabled = CONF.my_extension.enabled

def create_threads(self):
    """Create web server or other background threads."""
    if self.enabled:
        return [MyWebServerThread()]
    return []
```

**CLI Extensions** (like aprsd-trip-extension):
- Add commands in `cmds/` directory
- Register entry points in pyproject.toml
- Follow Click or argparse patterns consistently

**Background Service Extensions:**
- All threads must inherit from `APRSDThread` base class
- Implement proper thread lifecycle methods
- Handle graceful shutdown

---

## Configuration Patterns (Oslo.config)

### conf/opts.py Structure

Must include Apache license header and follow this standard pattern:

```python
# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import collections
import importlib
import importlib.util
import os
import pkgutil

LIST_OPTS_FUNC_NAME = "list_opts"

def list_opts():
    """Collect all configuration options from conf modules."""
    opts = collections.defaultdict(list)
    module_names = _list_module_names()
    imported_modules = _import_modules(module_names)
    _append_config_options(imported_modules, opts)
    return _tupleize(opts)

def export_config(format="dict"):
    """Export configuration options as dict or JSON.

    Returns configuration metadata including type, default, help text, etc.
    """
    # Standard export implementation
    # See existing plugins for complete implementation
```

### conf/main.py Pattern

Define plugin/extension-specific config options:

```python
from oslo_config import cfg

# Define configuration group
plugin_group = cfg.OptGroup(
    name="my_plugin",
    title="My Plugin Settings",
)

# Define configuration options
plugin_opts = [
    cfg.BoolOpt(
        "enabled",
        default=False,
        help="Enable the plugin",
    ),
    cfg.StrOpt(
        "api_key",
        default=None,
        help="API key for external service",
        secret=True,
    ),
    cfg.IntOpt(
        "timeout",
        default=30,
        help="Timeout in seconds for API calls",
        min=1,
        max=300,
    ),
]

def register_opts(config):
    """Register configuration options."""
    config.register_group(plugin_group)
    config.register_opts(plugin_opts, group=plugin_group)

def list_opts():
    """Return configuration options."""
    return {plugin_group.name: plugin_opts}
```

### Configuration Best Practices

- Always include an `enabled` boolean option
- Mark sensitive options with `secret=True`
- Provide reasonable defaults
- Include helpful documentation in help strings
- Use appropriate option types (StrOpt, BoolOpt, IntOpt, ListOpt, etc.)
- Set min/max bounds for numeric values
- Use choices for enum-like options

### Accessing Configuration

```python
from oslo_config import cfg

CONF = cfg.CONF

# Access config values
if CONF.my_plugin.enabled:
    api_key = CONF.my_plugin.api_key
```

---

## pyproject.toml Standards

### Required Entry Points

```toml
[project.entry-points."oslo.config.opts"]
    "module_name.conf" = "module_name.conf.opts:list_opts"

[project.scripts]
    "module-name-export-config" = "module_name.cli:main"
```

For plugins with README support:
```toml
[project.entry-points."aprsd.plugin.readme"]
    "module_name" = "module_name:get_readme"
```

### Standard Dependencies

```toml
dependencies = [
    "aprsd>=4.2.0",      # Pin minimum APRSD version
    "oslo-config",       # or "oslo_config" - for configuration management
]
```

### Project Metadata

**Author Information:**
```toml
authors = [
    {name = "Walter A. Boring IV", email = "waboring@hemna.com"},
]
maintainers = [
    {name = "Walter A. Boring IV", email = "waboring@hemna.com"},
]
```

**Keywords:**
```toml
keywords = [
    "aprs",
    "aprs-is",
    "aprsd",
    "ham-radio",
    # Add project-specific keywords
]
```

**Classifiers:**
```toml
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Topic :: Communications :: Ham Radio",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
```

**Python Version:**
```toml
requires-python = ">=3.10"
```

### Tool Configurations

```toml
[tool.setuptools_scm]

[tool.isort]
force_sort_within_sections = true
line_length = 88
skip_gitignore = true

[tool.coverage.run]
branch = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
norecursedirs = [".tox", ".git", "build", "dist", "*.egg-info", ".venv"]
```

---

## CLI Command Patterns

### Config Export Command (cli.py)

All plugins/extensions must provide a config export CLI command:

```python
#!/usr/bin/env python3
"""CLI tool for module-name configuration export."""

import json
import sys

def export_config_cmd(format="json"):
    """Export plugin configuration options."""
    try:
        from module_name.conf.opts import export_config

        result = export_config(format=format)

        if format == "json":
            print(result)
        else:
            print(json.dumps(result, indent=2))

        return 0
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTo export config, install oslo.config:", file=sys.stderr)
        print("  pip install oslo.config", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error exporting config: {e}", file=sys.stderr)
        return 1

def main():
    """Main entry point for CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Export module-name configuration options"
    )
    parser.add_argument(
        "--format",
        choices=["dict", "json"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()
    sys.exit(export_config_cmd(format=args.format))

if __name__ == "__main__":
    main()
```

### CLI Best Practices

- Use argparse for command-line parsing
- Provide clear help messages
- Return appropriate exit codes (0 for success, non-zero for errors)
- Write errors to stderr using `file=sys.stderr`
- Handle ImportError gracefully with helpful messages
- Include shebang `#!/usr/bin/env python3` at the top

### Command Naming Convention

- Use hyphenated names (e.g., `aprsd-joke-plugin-export-config`)
- Start with the module name
- End with the action (e.g., `export-config`)
- Keep names descriptive but concise

---

## Testing Standards

### Test Organization

- Place all tests in top-level `tests/` folder, not nested in module
- Name test files `test_*.py`
- Use pytest as the test framework
- Create `tests/__init__.py` to make tests a package

### Test Structure

```python
import pytest
from aprsd import packets
from unittest import mock

from module_name import MyPlugin

class TestMyPlugin:
    """Test cases for MyPlugin."""

    def setup_method(self):
        """Setup test fixtures."""
        self.plugin = MyPlugin()

    def test_plugin_setup(self):
        """Test plugin setup."""
        self.plugin.setup()
        # Assertions here

    def test_plugin_process_success(self):
        """Test successful message processing."""
        packet = packets.core.Packet(
            from_call="TEST",
            to_call="DEST",
            message_text="test command",
        )
        result = self.plugin.process(packet)
        assert result is not None

    @mock.patch("module_name.plugin.requests.get")
    def test_external_api_call(self, mock_get):
        """Test external API calls are mocked."""
        mock_get.return_value.json.return_value = {"data": "test"}
        # Test logic here
```

### Testing Best Practices

**Mock External Dependencies:**
- Always mock external API calls
- Mock network requests using `unittest.mock` or `pytest-mock`
- Don't make real network calls in tests

**Test Both Success and Failure Cases:**
- Test happy path (successful operations)
- Test error handling (exceptions, invalid input, etc.)
- Test edge cases (empty strings, None values, etc.)

**Use Fixtures:**
```python
@pytest.fixture
def sample_packet():
    """Create a sample test packet."""
    return packets.core.Packet(
        from_call="TEST",
        to_call="DEST",
        message_text="test",
    )

def test_with_fixture(sample_packet):
    """Test using fixture."""
    result = process(sample_packet)
    assert result is not None
```

### What to Test

- Plugin setup and initialization
- Message processing logic
- Configuration loading
- Error handling
- Helper functions
- Thread creation (if applicable)
- CLI commands

---

## Thread Management

### APRSDThread Base Class

All background threads must inherit from `APRSDThread`:

```python
from aprsd.threads import APRSDThread

class MyThread(APRSDThread):
    """Background thread description."""

    def __init__(self, config):
        super().__init__("MyThread")
        self.config = config

    def loop(self):
        """Main thread loop logic."""
        # Your periodic logic here
        return True  # Return True to continue, False to stop
```

**Key Points:**
- Place all thread implementations using APRSDThread base class
- Implement the `loop()` method for periodic operations
- Handle graceful shutdown properly
- Use appropriate logging

---

## Thread-Specific Guidelines

When implementing threads:
- All threads should be done with APRSDThread base class
- Implement proper lifecycle methods
- Handle exceptions within the thread
- Log thread startup and shutdown
- Use configuration for thread intervals

---

## Additional Guidelines

### Documentation

- Maintain docs in `docs/` directory
- Use Sphinx for documentation generation
- Keep README files up to date with plugin functionality
- Document configuration options in docstrings

### Pre-commit Hooks

- Use `.pre-commit-config.yaml` for code quality
- Include linting, formatting, and type checking
- Run pre-commit hooks before committing

### Build System

```toml
[build-system]
requires = [
    "setuptools>=69.5.0",
    "setuptools_scm>=0",
    "wheel",
]
build-backend = "setuptools.build_meta"
```

### Package Configuration

```toml
[tool.setuptools]
packages = ["module_name"]
# or for auto-discovery:
packages = {find = {}}

[tool.setuptools.package-data]
"*" = ["LICENSE"]
"module_name" = ["README.md"]
```

---

## Summary

When developing APRSD plugins and extensions:

1. **Follow the standard project structure** with underscored module names
2. **Inherit from the correct base classes** (APRSDRegexCommandPluginBase or APRSDExtensionBase)
3. **Implement required methods** (setup, process, help, create_threads)
4. **Use oslo.config** for all configuration management
5. **Provide CLI commands** for config export
6. **Write comprehensive tests** with proper mocking
7. **Handle errors gracefully** with appropriate logging
8. **Format APRS messages** to 67 character limit
9. **Use APRSDThread** for all background threads
10. **Maintain clean, simple, DRY code**

These standards ensure consistency, maintainability, and quality across all APRSD projects.
