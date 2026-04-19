"""Helpers for validating the local Codex agent stack.

The repo treats ``~/.codex/agents`` as the source of truth for the
planner/worker/docs-researcher/reviewer contract requested by the user.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    tomllib_module: Any = importlib.import_module("tomllib")
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib_module = importlib.import_module("tomli")


def _safe_home() -> Path:
    try:
        return Path.home()
    except (OSError, RuntimeError):
        return Path.cwd()


@dataclass(frozen=True)
class CodexAgentSpec:
    name: str
    description: str
    model: str
    model_reasoning_effort: str
    sandbox_mode: str
    developer_instructions: str
    mcp_servers: dict[str, Any]
    path: Path


@dataclass(frozen=True)
class CodexAgentExpectation:
    model: str
    sandbox_mode: str
    instructions: tuple[str, ...] = ()
    mcp_command: str | None = None


class CodexAgentStack:
    def __init__(self, agent_dir: Path | None = None) -> None:
        self.agent_dir = agent_dir or (_safe_home() / ".codex" / "agents")

    def list_agents(self) -> list[CodexAgentSpec]:
        if not self.agent_dir.exists():
            return []
        agents: list[CodexAgentSpec] = []
        for path in sorted(self.agent_dir.glob("*.toml")):
            parsed: dict[str, Any] = tomllib_module.loads(path.read_text(encoding="utf-8"))
            mcp_servers: dict[str, Any] = {}
            raw_servers = parsed.get("mcp_servers", {})
            if isinstance(raw_servers, dict):
                for key, value in raw_servers.items():
                    if isinstance(value, dict):
                        mcp_servers[str(key)] = value
            agents.append(
                CodexAgentSpec(
                    name=str(parsed.get("name", path.stem)),
                    description=str(parsed.get("description", "")),
                    model=str(parsed.get("model", "")),
                    model_reasoning_effort=str(parsed.get("model_reasoning_effort", "")),
                    sandbox_mode=str(parsed.get("sandbox_mode", "")),
                    developer_instructions=str(parsed.get("developer_instructions", "")),
                    mcp_servers=mcp_servers,
                    path=path,
                )
            )
        return agents

    def by_name(self) -> dict[str, CodexAgentSpec]:
        return {agent.name: agent for agent in self.list_agents()}

    def validate_required_agents(self) -> list[str]:
        agents = self.by_name()
        required: dict[str, CodexAgentExpectation] = {
            "planner": CodexAgentExpectation(
                model="gpt-5.4",
                sandbox_mode="read-only",
            ),
            "worker": CodexAgentExpectation(
                model="gpt-5.4",
                sandbox_mode="workspace-write",
                instructions=(
                    "/caveman full",
                    "$ui-system-discipline",
                    "PLAN.md",
                    "TDD",
                    "docs_researcher",
                ),
            ),
            "docs_researcher": CodexAgentExpectation(
                model="gpt-5.4-mini",
                sandbox_mode="read-only",
                mcp_command="c7-mcp-server",
            ),
            "reviewer": CodexAgentExpectation(
                model="gpt-5.4",
                sandbox_mode="read-only",
            ),
        }

        if not agents or not set(required).intersection(agents):
            return []

        issues: list[str] = []

        for name, expected in required.items():
            agent = agents.get(name)
            if agent is None:
                issues.append(f"missing agent: {name}")
                continue

            if agent.model != expected.model:
                issues.append(
                    f"{name}: model {agent.model!r} != {expected.model!r}"
                )
            if agent.sandbox_mode != expected.sandbox_mode:
                issues.append(
                    f"{name}: sandbox_mode {agent.sandbox_mode!r} != {expected.sandbox_mode!r}"
                )

            instructions = agent.developer_instructions
            for token in expected.instructions:
                if token not in instructions:
                    issues.append(f"{name}: missing instruction token {token!r}")

            mcp_command = expected.mcp_command
            if mcp_command is not None:
                context7 = agent.mcp_servers.get("context7")
                command = ""
                if isinstance(context7, dict):
                    command = str(context7.get("command", ""))
                if command != mcp_command:
                    issues.append(
                        f"{name}: context7 command {command!r} != {mcp_command!r}"
                    )

        return issues
