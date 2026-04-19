# GSD Node 22 Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `npm run gsd:*` reproducible in this repository by aligning the project to Node 22 and documenting the local installation path clearly.

**Architecture:** Keep the existing repo-level `package.json` entrypoint for GSD, but make the runtime contract explicit and enforceable. Align setup docs, setup script checks, and Python-side helper messaging to the same Node 22 + local install expectation.

**Tech Stack:** Node.js 22, npm, Python pytest, PyRME devtools

---

### Task 1: Lock the GSD runtime contract with tests

**Files:**
- Create: `tests/python/test_gsd_project_contract.py`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_package_json_requires_node_22_for_gsd() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert package["engines"]["node"] == ">=22.0.0"
    assert package["devDependencies"]["gsd-pi"] == "2.64.0"
    assert package["scripts"]["gsd"] == "gsd-pi"
    assert package["scripts"]["gsd:auto"] == "gsd-pi auto"
    assert package["scripts"]["gsd:plan"] == "gsd-pi plan"
    assert package["scripts"]["gsd:status"] == "gsd-pi status"


def test_setup_script_and_readme_match_node_22_contract() -> None:
    setup_script = (ROOT / "scripts" / "setup-devtools.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Node.js 22+" in setup_script
    assert "Node.js 22+" in readme
    assert "npm install --silent" in setup_script
    assert "npm run gsd:auto" in readme
```

- [ ] **Step 2: Run test to verify it fails**

Run: `env PYTHONPATH=. pytest tests/python/test_gsd_project_contract.py -v --tb=short`
Expected: FAIL because `package.json`, `README.md`, and `scripts/setup-devtools.sh` still describe Node 18+/20-compatible behavior and `npx gsd-pi`.

- [ ] **Step 3: Write minimal implementation**

```text
Update package.json to require Node >=22.0.0, pin gsd-pi 2.64.0, and call the local binary directly in npm scripts.
Update scripts/setup-devtools.sh and README.md to require Node 22+ and document the local install workflow.
Update pyrme/tools/ai_assistant.py error/help text so it points to repo-local npm installation instead of ad-hoc npx usage.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `env PYTHONPATH=. pytest tests/python/test_gsd_project_contract.py -v --tb=short`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-04-06-gsd-node22-alignment.md tests/python/test_gsd_project_contract.py package.json README.md scripts/setup-devtools.sh pyrme/tools/ai_assistant.py
git commit -m "build: align gsd runtime to node 22"
```

### Task 2: Verify the repo-level GSD entrypoint behavior

**Files:**
- Modify: `README.md`
- Modify: `package.json`

- [ ] **Step 1: Write the failing test**

```python
def test_readme_documents_local_gsd_commands() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "npm install" in readme
    assert "npm run gsd:auto" in readme
```

- [ ] **Step 2: Run test to verify it fails**

Run: `env PYTHONPATH=. pytest tests/python/test_gsd_project_contract.py::test_readme_documents_local_gsd_commands -v --tb=short`
Expected: FAIL if the README does not describe the local installation precondition clearly enough.

- [ ] **Step 3: Write minimal implementation**

```text
Add a short README note that GSD is installed as a local dev dependency and requires Node 22+ before `npm run gsd:*` commands will work.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `env PYTHONPATH=. pytest tests/python/test_gsd_project_contract.py::test_readme_documents_local_gsd_commands -v --tb=short`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md tests/python/test_gsd_project_contract.py
git commit -m "docs: clarify local gsd usage"
```
