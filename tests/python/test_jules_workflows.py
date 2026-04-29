from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _workflow(name: str) -> dict[str, Any]:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
    )
    assert isinstance(workflow, dict)
    return workflow


def _on(workflow: dict[str, Any]) -> dict[str, Any]:
    # PyYAML 1.1 resolves "on" as True unless quoted.
    value = workflow.get("on", workflow.get(True))
    assert isinstance(value, dict)
    return value


def _workflow_dispatch_options(workflow: dict[str, Any]) -> list[str]:
    focus = _on(workflow)["workflow_dispatch"]["inputs"]["focus"]
    options = focus["options"]
    assert isinstance(options, list)
    return [str(option) for option in options]


def test_jules_dispatch_accepts_uiux_test_and_system_focuses() -> None:
    workflow = _workflow("jules-dispatch.yml")

    assert {"uiux", "test", "system"}.issubset(
        set(_workflow_dispatch_options(workflow))
    )

    script = workflow["jobs"]["prepare"]["steps"][0]["with"]["script"]
    assert re.search(
        r"auto\|python\|rust\|bridge\|review\|test\|utility\|maintenance\|ci\|uiux\|system",
        script,
    )


def test_jules_invoke_routes_new_focuses_to_agents() -> None:
    workflow = _workflow("jules-invoke.yml")

    assert {"uiux", "test", "system"}.issubset(
        set(_workflow_dispatch_options(workflow))
    )

    script = workflow["jobs"]["invoke"]["steps"][1]["run"]
    assert "uiux) prompt_file='.jules/newagents/uiux.md' ;;" in script
    assert "system) prompt_file='.jules/newagents/system.md' ;;" in script
    assert "test) prompt_file='.jules/newagents/test.md' ;;" in script


def test_focused_jules_workflows_call_reusable_invoke() -> None:
    expected = {
        "jules-uiux.yml": "uiux",
        "jules-test.yml": "test",
        "jules-system.yml": "system",
    }

    for workflow_name, focus in expected.items():
        workflow = _workflow(workflow_name)
        invoke = workflow["jobs"]["invoke"]

        assert invoke["uses"] == "./.github/workflows/jules-invoke.yml"
        assert invoke["secrets"] == "inherit"
        assert invoke["with"]["focus"] == focus
        assert "starting_branch" in invoke["with"]
        assert "additional_context" in invoke["with"]


def test_new_jules_agent_contracts_exist() -> None:
    for name in ("uiux", "system"):
        path = ROOT / ".jules" / "newagents" / f"{name}.md"
        text = path.read_text(encoding="utf-8")

        assert "AUTONOMOUS AGENT" in text
        assert "Task Context" in text
