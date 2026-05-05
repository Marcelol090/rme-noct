# M034 Tool Selection UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Drawing Tools toolbar expose real exclusive editor-mode actions for Select, Draw, Erase, Fill, and Move.

**Architecture:** Keep mode ownership in `MainWindow`. Replace inert toolbar actions with shared `brush_mode_actions` entries created from one explicit mode list, then reuse the existing `_set_editor_mode()`, `_normalized_editor_mode()`, `_mode_label_for()`, `_sync_canvas_shell_state()`, and `_ToolOptionsDock` seams.

**Tech Stack:** Python 3.12-compatible code, PyQt6 QAction/QActionGroup/QToolBar, pytest-qt, ruff, rtk.

---

## Context

Design source: `docs/superpowers/specs/2026-05-05-m034-tool-selection-ui-design.md`

Issue source: https://github.com/Marcelol090/rme-noct/issues/72

Context7 PyQt6 notes used for this plan:

- `QAction.triggered(checked: bool = False)` fires when a user activates an action or `trigger()` is called. It does not fire when `setChecked()` is called.
- `QActionGroup.setExclusive(True)` keeps checkable actions mutually exclusive.
- `QActionGroup.triggered(QAction)` can route group activation, but this plan keeps the existing per-action `triggered` lambda to minimize change.
- `QToolBar.addAction(QAction)` appends an existing action to the toolbar.

## Files

- Modify: `pyrme/ui/main_window.py`
- Modify: `tests/python/test_main_window_commands_m5.py`
- Modify: `tests/python/test_canvas_seam_m4.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M034-tool-selection-ui/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M034-tool-selection-ui/slices/S01/S01-SUMMARY.md`

## Task 1: Toolbar Mode Actions

**Files:**
- Modify: `tests/python/test_main_window_commands_m5.py`
- Modify: `pyrme/ui/main_window.py`

- [ ] **Step 1: Write failing toolbar action tests**

Add this test near `test_main_window_brush_mode_toolbar_updates_session_and_tool_options` in `tests/python/test_main_window_commands_m5.py`:

```python
@pytest.mark.parametrize(
    ("mode", "label"),
    [
        ("selection", "Select"),
        ("drawing", "Draw"),
        ("erasing", "Erase"),
        ("fill", "Fill"),
        ("move", "Move"),
    ],
)
def test_main_window_drawing_toolbar_exposes_all_editor_modes(
    qtbot,
    settings_workspace: Path,
    mode: str,
    label: str,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, f"mode-{mode}.ini"))
    qtbot.addWidget(window)

    assert set(window.brush_mode_actions) == {
        "selection",
        "drawing",
        "erasing",
        "fill",
        "move",
    }
    assert window.drawing_toolbar is not None
    assert window.brush_mode_actions[mode].isCheckable() is True

    if mode == "drawing":
        window.brush_mode_actions["selection"].trigger()
    window.brush_mode_actions[mode].trigger()

    assert window._editor_context.session.mode == mode
    assert window.brush_mode_actions[mode].isChecked() is True
    for other_mode, action in window.brush_mode_actions.items():
        if other_mode != mode:
            assert action.isChecked() is False
    assert window.tool_options_dock is not None
    assert window.tool_options_dock._mode_label.text() == label
    assert _status_message(window) == f"Editor mode: {label}."
```

Add this toolbar-order test after the parameterized test:

```python
def test_main_window_drawing_toolbar_orders_tool_modes(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, "mode-order.ini"))
    qtbot.addWidget(window)

    assert window.drawing_toolbar is not None
    labels = [
        "|" if action.isSeparator() else action.text()
        for action in window.drawing_toolbar.actions()
    ]

    assert labels[:6] == ["Select", "Draw", "Erase", "Fill", "|", "Move"]
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py::test_main_window_drawing_toolbar_exposes_all_editor_modes tests/python/test_main_window_commands_m5.py::test_main_window_drawing_toolbar_orders_tool_modes -q --tb=short
```

