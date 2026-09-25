"""Verify oslo.config entry points declared in pyproject.toml resolve.

Regression test for the `aprsd sample-config` AttributeError caused by a
`oslo.config.opts.defaults` entry point pointing at a nonexistent
`defaults` function (see handover session-state-2026-09-24.json).
"""

import importlib
import tomllib
from pathlib import Path


def _entry_points():
    root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return pyproject["project"]["entry-points"]


def test_oslo_config_entry_points_resolve():
    """Every oslo.config entry point target must resolve to a real attribute."""
    entry_points = _entry_points()
    for group, targets in entry_points.items():
        if not group.startswith("oslo.config.opts"):
            continue
        for target in targets.values():
            module_name, _, attr = target.partition(":")
            module = importlib.import_module(module_name)
            assert hasattr(module, attr), (
                f"{group} entry point '{target}' does not resolve: "
                f"module '{module_name}' has no attribute '{attr}'"
            )
