import shutil
import sys
import uuid
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


def _system_temp_root() -> Path:
    temp_root = ROOT / ".tmp-tests"
    temp_root.mkdir(parents=True, exist_ok=True)
    return temp_root


def _make_workspace(name: str) -> Path:
    workspace = _system_temp_root() / f"{name}-{uuid.uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def test_loader_prefers_repo_then_user_then_bundled() -> None:
    from pyrme.devtools.superpowers.skills_loader import SkillsLoader, SkillsLoaderConfig

    temp_root = _make_workspace("loader-prefer")
    try:
        project_root = temp_root / "repo"
        repo_skills = project_root / ".pi" / "agent" / "skills"
        user_skills = temp_root / "home" / ".gsd" / "agent" / "skills"
        codex_skills = temp_root / "home" / ".codex" / "skills"
        bundled_skills = temp_root / "home" / ".codex" / "superpowers" / "skills"

        _write_skill(bundled_skills, "brainstorming", "Bundled brainstorming")
        _write_skill(user_skills, "brainstorming", "User brainstorming")
        _write_skill(codex_skills, "ui-system-discipline", "Codex UI discipline")
        _write_skill(repo_skills, "brainstorming", "Repo brainstorming")
        _write_skill(bundled_skills, "requesting-code-review", "Bundled review")

        loader = SkillsLoader(
            config=SkillsLoaderConfig(
                project_root=project_root,
                repo_skills_dir=repo_skills,
                user_skills_dir=user_skills,
                codex_skills_dir=codex_skills,
                superpowers_dir=bundled_skills,
            )
        )

        skill = loader.resolve_skill("brainstorming")
        assert skill is not None
        assert skill.source_type == "repo"

        forced = loader.resolve_skill("superpowers:brainstorming")
        assert forced is not None
        assert forced.source_type == "superpowers"

        visible = {item.name: item.source_type for item in loader.find_skills()}
        assert visible["brainstorming"] == "repo"
        assert visible["ui-system-discipline"] == "codex"
        assert visible["requesting-code-review"] == "superpowers"
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_loader_defaults_use_project_pi_and_user_gsd_skills(monkeypatch) -> None:
    from pyrme.devtools.superpowers.skills_loader import SkillsLoader, SkillsLoaderConfig

    temp_root = _make_workspace("loader-defaults")
    try:
        monkeypatch.setattr(Path, "home", lambda: temp_root / "home")

        project_root = temp_root / "repo"
        loader = SkillsLoader(config=SkillsLoaderConfig(project_root=project_root))

        assert loader.repo_skills_dir == project_root / ".pi" / "agent" / "skills"
        assert loader.user_skills_dir == temp_root / "home" / ".gsd" / "agent" / "skills"
        assert loader.codex_skills_dir == temp_root / "home" / ".codex" / "skills"
        assert (
            loader.superpowers_dir
            == temp_root / "home" / ".codex" / "superpowers" / "skills"
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_loader_still_accepts_legacy_kwargs() -> None:
    from pyrme.devtools.superpowers.skills_loader import SkillsLoader

    temp_root = _make_workspace("loader-legacy-kwargs")
    try:
        project_root = temp_root / "repo"
        repo_skills = project_root / "skills"

        loader = SkillsLoader(project_root=project_root, repo_skills_dir=repo_skills)

        assert loader.project_root == project_root
        assert loader.repo_skills_dir == repo_skills
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
