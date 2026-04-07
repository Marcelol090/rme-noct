import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _write_skill(root: Path, name: str, description: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        (
            "---\n"
            f"name: {name}\n"
            f"description: {description}\n"
            "---\n"
            "# Skill body\n"
        ),
        encoding="utf-8",
    )


def test_loader_prefers_repo_then_user_then_bundled(tmp_path: Path) -> None:
    from pyrme.devtools.superpowers.skills_loader import SkillsLoader

    project_root = tmp_path / "repo"
    repo_skills = project_root / ".agents" / "skills"
    user_skills = tmp_path / "home" / ".agents" / "skills"
    bundled_skills = tmp_path / "home" / ".codex" / "superpowers" / "skills"

    _write_skill(bundled_skills, "brainstorming", "Bundled brainstorming")
    _write_skill(user_skills, "brainstorming", "User brainstorming")
    _write_skill(repo_skills, "brainstorming", "Repo brainstorming")
    _write_skill(bundled_skills, "requesting-code-review", "Bundled review")

    loader = SkillsLoader(
        project_root=project_root,
        repo_skills_dir=repo_skills,
        user_skills_dir=user_skills,
        superpowers_dir=bundled_skills,
    )

    skill = loader.resolve_skill("brainstorming")
    assert skill is not None
    assert skill.source_type == "repo"

    forced = loader.resolve_skill("superpowers:brainstorming")
    assert forced is not None
    assert forced.source_type == "superpowers"

    visible = {item.name: item.source_type for item in loader.find_skills()}
    assert visible["brainstorming"] == "repo"
    assert visible["requesting-code-review"] == "superpowers"
