# M035 Ground and Wall Brushes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make selected default ground and wall catalog brushes mutate the Python map model through the active Draw tool.

**Architecture:** Move the shared starter brush placement data into a pure editor module, then let the UI catalog view model derive its visible rows from that data. Keep `EditorModel.apply_active_tool_at()` as the only map-mutation owner, with ground brushes replacing ground and wall brushes adding one wall item once.

**Tech Stack:** Python 3.12-compatible code, dataclasses, pytest, pytest-qt, ruff, rtk.

---

## Context

Design source: `docs/superpowers/specs/2026-05-05-m035-ground-wall-brushes-design.md`

Issue source: https://github.com/Marcelol090/rme-noct/issues/72

Legacy evidence:

- `remeres-map-editor-redux/source/brushes/ground/ground_brush.cpp`: `GroundBrush::draw()` chooses a brush item and places it on the tile.
- `remeres-map-editor-redux/source/brushes/wall/wall_brush.cpp`: `WallBrush::draw()` adds a wall item first; wall-border logic reshapes it later.

Scope guards:

- No renderer changes.
- No minimap changes.
- No Search menu changes.
- No XML brush loader.
- No autoborder mutation.
- No wall alignment recalculation.
- No PyO3/Rust export changes.

## Files

- Create: `pyrme/editor/brushes.py`
- Modify: `pyrme/editor/model.py`
- Modify: `pyrme/ui/models/brush_catalog.py`
- Modify: `tests/python/test_editor_activation_backend.py`
- Modify: `tests/python/test_brush_catalog_ui_bridge.py`
- Modify: `tests/python/test_canvas_seam_m4.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M035-ground-wall-brushes/M035-ground-wall-brushes-META.json`
- Modify: `.gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-SUMMARY.md`

## Task 1: Shared Brush Placement Catalog

**Files:**
- Create: `pyrme/editor/brushes.py`
- Modify: `pyrme/ui/models/brush_catalog.py`
- Modify: `tests/python/test_brush_catalog_ui_bridge.py`

- [ ] **Step 1: Write failing shared-catalog tests**

Add imports to `tests/python/test_brush_catalog_ui_bridge.py`:

```python
from pyrme.editor.brushes import (
    BrushPlacementKind,
    brush_placement_for_active_id,
    default_editor_brush_placements,
)
```

Add these tests after `test_brush_palette_entry_active_id_and_search_text`:

```python
def test_default_editor_brush_placements_match_visible_catalog_entries() -> None:
    placements = default_editor_brush_placements()
    entries = default_brush_palette_entries()

    assert [placement.active_brush_id for placement in placements] == [
        entry.active_brush_id for entry in entries
    ]
    assert [placement.item_id for placement in placements] == [
        entry.look_id for entry in entries
    ]


def test_brush_placement_for_active_id_resolves_default_ground_and_wall() -> None:
    grass = brush_placement_for_active_id("brush:ground:10")
    stone_wall = brush_placement_for_active_id("brush:wall:20")

    assert grass is not None
    assert grass.kind is BrushPlacementKind.GROUND
    assert grass.item_id == 4526
    assert stone_wall is not None
    assert stone_wall.kind is BrushPlacementKind.WALL
    assert stone_wall.item_id == 3361
    assert brush_placement_for_active_id("brush:ground:999") is None
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py::test_default_editor_brush_placements_match_visible_catalog_entries tests/python/test_brush_catalog_ui_bridge.py::test_brush_placement_for_active_id_resolves_default_ground_and_wall -q --tb=short
```

Expected: import fails with `ModuleNotFoundError: No module named 'pyrme.editor.brushes'`.

- [ ] **Step 3: Create pure editor brush placement module**

Create `pyrme/editor/brushes.py`:

