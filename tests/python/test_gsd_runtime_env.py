"""Tests for the project-local GSD runtime environment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyrme.devtools.gsd.runtime import build_gsd_env

if TYPE_CHECKING:
    from pathlib import Path


def test_build_gsd_env_uses_project_local_gsd_home(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()

    env = build_gsd_env(project_root)

    assert env["GSD_HOME"] == str(project_root / ".gsd")
    assert (project_root / ".gsd").is_dir()