Expected:

- parameterized test fails because `erasing`, `fill`, and `move` are missing from `brush_mode_actions`;
- toolbar order test fails because current Erase/Fill/Move actions are inert actions not the shared mode actions.

- [ ] **Step 3: Implement shared mode action list**

In `pyrme/ui/main_window.py`, add this constant near other module constants:

```python
EDITOR_MODE_ACTIONS: tuple[tuple[str, str], ...] = (
    ("selection", "Select"),
    ("drawing", "Draw"),
    ("erasing", "Erase"),
    ("fill", "Fill"),
    ("move", "Move"),
)
```

In `MainWindow.__init__`, add explicit group ownership near the existing toolbar fields:

```python
self._brush_mode_group: QActionGroup | None = None
```

Replace the current mode action creation block in `_setup_menu_bar()` with:

```python
self.brush_mode_actions: dict[str, QAction] = {}
self._brush_mode_group = QActionGroup(self)
self._brush_mode_group.setExclusive(True)
for mode, label in EDITOR_MODE_ACTIONS:
    action = self._action(label)
    action.setCheckable(True)
    action.triggered.connect(
        lambda checked, value=mode: self._set_editor_mode(value)
        if checked
        else None
    )
    self._brush_mode_group.addAction(action)
    self.brush_mode_actions[mode] = action
self.brush_mode_actions["drawing"].setChecked(True)
```

Replace the Drawing Tools toolbar action block in `_setup_toolbars()` with:

```python
for mode in ("selection", "drawing", "erasing", "fill"):
    self.drawing_toolbar.addAction(self.brush_mode_actions[mode])
self.drawing_toolbar.addSeparator()
self.drawing_toolbar.addAction(self.brush_mode_actions["move"])
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py::test_main_window_drawing_toolbar_exposes_all_editor_modes tests/python/test_main_window_commands_m5.py::test_main_window_drawing_toolbar_orders_tool_modes -q --tb=short
```

Expected: all new toolbar tests pass.

## Task 2: Canvas Mode Sync

**Files:**
- Modify: `tests/python/test_canvas_seam_m4.py`
- Verify: `pyrme/ui/main_window.py`

- [ ] **Step 1: Write failing canvas sync tests**

Add this test near `test_main_window_brush_mode_selection_updates_canvas_activation` in `tests/python/test_canvas_seam_m4.py`:

```python
def test_main_window_extended_tool_modes_update_canvas_activation(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-extended-modes")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-extended-modes.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        for mode in ("erasing", "fill", "move"):
            window.brush_mode_actions[mode].trigger()
            assert window._editor_context.session.mode == mode
            assert holder["canvas"].editor_mode == mode
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_seam_m4.py::test_main_window_extended_tool_modes_update_canvas_activation -q --tb=short
```

Expected: fails before Task 1 implementation because `brush_mode_actions["erasing"]` does not exist.

- [ ] **Step 3: Verify implementation seam**

No extra production change should be needed after Task 1. `_set_editor_mode()` already normalizes the mode, sets `EditorContext.session.mode`, calls `self._canvas.set_editor_mode(...)` when the canvas supports the activation protocol, updates `_ToolOptionsDock`, and writes status text.

If the test fails after Task 1, inspect only:

- `MainWindow._set_editor_mode()`
- `MainWindow._normalized_editor_mode()`
- `implements_editor_activation_canvas_protocol()`
- `_FakeCanvasWidget.set_editor_mode()`

Do not change renderer, minimap, Search menu, or backend map mutation.

- [ ] **Step 4: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_seam_m4.py::test_main_window_extended_tool_modes_update_canvas_activation -q --tb=short
```

Expected: test passes.

## Task 3: Focused Regression Bundle

**Files:**
- Verify: `tests/python/test_main_window_commands_m5.py`
- Verify: `tests/python/test_canvas_seam_m4.py`
- Verify: `tests/python/test_main_window_new_view.py`
- Verify: `tests/python/test_editor_activation_backend.py`

- [ ] **Step 1: Run focused pytest bundle**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_new_view.py tests/python/test_editor_activation_backend.py -q --tb=short
```