```python
"""Pure editor brush placement data shared by UI and backend seams."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BrushPlacementKind(StrEnum):
    GROUND = "ground"
    WALL = "wall"


@dataclass(frozen=True, slots=True)
class EditorBrushPlacement:
    brush_id: int
    name: str
    kind: BrushPlacementKind
    palette_name: str
    item_id: int
    related_item_ids: tuple[int, ...]
    visible_in_palette: bool = True

    @property
    def active_brush_id(self) -> str:
        return f"brush:{self.kind.value}:{self.brush_id}"


def default_editor_brush_placements() -> tuple[EditorBrushPlacement, ...]:
    """Return starter brush placements mirrored from the Rust brush contract."""
    return (
        EditorBrushPlacement(
            10,
            "grass",
            BrushPlacementKind.GROUND,
            "Terrain",
            4526,
            (4526, 4527),
        ),
        EditorBrushPlacement(
            11,
            "dirt",
            BrushPlacementKind.GROUND,
            "Terrain",
            103,
            (103,),
        ),
        EditorBrushPlacement(
            20,
            "stone wall",
            BrushPlacementKind.WALL,
            "Terrain",
            3361,
            (3361, 3362),
        ),
        EditorBrushPlacement(
            21,
            "wooden wall",
            BrushPlacementKind.WALL,
            "Terrain",
            3390,
            (3390,),
        ),
    )


def brush_placement_for_active_id(
    active_brush_id: str | None,
) -> EditorBrushPlacement | None:
    if active_brush_id is None:
        return None
    return next(
        (
            placement
            for placement in default_editor_brush_placements()
            if placement.active_brush_id == active_brush_id
        ),
        None,
    )
```

- [ ] **Step 4: Derive UI catalog entries from editor placements**

In `pyrme/ui/models/brush_catalog.py`, add this import:

```python
from pyrme.editor.brushes import default_editor_brush_placements
```

Replace `default_brush_palette_entries()` with:

```python
def default_brush_palette_entries() -> tuple[BrushPaletteEntry, ...]:
    """Return visible starter brush entries mirrored from the editor brush catalog."""
    return tuple(
        BrushPaletteEntry(
            brush_id=placement.brush_id,
            name=placement.name,
            kind=placement.kind.value,
            palette_name=placement.palette_name,
            look_id=placement.item_id,
            related_item_ids=placement.related_item_ids,
            visible_in_palette=placement.visible_in_palette,
        )
        for placement in default_editor_brush_placements()
    )
```

- [ ] **Step 5: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py::test_default_editor_brush_placements_match_visible_catalog_entries tests/python/test_brush_catalog_ui_bridge.py::test_brush_placement_for_active_id_resolves_default_ground_and_wall -q --tb=short
```

Expected: 2 passed.

## Task 2: Backend Apply for Ground and Wall Brushes

**Files:**
- Modify: `pyrme/editor/model.py`
- Modify: `tests/python/test_editor_activation_backend.py`

- [ ] **Step 1: Write failing backend tests**

Add this import to `tests/python/test_editor_activation_backend.py`:

```python
from pyrme.editor.brushes import brush_placement_for_active_id
```

Add these tests after `test_editor_backend_drawing_tool_preserves_existing_item_stack`:

```python
def test_editor_backend_ground_catalog_brush_sets_ground_and_preserves_stack() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.map_model.set_tile(
        TileState(position=position, ground_item_id=100, item_ids=(200, 300))
    )
    editor.map_model.clear_changed()

    editor.set_mode("drawing")
    editor.active_brush_id = "brush:ground:10"

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=4526,
        item_ids=(200, 300),
    )


def test_editor_backend_wall_catalog_brush_appends_wall_item_once() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.map_model.set_tile(TileState(position=position, ground_item_id=4526))
    editor.map_model.clear_changed()

    editor.set_mode("drawing")
    editor.active_brush_id = "brush:wall:20"

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=4526,
        item_ids=(3361,),
    )
    assert editor.apply_active_tool_at(position) is False
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=4526,
        item_ids=(3361,),
    )


