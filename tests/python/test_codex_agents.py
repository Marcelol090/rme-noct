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
    agent = root / f"{name}.toml"
    agent.write_text(body, encoding="utf-8")


def test_codex_agent_stack_validates_required_agents() -> None:
    from pyrme.devtools.codex.agents import CodexAgentStack

    temp_root = _workspace("codex-agents")
    try:
        agent_dir = temp_root / ".codex" / "agents"
        _write_agent(
            agent_dir,
            "planner",
            (
                'name = "planner"\n'
                'description = "Superpowers planejamento"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\n'
                "NÃO use caveman aqui.\n"
                '"""\n'
            ),
        )
        _write_agent(
            agent_dir,
            "worker",
            (
                'name = "worker"\n'
                'description = "Executor"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "medium"\n'
                'sandbox_mode = "workspace-write"\n'
                'developer_instructions = """\n'
                "/caveman full\n"
                "$ui-system-discipline\n"
                "PLAN.md\n"
                "TDD\n"
                "docs_researcher\n"
                '"""\n'
            ),
        )
        _write_agent(
            agent_dir,
            "docs-researcher",
            (
                'name = "docs_researcher"\n'
                'description = "Context7 para PyQt6"\n'
                'model = "gpt-5.4-mini"\n'
                'model_reasoning_effort = "medium"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\n'
                "Execute /caveman full\n"
                '"""\n'
                "[mcp_servers.context7]\n"
                'command = "c7-mcp-server"\n'
            ),
        )
        _write_agent(
            agent_dir,
            "reviewer",
            (
                'name = "reviewer"\n'
                'description = "Review"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\n'
                "Execute /caveman lite\n"
                '"""\n'
            ),
        )

        stack = CodexAgentStack(agent_dir=agent_dir)
        issues = stack.validate_required_agents()

        assert issues == []
        assert [agent.name for agent in stack.list_agents()] == [
            "docs_researcher",
            "planner",
            "reviewer",
            "worker",
        ]
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
