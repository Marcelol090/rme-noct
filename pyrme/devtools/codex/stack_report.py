"""Text report for the local Codex + GSD + Superpowers stack."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pyrme.devtools.codex.agents import CodexAgentStack
from pyrme.devtools.gsd.config import GSDConfig
from pyrme.devtools.superpowers.skills_loader import SkillsLoader


@dataclass(frozen=True)
class StackReport:
    data: dict[str, Any]
    lines: list[str]

    @property
    def ok(self) -> bool:
        return not self.data["validation"]["issues"]

    def render(self) -> str:
        return "\n".join(self.lines) + "\n"

    def render_json(self) -> str:
        return json.dumps(self.data, indent=2, sort_keys=True) + "\n"


def _skill_exists(path: Path) -> bool:
    return (path / "SKILL.md").is_file()


def _default_home(project_root: Path) -> Path:
    try:
        return Path.home()
    except (OSError, RuntimeError):
        for candidate in (project_root, *project_root.parents):
            if candidate.parent.name.lower() == "users":
                return candidate
        return project_root


def _read_project_preferences(project_root: Path) -> str:
    for candidate in (
        project_root / ".gsd" / "PREFERENCES.md",
        project_root / ".gsd" / "preferences.md",
    ):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    return ""


def _extract_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    return parts[1]


_PROVIDER_PATTERN = re.compile(r"\b([a-z0-9_-]+)/[A-Za-z0-9_.:-]+")


def _extract_model_providers(preferences_text: str) -> set[str]:
    frontmatter = _extract_frontmatter(preferences_text)
    if not frontmatter:
        return set()

    providers: set[str] = set()
    in_models = False
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if not in_models:
            if stripped == "models:":
                in_models = True
            continue

        if not line.startswith(" "):
            break

        for match in _PROVIDER_PATTERN.finditer(stripped):
            providers.add(match.group(1))

    return providers


def build_stack_report(
    project_root: Path | None = None,
    home_dir: Path | None = None,
) -> StackReport:
    project_root = project_root or Path.cwd()
    home_dir = home_dir or _default_home(project_root)

    gsd_config = GSDConfig(project_root=project_root)
    skills_loader = SkillsLoader(
        project_root=project_root,
        user_skills_dir=home_dir / ".gsd" / "agent" / "skills",
        codex_skills_dir=home_dir / ".codex" / "skills",
        superpowers_dir=home_dir / ".codex" / "superpowers" / "skills",
    )
    codex_stack = CodexAgentStack(agent_dir=home_dir / ".codex" / "agents")

    agents = codex_stack.by_name()
    issues = codex_stack.validate_required_agents()
    codex_skills = [skill for skill in skills_loader.find_skills() if skill.source_type == "codex"]
    superpowers_skills = [
        skill for skill in skills_loader.find_skills() if skill.source_type == "superpowers"
    ]
    caveman_skill = home_dir / ".agents" / "skills" / "caveman"
    ui_system_skill = home_dir / ".codex" / "skills" / "ui-system-discipline"
    premium_ui_skill = home_dir / ".codex" / "skills" / "premium-ui"
    repo_agents = project_root / "AGENTS.md"
    context7_command = shutil.which("c7-mcp-server")
    ollama_command = shutil.which("ollama")
    preferences_text = _read_project_preferences(project_root)
    configured_model_providers = sorted(_extract_model_providers(preferences_text))

    if not _skill_exists(caveman_skill):
        issues.append(f"missing skill: {caveman_skill}")
    if not repo_agents.is_file():
        issues.append(f"missing repo instruction file: {repo_agents}")
    if "ollama" in configured_model_providers and not ollama_command:
        issues.append(
            "project models require ollama/* but `ollama` command is missing; "
            "local no-API runtime is unavailable"
        )

    lines = [
        "Codex + GSD + Superpowers Stack",
        f"Project root: {project_root}",
        f"GSD dir: {gsd_config.gsd_dir}",
        f"Codex agents dir: {codex_stack.agent_dir}",
        f"Codex skills dir: {skills_loader.codex_skills_dir}",
        f"Superpowers dir: {skills_loader.superpowers_dir}",
        f"caveman skill: {caveman_skill}",
        f"repo AGENTS.md: {repo_agents}",
        f"context7 command: {context7_command or 'missing'}",
        f"ollama command: {ollama_command or 'missing'}",
        "",
        "Agents:",
    ]

    for name in ("planner", "worker", "docs_researcher", "reviewer"):
        agent = agents.get(name)
        if agent is None:
            lines.append(f"- {name}: missing")
            continue
        lines.append(f"- {name}: model={agent.model}, sandbox={agent.sandbox_mode}")

    lines.extend(
        [
            "",
            "Codex skills:",
        ]
    )
    if codex_skills:
        for skill in codex_skills:
            lines.append(f"- {skill.name}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Superpowers skills:",
        ]
    )
    if superpowers_skills:
        for skill in superpowers_skills:
            lines.append(f"- {skill.name}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Validation:",
        ]
    )
    if issues:
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- ok")

    return StackReport(
        data={
            "project_root": str(project_root),
            "gsd_dir": str(gsd_config.gsd_dir),
            "codex_agents_dir": str(codex_stack.agent_dir),
            "codex_skills_dir": str(skills_loader.codex_skills_dir),
            "superpowers_dir": str(skills_loader.superpowers_dir),
            "checks": {
                "caveman_skill": _skill_exists(caveman_skill),
                "ui_system_discipline": _skill_exists(ui_system_skill),
                "premium_ui": _skill_exists(premium_ui_skill),
                "repo_agents_md": repo_agents.is_file(),
                "local_agents_optional": not bool(agents),
                "context7_command": context7_command is not None,
                "ollama_command": ollama_command is not None,
            },
            "gsd": {
                "configured_model_providers": configured_model_providers,
            },
            "agents": {
                name: {
                    "model": agent.model,
                    "sandbox_mode": agent.sandbox_mode,
                }
                for name, agent in agents.items()
            },
            "skills": {
                "codex": [skill.name for skill in codex_skills],
                "superpowers": [skill.name for skill in superpowers_skills],
            },
            "validation": {"issues": issues},
        },
        lines=lines,
    )
