from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

from pyrme.tools.ai_assistant import AIAssistant


def test_gsd_plan_uses_long_timeout(monkeypatch, settings_workspace: Path) -> None:
    seen: dict[str, int] = {}

    def fake_run(*_args, **kwargs):
        seen["timeout"] = kwargs["timeout"]
        return SimpleNamespace(stdout="ok", stderr="", returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    assistant = AIAssistant(project_root=settings_workspace)
    monkeypatch.setattr(assistant, "_gsd_binary", lambda: Path("gsd"))

    assert assistant.gsd_plan("Plan the next milestone") == "ok"
    assert seen["timeout"] >= 600
