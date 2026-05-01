# Jules Workflow Matrix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add tested Jules focus routing plus weekly scheduled area coverage for Python, Rust, bridge, review, test, utility, system, UI/UX, and maintenance lanes.

**Architecture:** Keep `.github/workflows/jules-invoke.yml` as the shared runner. Add focused `.jules/newagents/*` contracts, thin manual wrapper workflows, and one central scheduled workflow that maps `github.event.schedule` to area focus values.

**Tech Stack:** GitHub Actions YAML, `actions/github-script`, `google-labs-code/jules-invoke@v1`, Python pytest contract tests with PyYAML.

---

### Task 1: Workflow Contract Tests

**Files:**
- Create: `tests/python/test_jules_workflows.py`

- [ ] **Step 1: Write failing tests**

```python
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _workflow(name: str) -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"))


def test_jules_dispatch_accepts_uiux_test_and_system_focuses() -> None:
    workflow = _workflow("jules-dispatch.yml")
    options = workflow["on"]["workflow_dispatch"]["inputs"]["focus"]["options"]
    assert {"uiux", "test", "system"}.issubset(set(options))

    script = workflow["jobs"]["prepare"]["steps"][0]["with"]["script"]
    match = re.search(r"auto\|python\|rust\|bridge\|review\|test\|utility\|maintenance\|ci\|uiux\|system", script)
    assert match is not None


def test_jules_invoke_routes_new_focuses_to_agents() -> None:
    workflow = _workflow("jules-invoke.yml")
    options = workflow["on"]["workflow_dispatch"]["inputs"]["focus"]["options"]
    assert {"uiux", "test", "system"}.issubset(set(options))

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
```

- [ ] **Step 2: Run RED**

Run:

```bash
python3 -m pytest tests/python/test_jules_workflows.py -q --tb=short
```

Expected: FAIL because `test_jules_workflows.py` or new workflows/agents are missing.

### Task 2: Add Focus Routing and Agents

**Files:**
- Modify: `.github/workflows/jules-invoke.yml`
- Modify: `.github/workflows/jules-dispatch.yml`
- Create: `.jules/newagents/uiux.md`
- Create: `.jules/newagents/system.md`
- Create: `.jules/newagents/maintenance.md`
- Create: `.jules/newagents/ci.md`

- [ ] **Step 1: Add focuses to workflow choices**

Add `uiux` and `system` to focus option lists in both workflows. Keep existing `test`, `maintenance`, and `ci` choices.

- [ ] **Step 2: Add prompt routing**

Add these cases in `jules-invoke.yml`:

```bash
uiux) prompt_file='.jules/newagents/uiux.md' ;;
system) prompt_file='.jules/newagents/system.md' ;;
maintenance) prompt_file='.jules/newagents/maintenance.md' ;;
ci) prompt_file='.jules/newagents/ci.md' ;;
```

- [ ] **Step 3: Add focused agent docs**

Create `.jules/newagents/uiux.md`, `.jules/newagents/system.md`, `.jules/newagents/maintenance.md`, and `.jules/newagents/ci.md` with autonomous process, rules, verification, and PR contract sections.

### Task 3: Add Wrapper Workflows

**Files:**
- Create: `.github/workflows/jules-uiux.yml`
- Create: `.github/workflows/jules-test.yml`
- Create: `.github/workflows/jules-system.yml`
- Create: `.github/workflows/jules-schedule.yml`
- Modify: `.github/workflows/jules-maintenance.yml`

- [ ] **Step 1: Create reusable wrappers**

Each workflow calls `./.github/workflows/jules-invoke.yml`, passes `secrets: inherit`, and sets fixed `focus` to its own lane.

- [ ] **Step 2: Add schedules**

Schedule all periodic area lanes in `jules-schedule.yml` with the first five hourly lanes followed by a five-hour pause. Keep focused wrapper workflows manual-only so schedule runs are not duplicated.

### Task 4: Docs and Verification

**Files:**
- Modify: `.github/workflows/README.md`
- Modify: `README.md`

- [ ] **Step 1: Document workflows and comment triggers**

Add `Jules UI/UX`, `Jules Test`, and `Jules System` to workflow tables and examples.

- [ ] **Step 2: Run GREEN**

Run:

```bash
python3 -m pytest tests/python/test_jules_workflows.py -q --tb=short
npm run preflight --silent
python3 -m pytest tests/python/test_codex_agents.py tests/python/test_codex_stack_report.py tests/python/test_jules_workflows.py -q --tb=short
```

Expected: all pass.