def test_editor_backend_unknown_catalog_brush_noops() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)

    editor.set_mode("drawing")
    editor.active_brush_id = "brush:ground:999"

    assert brush_placement_for_active_id(editor.active_brush_id) is None
    assert editor.apply_active_tool_at(position) is False
    assert editor.map_model.get_tile(position) is None
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_editor_activation_backend.py::test_editor_backend_ground_catalog_brush_sets_ground_and_preserves_stack tests/python/test_editor_activation_backend.py::test_editor_backend_wall_catalog_brush_appends_wall_item_once tests/python/test_editor_activation_backend.py::test_editor_backend_unknown_catalog_brush_noops -q --tb=short
```

Expected: ground and wall tests fail because `EditorModel.apply_active_tool_at()` returns `False` for catalog brush ids.

- [ ] **Step 3: Add backend placement branch**

In `pyrme/editor/model.py`, add this import:

```python
from pyrme.editor.brushes import BrushPlacementKind, brush_placement_for_active_id
```

Replace the `if self.mode == "drawing":` block in `EditorModel.apply_active_tool_at()` with:

```python
        if self.mode == "drawing":
            existing = self.map_model.get_tile(position)
            if self.active_item_id is not None:
                next_tile = TileState(
                    position=position,
                    ground_item_id=self.active_item_id,
                    item_ids=existing.item_ids if existing is not None else (),
                )
            elif (
                placement := brush_placement_for_active_id(self.active_brush_id)
            ) is not None:
                if placement.kind is BrushPlacementKind.GROUND:
                    next_tile = TileState(
                        position=position,
                        ground_item_id=placement.item_id,
                        item_ids=existing.item_ids if existing is not None else (),
                    )
                else:
                    existing_items = existing.item_ids if existing is not None else ()
                    if placement.item_id in existing_items:
                        return False
                    next_tile = TileState(
                        position=position,
                        ground_item_id=(
                            existing.ground_item_id if existing is not None else None
                        ),
                        item_ids=(*existing_items, placement.item_id),
                    )
            else:
                return False
            if existing == next_tile:
                return False
            self._apply_changes(
                (TileEditChange(position=position, before=existing, after=next_tile),)
            )
            return True
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_editor_activation_backend.py::test_editor_backend_ground_catalog_brush_sets_ground_and_preserves_stack tests/python/test_editor_activation_backend.py::test_editor_backend_wall_catalog_brush_appends_wall_item_once tests/python/test_editor_activation_backend.py::test_editor_backend_unknown_catalog_brush_noops -q --tb=short
```

Expected: 3 passed.

## Task 3: Canvas-Driven Brush Apply

**Files:**
- Modify: `tests/python/test_canvas_seam_m4.py`
- Verify: `pyrme/ui/main_window.py`

- [ ] **Step 1: Write failing canvas apply tests**

Add this import to `tests/python/test_canvas_seam_m4.py`:

```python
from pyrme.ui.models.brush_catalog import default_brush_palette_entries
```

Add this helper near `_build_settings()`:

```python
def _brush_entry(name: str):
    return next(entry for entry in default_brush_palette_entries() if entry.name == name)
