"""GSD-2 project configuration for PyRME.

This module provides the configuration interface for GSD-2
(Get Stuff Done) coding agent integration within the editor.

Official GSD-2 Skill Directories (from Context7 docs):
- User-scope (global):    ~/.gsd/agent/skills/
- Project-scope (local):  .pi/agent/skills/

Both follow the SKILL.md + router pattern:
  skill-name/
  ├── SKILL.md          (router + principles)
  ├── workflows/        (procedures)
  ├── references/       (knowledge)
  ├── templates/        (output structures)
  └── scripts/          (reusable code)

Official Preferences Schema (from Context7 docs):
  Located at: .gsd/preferences.md (YAML frontmatter)
  Required fields: version, models, verification_commands
  Optional fields: budget_ceiling, auto_supervisor, git, skill_rules,
                   notifications, post_unit_hooks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GSDConfig:
    """GSD-2 project configuration.

    Follows the official GSD-2 directory and preferences conventions
    as documented at https://github.com/gsd-build/gsd-2 (Context7).
    """

    project_root: Path = field(default_factory=lambda: Path.cwd())
    mode: str = "solo"  # "solo" or "team"

    # Skill preferences (from Context7: GSD skill_rules config)
    always_use_skills: list[str] = field(
        default_factory=lambda: ["debug-like-expert"]
    )
    prefer_skills: list[str] = field(
        default_factory=lambda: ["frontend-design"]
    )
    avoid_skills: list[str] = field(default_factory=list)
    skill_rules: list[dict[str, str | list[str]]] = field(
        default_factory=lambda: [
            {"when": "task involves PyQt6 UI", "use": ["frontend-design"]},
            {"when": "task involves Rust core", "prefer": ["systems-programming"]},
            {"when": "working with OTBM parsing", "use": ["binary-formats"]},
        ]
    )

    # Verification commands (official schema: verification_commands)
    verification_commands: list[str] = field(
        default_factory=lambda: [
            "pytest tests/ -v --tb=short",
            "ruff check pyrme/",
            "mypy pyrme/ --ignore-missing-imports",
            "cargo test --manifest-path crates/rme_core/Cargo.toml",
        ]
    )

    # Budget (official schema: budget_ceiling)
    budget_ceiling: float = 50.00

    @property
    def gsd_dir(self) -> Path:
        """Project .gsd directory (preferences, milestones)."""
        return self.project_root / ".gsd"

    @property
    def pi_skills_dir(self) -> Path:
        """Project-scope skills directory (official GSD convention)."""
        return self.project_root / ".pi" / "agent" / "skills"

    @property
    def global_skills_dir(self) -> Path:
        """User-scope global skills directory (official GSD convention)."""
        return Path.home() / ".gsd" / "agent" / "skills"

    @property
    def preferences_file(self) -> Path:
        """Path to .gsd/preferences.md."""
        return self.gsd_dir / "preferences.md"

    def ensure_dirs(self) -> None:
        """Create required GSD directories if they don't exist."""
        self.gsd_dir.mkdir(parents=True, exist_ok=True)
        self.pi_skills_dir.mkdir(parents=True, exist_ok=True)

    def list_project_skills(self) -> list[str]:
        """List all project-scope skills in .pi/agent/skills/."""
        if not self.pi_skills_dir.exists():
            return []
        return [
            d.name
            for d in self.pi_skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        ]

    def list_global_skills(self) -> list[str]:
        """List all global skills in ~/.gsd/agent/skills/."""
        if not self.global_skills_dir.exists():
            return []
        return [
            d.name
            for d in self.global_skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        ]

    def to_preferences_yaml(self) -> str:
        """Generate .gsd/preferences.md content following official schema."""
        lines = [
            "---",
            "version: 1",
            f"mode: {self.mode}",
            "",
            "# Skills",
            "skill_discovery: suggest",
            "always_use_skills:",
        ]
        for s in self.always_use_skills:
            lines.append(f"  - {s}")
        lines.append("prefer_skills:")
        for s in self.prefer_skills:
            lines.append(f"  - {s}")
        if self.avoid_skills:
            lines.append("avoid_skills:")
            for s in self.avoid_skills:
                lines.append(f"  - {s}")
        lines.extend([
            "",
            "# Verification commands",
            "verification_commands:",
        ])
        for cmd in self.verification_commands:
            lines.append(f"  - {cmd}")
        lines.extend([
            "",
            f"budget_ceiling: {self.budget_ceiling}",
            "---",
        ])
        return "\n".join(lines) + "\n"
