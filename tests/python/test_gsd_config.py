from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


def _write_skill(root: Path, name: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {name}\n---\n# body\n",
        encoding="utf-8",
    )



@pytest.mark.parametrize("error", [RuntimeError("no home"), OSError("mock os error")])
def test_gsd_config_user_skills_dir_falls_back_to_cwd(
    monkeypatch, tmp_path: Path, error: Exception
) -> None:
    from pyrme.devtools.gsd.config import GSDConfig

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "pyrme.devtools.gsd.config.Path.home",
        lambda: (_ for _ in ()).throw(error),
    )

    config = GSDConfig(project_root=tmp_path / "repo")

    assert config.user_skills_dir == tmp_path / ".agents" / "skills"
    assert config.global_skills_dir == config.user_skills_dir


def test_gsd_config_lists_project_and_global_skills(monkeypatch, tmp_path: Path) -> None:
    from pyrme.devtools.gsd.config import GSDConfig

    home_dir = tmp_path / "home"
    project_root = tmp_path / "repo"
    _write_skill(project_root / ".agents" / "skills", "repo-skill")
    _write_skill(home_dir / ".agents" / "skills", "user-skill")
    monkeypatch.setattr("pyrme.devtools.gsd.config.Path.home", lambda: home_dir)

    config = GSDConfig(project_root=project_root)

    assert config.repo_skills_dir == project_root / ".agents" / "skills"
    assert config.user_skills_dir == home_dir / ".agents" / "skills"
    assert config.pi_skills_dir == config.repo_skills_dir
    assert sorted(config.list_project_skills()) == ["repo-skill"]
    assert sorted(config.list_global_skills()) == ["user-skill"]
