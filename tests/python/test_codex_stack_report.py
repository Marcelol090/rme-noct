from __future__ import annotations

import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _workspace(name: str) -> Path:
    temp_root = ROOT / ".tmp-tests" / f"{name}-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True, exist_ok=True)
    return temp_root


def _write_agent(root: Path, name: str, body: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{name}.toml").write_text(body, encoding="utf-8")


def _write_skill(root: Path, name: str, description: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n# Body\n",
        encoding="utf-8",
    )


def test_stack_report_lists_and_validates_stack(monkeypatch) -> None:
    from pyrme.devtools.codex.stack_report import build_stack_report

    temp_root = _workspace("stack-report")
    try:
        project_root = temp_root / "repo"
        home_dir = temp_root / "home"
        agent_dir = home_dir / ".codex" / "agents"
        codex_skills = home_dir / ".codex" / "skills"
        superpowers_skills = home_dir / ".codex" / "superpowers" / "skills"
        caveman_skill_root = home_dir / ".agents" / "skills"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "AGENTS.md").write_text(
            "# RME Noct - Agent Instructions\n",
            encoding="utf-8",
        )

        _write_agent(
            agent_dir,
            "planner",
            (
                'name = "planner"\n'
                'description = "Planner"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\nNÃO use caveman aqui.\n"""\n'
            ),
        )
        _write_agent(
            agent_dir,
            "worker",
            (
                'name = "worker"\n'
                'description = "Worker"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "medium"\n'
                'sandbox_mode = "workspace-write"\n'
                'developer_instructions = """\n'
                '/caveman full\n'
                '$ui-system-discipline\n'
                'PLAN.md\n'
                'TDD\n'
                'docs_researcher\n'
                '"""\n'
            ),
        )
        _write_agent(
            agent_dir,
            "docs_researcher",
            (
                'name = "docs_researcher"\n'
                'description = "Docs"\n'
                'model = "gpt-5.4-mini"\n'
                'model_reasoning_effort = "medium"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\nExecute /caveman full\n"""\n'
                "[mcp_servers.context7]\ncommand = \"c7-mcp-server\"\n"
            ),
        )
        _write_agent(
            agent_dir,
            "reviewer",
            (
                'name = "reviewer"\n'
                'description = "Reviewer"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\nExecute /caveman lite\n"""\n'
            ),
        )
        _write_skill(codex_skills, "ui-system-discipline", "UI discipline")
        _write_skill(codex_skills, "premium-ui", "Premium UI")
        _write_skill(superpowers_skills, "brainstorming", "Brainstorm")
        _write_skill(caveman_skill_root, "caveman", "Caveman")

        monkeypatch.setattr(
            "pyrme.devtools.codex.stack_report.shutil.which",
            lambda name: "/tmp/c7-mcp-server" if name == "c7-mcp-server" else None,
        )
        report = build_stack_report(project_root=project_root, home_dir=home_dir)
        rendered = report.render()

        assert "Codex + GSD + Superpowers Stack" in rendered
        assert "planner: model=gpt-5.4, sandbox=read-only" in rendered
        assert "worker: model=gpt-5.4, sandbox=workspace-write" in rendered
        assert "docs_researcher: model=gpt-5.4-mini, sandbox=read-only" in rendered
        assert "reviewer: model=gpt-5.4, sandbox=read-only" in rendered
        assert "- ui-system-discipline" in rendered
        assert "- premium-ui" in rendered
        assert "- brainstorming" in rendered
        assert "- ok" in rendered
        assert report.ok is True
        assert report.data["checks"]["caveman_skill"] is True
        assert report.data["checks"]["repo_agents_md"] is True
        assert report.data["checks"]["context7_command"] is True
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_stack_report_tolerates_integrated_codex_session_without_local_agents(
    monkeypatch,
) -> None:
    from pyrme.devtools.codex.stack_report import build_stack_report

    temp_root = _workspace("stack-report-integrated-session")
    try:
        home_dir = temp_root / "Users" / "Marcelo"
        project_root = home_dir / "Desktop" / "repo"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "AGENTS.md").write_text(
            "# RME Noct - Agent Instructions\n",
            encoding="utf-8",
        )
        _write_skill(home_dir / ".agents" / "skills", "caveman", "Caveman")
        monkeypatch.setattr(
            "pyrme.devtools.codex.stack_report.Path.home",
            lambda: (_ for _ in ()).throw(RuntimeError("no home")),
        )
        monkeypatch.setattr(
            "pyrme.devtools.codex.stack_report.shutil.which",
            lambda _name: None,
        )

        report = build_stack_report(project_root=project_root)

        assert report.ok is True
        assert report.data["checks"]["local_agents_optional"] is True
        assert report.data["checks"]["context7_command"] is False
        assert "missing command on PATH: c7-mcp-server" not in report.render()
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_stack_report_flags_missing_ollama_for_local_only_project(monkeypatch) -> None:
    from pyrme.devtools.codex.stack_report import build_stack_report

    temp_root = _workspace("stack-report-ollama")
    try:
        project_root = temp_root / "repo"
        home_dir = temp_root / "home"
        agent_dir = home_dir / ".codex" / "agents"
        codex_skills = home_dir / ".codex" / "skills"
        superpowers_skills = home_dir / ".codex" / "superpowers" / "skills"
        caveman_skill_root = home_dir / ".agents" / "skills"
        project_root.mkdir(parents=True, exist_ok=True)
        project_gsd = project_root / ".gsd"
        project_gsd.mkdir(parents=True, exist_ok=True)
        (project_gsd / "preferences.md").write_text(
            "---\nversion: 1\nmodels:\n  planning: ollama/qwen2.5-coder:3b\n---\n",
            encoding="utf-8",
        )

        _write_agent(
            agent_dir,
            "planner",
            (
                'name = "planner"\n'
                'description = "Planner"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\nNÃO use caveman aqui.\n"""\n'
            ),
        )
        _write_agent(
            agent_dir,
            "worker",
            (
                'name = "worker"\n'
                'description = "Worker"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "medium"\n'
                'sandbox_mode = "workspace-write"\n'
                'developer_instructions = """\n'
                '/caveman full\n'
                '$ui-system-discipline\n'
                'PLAN.md\n'
                'TDD\n'
                'docs_researcher\n'
                '"""\n'
            ),
        )
        _write_agent(
            agent_dir,
            "docs_researcher",
            (
                'name = "docs_researcher"\n'
                'description = "Docs"\n'
                'model = "gpt-5.4-mini"\n'
                'model_reasoning_effort = "medium"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\nExecute /caveman full\n"""\n'
                "[mcp_servers.context7]\ncommand = \"c7-mcp-server\"\n"
            ),
        )
        _write_agent(
            agent_dir,
            "reviewer",
            (
                'name = "reviewer"\n'
                'description = "Reviewer"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\nExecute /caveman lite\n"""\n'
            ),
        )
        _write_skill(codex_skills, "ui-system-discipline", "UI discipline")
        _write_skill(codex_skills, "premium-ui", "Premium UI")
        _write_skill(superpowers_skills, "brainstorming", "Brainstorm")
        _write_skill(caveman_skill_root, "caveman", "Caveman")

        monkeypatch.setattr(
            "pyrme.devtools.codex.stack_report.shutil.which",
            lambda name: "/tmp/c7-mcp-server" if name == "c7-mcp-server" else None,
        )

        report = build_stack_report(project_root=project_root, home_dir=home_dir)

        assert report.ok is False
        assert "ollama" in report.render()
        assert any("ollama" in issue for issue in report.data["validation"]["issues"])
        assert report.data["gsd"]["configured_model_providers"] == ["ollama"]
        assert report.data["checks"]["ollama_command"] is False
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_pyrme_stack_command_prints_report(monkeypatch, capsys) -> None:
    from pyrme.__main__ import main

    class DummyReport:
        def render(self) -> str:
            return "stack-report\n"

    monkeypatch.setattr(
        "pyrme.devtools.codex.stack_report.build_stack_report",
        lambda: DummyReport(),
    )

    exit_code = main(["pyrme", "stack"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "stack-report\n"


def test_pyrme_stack_command_supports_json(monkeypatch, capsys) -> None:
    from pyrme.__main__ import main

    class DummyReport:
        def render(self) -> str:
            return "text-report\n"

        def render_json(self) -> str:
            return '{"ok": true}\n'

        @property
        def ok(self) -> bool:
            return True

    monkeypatch.setattr(
        "pyrme.devtools.codex.stack_report.build_stack_report",
        lambda: DummyReport(),
    )

    exit_code = main(["pyrme", "stack", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == '{"ok": true}\n'
