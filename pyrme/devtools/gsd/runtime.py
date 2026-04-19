"""Runtime helpers for invoking GSD from PyRME."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def resolve_gsd_home(project_root: Path | None = None) -> Path:
    """Return the project-local GSD home directory."""
    root = project_root or Path.cwd()
    return root / ".gsd"


def build_gsd_env(
    project_root: Path | None = None,
    base_env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build an environment that forces GSD to use the repo-local home."""
    env = dict(base_env or os.environ)
    gsd_home = resolve_gsd_home(project_root)
    gsd_home.mkdir(parents=True, exist_ok=True)
    env["GSD_HOME"] = str(gsd_home)
    return env