Expected: all tests pass.

- [ ] **Step 2: Preserve backend no-op contract**

Confirm `tests/python/test_editor_activation_backend.py::test_editor_backend_tool_noops_when_operation_is_not_supported` still passes in the focused bundle. This proves `fill` and `move` remain selectable modes without new map mutation behavior.

## Task 4: Closeout Docs and Verification

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M034-tool-selection-ui/M034-tool-selection-ui-META.json`
- Modify: `.gsd/milestones/M034-tool-selection-ui/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M034-tool-selection-ui/slices/S01/S01-SUMMARY.md`

- [ ] **Step 1: Mark S01 tasks complete after tests pass**

Update `.gsd/milestones/M034-tool-selection-ui/slices/S01/S01-PLAN.md`:

```markdown
- [x] T01: Write implementation plan after design review.
- [x] T02: Execute TDD implementation.
- [x] T03: Closeout docs, caveman-review, and verification.
```

- [ ] **Step 2: Update milestone meta**

Set `.gsd/milestones/M034-tool-selection-ui/M034-tool-selection-ui-META.json` status to:

```json
"status": "review"
```

- [ ] **Step 3: Write S01 summary**

Create `.gsd/milestones/M034-tool-selection-ui/slices/S01/S01-SUMMARY.md`:

```markdown
# S01 Summary - Tool Selection UI

## Done

- Converted Drawing Tools toolbar into real exclusive Select/Draw/Erase/Fill/Move mode actions.
- Kept Tool Options label synchronized with active editor mode.
- Kept canvas activation synchronized through `set_editor_mode()`.
- Preserved Fill/Move backend no-op behavior.
- Kept renderer, minimap, Search menu, PyO3, and new map mutation out of scope.

## Verification

- Record focused pytest command and pass count.
- Record ruff command and `All checks passed!`.
- Record `git diff --check` exit 0.
- Record `rtk npm run preflight --silent` result.
```

- [ ] **Step 4: Update GSD state**

Update `.gsd/STATE.md`:

```markdown
**Active Milestone:** M034-tool-selection-ui
**Active Slice:** S01-TOOL-SELECTION-UI
**Active Task:** none
**Phase:** review
**Next Action:** Run caveman-review on M034/S01 diff, then commit and PR after clean review.
```

Add recent decision:

```markdown
- `M034/S01-TOOL-SELECTION-UI` is implemented: Drawing Tools toolbar now exposes Select/Draw/Erase/Fill/Move as real exclusive mode actions while Fill/Move remain no-op backend modes for later slices.
```

- [ ] **Step 5: Run final verification**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_new_view.py tests/python/test_editor_activation_backend.py -q --tb=short
PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/main_window.py tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py
git diff --check
PATH="/home/marcelo/.local/bin:$PATH" rtk npm run preflight --silent
```

Expected:

- focused pytest passes;
- ruff prints `All checks passed!`;
- `git diff --check` exits 0;
- preflight prints `Validation: ok`.

- [ ] **Step 6: caveman-review before commit**

Review final diff. Required clean result:

- no renderer diff;
- no minimap diff;
- no Search menu diff;
- no PyO3/Rust diff;
- no new Fill/Move map mutation behavior.

If clean, commit:

```bash
git add -- pyrme/ui/main_window.py tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py .gsd/STATE.md .gsd/milestones/M034-tool-selection-ui/M034-tool-selection-ui-META.json .gsd/milestones/M034-tool-selection-ui/slices/S01/S01-PLAN.md .gsd/milestones/M034-tool-selection-ui/slices/S01/S01-SUMMARY.md
git commit -m "feat(M034/S01): wire tool selection modes"
```
