"""AI Assistant – Unified wrapper for GSD-2 and Superpowers integration.

This module provides the AI-assisted development interface that
can be invoked from:
- The editor's command palette (Ctrl+Shift+A)
- The Tools > AI Assistant menu
- Directly via Python script

It wraps GSD-2 commands and Superpowers skills into a single
interface usable from within PyRME.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from pyrme.devtools.gsd.config import GSDConfig
from pyrme.devtools.superpowers.skills_loader import Skill, SkillsLoader


class AIAssistant:
    """Unified AI assistant wrapping GSD-2 and Superpowers."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.gsd_config = GSDConfig(project_root=self.project_root)
        self.skills_loader = SkillsLoader(project_root=self.project_root)

    # ── GSD Integration ──────────────────────────────────────

    def gsd_auto(self, task: str = "") -> str:
        """Run GSD in autonomous mode (Context7: `/gsd auto`)."""
        return self._run_gsd_command("auto", task)

    def gsd_plan(self, task: str = "") -> str:
        """Run GSD planning phase."""
        return self._run_gsd_command("plan", task)

    def gsd_status(self) -> str:
        """Get GSD project status."""
        return self._run_gsd_command("status")

    def _run_gsd_command(self, subcommand: str, *args: str) -> str:
        """Execute a GSD CLI command and return output."""
        cmd = [str(self._gsd_binary()), subcommand, *[a for a in args if a]]
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout or result.stderr or "(no output)"
        except FileNotFoundError:
            return (
                "Error: repo-local GSD-2 is not installed. "
                "Use Node.js 22+ and run: npm install"
            )
        except subprocess.TimeoutExpired:
            return "Error: GSD command timed out after 60s"

    def _gsd_binary(self) -> Path:
        """Resolve the repo-local gsd binary."""
        suffix = ".cmd" if os.name == "nt" else ""
        return self.project_root / "node_modules" / ".bin" / f"gsd{suffix}"

    # ── Superpowers Skills ───────────────────────────────────

    def list_skills(self) -> list[Skill]:
        """List all available Superpowers skills."""
        return self.skills_loader.find_skills()

    def use_skill(self, skill_name: str) -> str:
        """Load and return a specific skill's content."""
        skill = self.skills_loader.resolve_skill(skill_name)
        if skill is None:
            available = self.list_skills()
            names = ", ".join(s.name for s in available)
            return f'Skill "{skill_name}" not found. Available: {names}'
        return (
            f"# {skill.name}\n"
            f"# {skill.description}\n"
            f"# Path: {skill.path}\n"
            f"# {'=' * 50}\n\n"
            f"{skill.content}"
        )

    # ── Convenience Methods ──────────────────────────────────

    def brainstorm(self, topic: str = "") -> str:
        """Activate the brainstorming skill."""
        content = self.use_skill("superpowers:brainstorming")
        if topic:
            return f"Topic: {topic}\n\n{content}"
        return content

    def plan(self, task: str = "") -> str:
        """Activate the planning skill + GSD planning."""
        skill_content = self.use_skill("superpowers:planning")
        if task:
            gsd_output = self.gsd_plan(task)
            return f"Task: {task}\n\n{skill_content}\n\n--- GSD Output ---\n{gsd_output}"
        return skill_content

    def tdd(self) -> str:
        """Activate TDD skill."""
        return self.use_skill("superpowers:tdd")

    def review(self) -> str:
        """Activate code review skill."""
        return self.use_skill("superpowers:code-review")

    def info(self) -> dict[str, Any]:
        """Return assistant configuration info."""
        skills = self.list_skills()
        return {
            "project_root": str(self.project_root),
            "gsd_mode": self.gsd_config.mode,
            "skills_count": len(skills),
            "skills": [
                {"name": s.name, "source": s.source_type, "desc": s.description}
                for s in skills
            ],
            "gsd_dir": str(self.gsd_config.gsd_dir),
            "pi_skills_dir": str(self.gsd_config.pi_skills_dir),
        }
