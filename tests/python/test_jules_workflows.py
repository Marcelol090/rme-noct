from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]

AREA_SCHEDULES = {
    "0 0 * * 1": "python",
    "0 1 * * 1": "rust",
    "0 2 * * 1": "bridge",
    "0 3 * * 1": "review",
    "0 4 * * 1": "test",
    "0 10 * * 1": "utility",
    "0 11 * * 1": "system",
    "0 12 * * 1": "uiux",
    "0 13 * * 1": "maintenance",
}


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

    assert {"ci", "maintenance", "uiux", "test", "system"}.issubset(
        set(_workflow_dispatch_options(workflow))
    )

    script = workflow["jobs"]["invoke"]["steps"][1]["run"]
    assert "ci) prompt_file='.jules/newagents/ci.md' ;;" in script
    assert "maintenance) prompt_file='.jules/newagents/maintenance.md' ;;" in script
    assert "uiux) prompt_file='.jules/newagents/uiux.md' ;;" in script
    assert "system) prompt_file='.jules/newagents/system.md' ;;" in script
    assert "test) prompt_file='.jules/newagents/test.md' ;;" in script


def test_jules_area_schedule_covers_every_lane_with_five_hour_pause() -> None:
    workflow = _workflow("jules-schedule.yml")

    crons = [entry["cron"] for entry in _on(workflow)["schedule"]]
    assert crons == list(AREA_SCHEDULES)

    hours = [int(cron.split()[1]) for cron in crons]
    assert hours[:5] == [0, 1, 2, 3, 4]
    assert hours[5] == 10

    script = workflow["jobs"]["prepare"]["steps"][0]["run"]
    for cron, focus in AREA_SCHEDULES.items():
        assert f'"{cron}") focus="{focus}" ;;' in script

    invoke = workflow["jobs"]["invoke"]
    assert invoke["uses"] == "./.github/workflows/jules-invoke.yml"
    assert invoke["secrets"] == "inherit"
    assert invoke["with"]["focus"] == "${{ needs.prepare.outputs.focus }}"


def test_focused_lane_wrappers_leave_periodic_runs_to_area_scheduler() -> None:
    for workflow_name in (
        "jules-maintenance.yml",
        "jules-system.yml",
        "jules-test.yml",
    ):
        workflow = _workflow(workflow_name)
        assert "schedule" not in _on(workflow)


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
    for name in ("ci", "maintenance", "uiux", "system"):
        path = ROOT / ".jules" / "newagents" / f"{name}.md"
        text = path.read_text(encoding="utf-8")

        assert "AUTONOMOUS AGENT" in text
        assert "Task Context" in text