```

Add these tests after `test_main_window_apply_active_tool_uses_canvas_seam_and_marks_view_dirty`:

```python
def test_main_window_apply_ground_catalog_brush_uses_canvas_seam(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-ground-brush")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-ground-brush.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        window._handle_brush_palette_selection(_brush_entry("grass"))
        changed = window._apply_active_tool_at_cursor()

        assert changed is True
        assert holder["canvas"].apply_count == 1
        assert window._editor_context.session.document.is_dirty is True
        assert window._editor_context.session.editor.map_model.get_tile(
            MapPosition(32000, 32000, 7)
        ) == TileState(position=MapPosition(32000, 32000, 7), ground_item_id=4526)
        assert window.statusBar().currentMessage() == "Applied Draw tool at 32000, 32000, 07."
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_apply_wall_catalog_brush_uses_canvas_seam(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-wall-brush")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-wall-brush.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)
        window._editor_context.session.editor.map_model.set_tile(
            TileState(position=MapPosition(32000, 32000, 7), ground_item_id=4526)
        )
        window._editor_context.session.editor.map_model.clear_changed()

        window._handle_brush_palette_selection(_brush_entry("stone wall"))
        changed = window._apply_active_tool_at_cursor()

        assert changed is True
        assert holder["canvas"].apply_count == 1
        assert window._editor_context.session.document.is_dirty is True
        assert window._editor_context.session.editor.map_model.get_tile(
            MapPosition(32000, 32000, 7)
        ) == TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=4526,
            item_ids=(3361,),
        )
        assert window.statusBar().currentMessage() == "Applied Draw tool at 32000, 32000, 07."
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_seam_m4.py::test_main_window_apply_ground_catalog_brush_uses_canvas_seam tests/python/test_canvas_seam_m4.py::test_main_window_apply_wall_catalog_brush_uses_canvas_seam -q --tb=short
```

Expected: both tests fail before Task 2 backend implementation because catalog brush apply returns `False`.

- [ ] **Step 3: Verify no `MainWindow` change is needed**

No production change should be needed in `pyrme/ui/main_window.py`. `_handle_brush_palette_selection()` already stores `entry.active_brush_id`; `_apply_active_tool_at_cursor()` already calls `EditorModel.apply_active_tool_at()` through the canvas seam and marks the document dirty when the result changes.

If either test fails after Task 2, inspect only:

- `MainWindow._handle_brush_palette_selection()`
- `MainWindow._apply_active_tool_at_cursor()`
- `_FakeCanvasWidget.apply_active_tool()`
- `EditorModel.apply_active_tool_at()`

Do not change renderer, minimap, Search menu, XML loading, PyO3/Rust export, or autoborder mutation.

- [ ] **Step 4: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_seam_m4.py::test_main_window_apply_ground_catalog_brush_uses_canvas_seam tests/python/test_canvas_seam_m4.py::test_main_window_apply_wall_catalog_brush_uses_canvas_seam -q --tb=short
```

Expected: 2 passed.

## Task 4: Focused Regression Bundle

**Files:**
- Verify: `tests/python/test_editor_activation_backend.py`
- Verify: `tests/python/test_brush_catalog_ui_bridge.py`
- Verify: `tests/python/test_canvas_seam_m4.py`
- Verify: `tests/python/test_main_window_commands_m5.py`

- [ ] **Step 1: Run focused pytest bundle**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_editor_activation_backend.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_commands_m5.py -q --tb=short
```

Expected: all focused tests pass.

- [ ] **Step 2: Preserve no-op contracts**

Confirm `tests/python/test_editor_activation_backend.py::test_editor_backend_tool_noops_when_operation_is_not_supported` still passes in the focused bundle. This proves `fill` and `move` remain no-op backend modes.

## Task 5: Closeout Docs and Verification

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M035-ground-wall-brushes/M035-ground-wall-brushes-META.json`
- Modify: `.gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-SUMMARY.md`

- [ ] **Step 1: Mark S01 tasks complete after tests pass**

Update `.gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-PLAN.md`:

```markdown
Plan source: `docs/superpowers/plans/2026-05-05-m035-ground-wall-brushes.md`

## Tasks

- [x] T01: Write implementation plan after design review.
- [x] T02: Execute TDD implementation.
- [x] T03: Closeout docs, caveman-review, and verification.
```

- [ ] **Step 2: Update milestone meta**

Set `.gsd/milestones/M035-ground-wall-brushes/M035-ground-wall-brushes-META.json` status to:

```json
"status": "review"
```

- [ ] **Step 3: Write S01 summary**

Create `.gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-SUMMARY.md`:

```markdown
# S01 Summary - Ground and Wall Brushes

## Done

- Added shared Python editor brush placement data for default ground and wall catalog entries.
- Derived visible PyQt brush catalog rows from the shared editor placement data.
- Made `EditorModel.apply_active_tool_at()` apply selected ground and wall catalog brushes in `drawing` mode.
- Kept item brush, selection, erasing, fill, and move behavior unchanged.
- Kept renderer, minimap, Search menu, XML loading, autoborder mutation, wall alignment recalculation, and PyO3/Rust export out of scope.

## Verification

- Record focused pytest command and pass count.
- Record ruff command and `All checks passed!`.
- Record `git diff --check` exit 0.
- Record `rtk npm run preflight --silent` result.
```

- [ ] **Step 4: Update GSD state**

Update `.gsd/STATE.md`:

```markdown
**Active Milestone:** M035-ground-wall-brushes
**Active Slice:** S01-GROUND-WALL-BRUSHES
**Active Task:** none
**Phase:** review
**Next Action:** Run caveman-review on M035/S01 diff, then commit and PR after clean review.
```

Add recent decision:

```markdown
- `M035/S01-GROUND-WALL-BRUSHES` is implemented: selected default ground and wall catalog brushes now mutate the Python map model through Draw while Fill/Move and deferred autoborder behavior remain unchanged.
```

- [ ] **Step 5: Run final verification**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_editor_activation_backend.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_commands_m5.py -q --tb=short
PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/editor/brushes.py pyrme/editor/model.py pyrme/ui/models/brush_catalog.py tests/python/test_editor_activation_backend.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_canvas_seam_m4.py
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
- no XML loader diff;
- no PyO3/Rust export diff;
- no autoborder mutation or wall alignment recalculation diff.

If clean, commit:

```bash
git add -- pyrme/editor/brushes.py pyrme/editor/model.py pyrme/ui/models/brush_catalog.py tests/python/test_editor_activation_backend.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_canvas_seam_m4.py .gsd/STATE.md .gsd/milestones/M035-ground-wall-brushes/M035-ground-wall-brushes-META.json .gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-PLAN.md .gsd/milestones/M035-ground-wall-brushes/slices/S01/S01-SUMMARY.md
git commit -m "feat(M035/S01): apply ground wall brushes"
```
