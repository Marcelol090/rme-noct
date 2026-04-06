"""Superpowers Skills Loader for PyRME.

Provides Python bindings to discover and load Superpowers skills
for use within the editor's AI assistant. Based on the Superpowers
plugin architecture (Context7: /obra/superpowers).

Official Skill Resolution Order (from Context7 docs):
1. Personal skills (project-local or ~/.config/superpowers/skills/)
2. Superpowers skills (cloned from git repo)
3. Personal skills OVERRIDE superpowers skills when names match
4. Prefix "superpowers:" to force using the bundled version

Official SKILL.md Format:
  ---
  name: skill-name
  description: Use when [condition] - [what it does]
  ---
  # Skill Content
  [Instructions here]

Official Skill Directory Structure:
  skill-name/
  ├── SKILL.md          (router + principles — always loaded)
  ├── workflows/        (procedures — FOLLOW)
  ├── references/       (knowledge — READ)
  ├── templates/        (output structures — COPY + FILL)
  └── scripts/          (reusable code — EXECUTE)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    """Represents a discovered Superpowers skill."""

    name: str
    description: str
    path: Path
    source_type: str  # "personal" or "superpowers"

    @property
    def content(self) -> str:
        """Read and return the skill content (stripping frontmatter)."""
        skill_file = self.path / "SKILL.md"
        if not skill_file.exists():
            return ""
        raw = skill_file.read_text(encoding="utf-8")
        return _strip_frontmatter(raw)

    @property
    def has_workflows(self) -> bool:
        """Check if this skill has a workflows/ directory."""
        return (self.path / "workflows").is_dir()

    @property
    def has_references(self) -> bool:
        """Check if this skill has a references/ directory."""
        return (self.path / "references").is_dir()

    @property
    def has_templates(self) -> bool:
        """Check if this skill has a templates/ directory."""
        return (self.path / "templates").is_dir()

    @property
    def has_scripts(self) -> bool:
        """Check if this skill has a scripts/ directory."""
        return (self.path / "scripts").is_dir()

    def list_workflows(self) -> list[str]:
        """List workflow files in workflows/ directory."""
        wf_dir = self.path / "workflows"
        if not wf_dir.is_dir():
            return []
        return [f.stem for f in wf_dir.iterdir() if f.suffix == ".md"]


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from skill content."""
    pattern = r"^---\s*\n.*?\n---\s*\n"
    return re.sub(pattern, "", text, count=1, flags=re.DOTALL).strip()


def _extract_frontmatter(text: str) -> dict[str, str]:
    """Extract name and description from YAML frontmatter."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


class SkillsLoader:
    """Discovers and loads Superpowers skills.

    Follows the official resolution order from Context7 docs:
    1. Personal skills (project .superpowers/ or ~/.config/superpowers/skills/)
    2. Superpowers bundled skills
    3. Personal overrides bundled when names match
    4. "superpowers:" prefix forces bundled version
    """

    def __init__(
        self,
        project_root: Path | None = None,
        superpowers_dir: Path | None = None,
        personal_dir: Path | None = None,
    ) -> None:
        self.project_root = project_root or Path.cwd()

        # Official paths per Context7 docs
        self.superpowers_dir = superpowers_dir or (
            self.project_root / ".superpowers" / "skills"
        )
        self.personal_dir = personal_dir or (
            Path.home() / ".config" / "superpowers" / "skills"
        )

    def find_skills(self, max_depth: int = 3) -> list[Skill]:
        """Find all available skills from personal and superpowers directories.

        Per official docs: personal skills override superpowers when names match.
        """
        personal = self._scan_dir(self.personal_dir, "personal", max_depth)
        superpowers = self._scan_dir(self.superpowers_dir, "superpowers", max_depth)

        # Personal skills override superpowers when names match
        seen_names: set[str] = set()
        result: list[Skill] = []
        for skill in personal:
            seen_names.add(skill.name)
            result.append(skill)
        for skill in superpowers:
            if skill.name not in seen_names:
                result.append(skill)

        return result

    def resolve_skill(self, skill_name: str) -> Skill | None:
        """Resolve a skill by name.

        Per official docs:
        - "superpowers:" prefix forces the bundled version
        - Otherwise, personal overrides superpowers
        """
        force_superpowers = skill_name.startswith("superpowers:")
        clean_name = skill_name.removeprefix("superpowers:")

        # Try personal first (unless explicitly superpowers:)
        if not force_superpowers:
            personal_path = self.personal_dir / clean_name
            if personal_path.exists() and (personal_path / "SKILL.md").exists():
                return self._load_skill(personal_path, "personal")

        # Try superpowers
        sp_path = self.superpowers_dir / clean_name
        if sp_path.exists() and (sp_path / "SKILL.md").exists():
            return self._load_skill(sp_path, "superpowers")

        return None

    def _scan_dir(
        self, directory: Path, source_type: str, max_depth: int
    ) -> list[Skill]:
        """Scan a directory for skills containing SKILL.md."""
        skills: list[Skill] = []
        if not directory.exists():
            return skills

        self._scan_recursive(directory, source_type, 0, max_depth, skills)
        return skills

    def _scan_recursive(
        self,
        directory: Path,
        source_type: str,
        depth: int,
        max_depth: int,
        results: list[Skill],
    ) -> None:
        """Recursively scan for SKILL.md files up to max_depth."""
        if depth > max_depth:
            return

        for item in directory.iterdir():
            if item.is_dir():
                if (item / "SKILL.md").exists():
                    skill = self._load_skill(item, source_type)
                    if skill:
                        results.append(skill)
                else:
                    self._scan_recursive(item, source_type, depth + 1, max_depth, results)

    def _load_skill(self, path: Path, source_type: str) -> Skill | None:
        """Load a single skill from its directory."""
        skill_file = path / "SKILL.md"
        if not skill_file.exists():
            return None

        text = skill_file.read_text(encoding="utf-8")
        fm = _extract_frontmatter(text)

        return Skill(
            name=fm.get("name", path.name),
            description=fm.get("description", ""),
            path=path,
            source_type=source_type,
        )
