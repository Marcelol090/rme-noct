# M033 Brush Catalog UI Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose real brush catalog entries in the PyQt brush palette and wire catalog brush selection into existing active brush shell state.

**Architecture:** Add a small Python view-model catalog mirroring the M029 Rust brush contract. Reuse that catalog from `BrushPaletteDock` and `FindBrushDialog`, then connect dock selection to `MainWindow` active brush state without map mutation.

**Tech Stack:** Python 3.12, PyQt6 model/view, pytest-qt, ruff, rtk, existing `EditorContext`/canvas activation seams.

---

## Files

- Create: `pyrme/ui/models/brush_catalog.py`
- Create: `tests/python/test_brush_catalog_ui_bridge.py`
- Modify: `pyrme/ui/docks/brush_palette.py`
- Modify: `pyrme/ui/dialogs/find_brush.py`
- Modify: `pyrme/ui/main_window.py`
- Modify: `tests/python/test_item_palette_integration.py`
- Modify: `tests/python/test_find_brush_tier2.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M033-brush-catalog-ui-bridge/*`

## Task 1: Catalog View Model

**Files:**
- Create: `pyrme/ui/models/brush_catalog.py`
- Test: `tests/python/test_brush_catalog_ui_bridge.py`

- [ ] **Step 1: Write failing catalog tests**

Add tests:

```python
from pyrme.ui.models.brush_catalog import (
    BrushPaletteEntry,
    default_brush_palette_entries,
    entries_by_palette,
)


def test_default_brush_catalog_has_real_ground_and_wall_entries() -> None:
    entries = default_brush_palette_entries()

    assert any(entry.name == "grass" and entry.kind == "ground" for entry in entries)
    assert any(entry.name == "stone wall" and entry.kind == "wall" for entry in entries)
    assert all(not entry.name.startswith("Terrain Brush") for entry in entries)


def test_brush_palette_entry_active_id_and_search_text() -> None:
    entry = BrushPaletteEntry(
        brush_id=10,
        name="grass",
        kind="ground",
        palette_name="Terrain",
        look_id=4526,
        related_item_ids=(4526, 4527),
    )

    assert entry.active_brush_id == "brush:ground:10"
    assert entry.search_text == "grass ground terrain 10 4526 4527"


def test_entries_by_palette_filters_visible_entries() -> None:
    grouped = entries_by_palette(
        (
            BrushPaletteEntry(1, "grass", "ground", "Terrain", 4526, (4526,)),
            BrushPaletteEntry(2, "hidden", "ground", "Terrain", 1, (1,), False),
            BrushPaletteEntry(3, "stone wall", "wall", "Terrain", 3361, (3361,)),
        )
    )

    assert [entry.name for entry in grouped["Terrain"]] == ["grass", "stone wall"]
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py -q --tb=short
```

Expected: import failure for `pyrme.ui.models.brush_catalog`.

- [ ] **Step 3: Implement catalog model**

Create `pyrme/ui/models/brush_catalog.py`:

```python
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class BrushPaletteEntry:
    brush_id: int
    name: str
    kind: str
    palette_name: str
    look_id: int
    related_item_ids: tuple[int, ...]
    visible_in_palette: bool = True

    @property
    def active_brush_id(self) -> str:
        return f"brush:{self.kind}:{self.brush_id}"

    @property
    def search_text(self) -> str:
        parts = [
            self.name,
            self.kind,
            self.palette_name,
            str(self.brush_id),
            str(self.look_id),
            *(str(item_id) for item_id in self.related_item_ids),
        ]
        return " ".join(parts).casefold()


def default_brush_palette_entries() -> tuple[BrushPaletteEntry, ...]:
    return (
        BrushPaletteEntry(10, "grass", "ground", "Terrain", 4526, (4526, 4527)),
        BrushPaletteEntry(11, "dirt", "ground", "Terrain", 103, (103,)),
        BrushPaletteEntry(20, "stone wall", "wall", "Terrain", 3361, (3361, 3362)),
        BrushPaletteEntry(21, "wooden wall", "wall", "Terrain", 3390, (3390,)),
    )


def entries_by_palette(
    entries: Iterable[BrushPaletteEntry],
) -> dict[str, tuple[BrushPaletteEntry, ...]]:
    grouped: dict[str, list[BrushPaletteEntry]] = defaultdict(list)
    for entry in entries:
        if entry.visible_in_palette:
            grouped[entry.palette_name].append(entry)
    return {name: tuple(values) for name, values in grouped.items()}
```

- [ ] **Step 4: Run GREEN**

Run same pytest command. Expected: 3 passed.

## Task 2: Brush Palette Dock Catalog Entries

**Files:**
- Modify: `pyrme/ui/docks/brush_palette.py`
- Test: `tests/python/test_brush_catalog_ui_bridge.py`
- Modify: `tests/python/test_item_palette_integration.py`

- [ ] **Step 1: Write failing dock tests**

Add tests:

```python
from PyQt6.QtCore import Qt

from pyrme.ui.docks.brush_palette import BrushPaletteDock


def _display_values(dock: BrushPaletteDock, palette: str) -> list[str]:
    proxy = dock._proxies[palette]
    return [
        proxy.data(proxy.index(row, 0), int(Qt.ItemDataRole.DisplayRole))
        for row in range(proxy.rowCount())
    ]


def test_brush_palette_uses_catalog_entries(qtbot) -> None:
    dock = BrushPaletteDock()
    qtbot.addWidget(dock)

    values = _display_values(dock, "Terrain")

    assert "grass" in values
    assert "stone wall" in values
    assert all(not value.startswith("Terrain Brush") for value in values)


def test_brush_palette_search_filters_catalog_entries(qtbot) -> None:
    dock = BrushPaletteDock()
    qtbot.addWidget(dock)
    dock.select_palette("Terrain")

    dock._search_bar.setText("wall")

    assert _display_values(dock, "Terrain") == ["stone wall", "wooden wall"]


def test_brush_palette_emits_selected_catalog_brush(qtbot) -> None:
    dock = BrushPaletteDock()
    qtbot.addWidget(dock)
    selected = []
    dock.brush_selected.connect(selected.append)

    dock.select_palette("Terrain")
    view = dock._views["Terrain"]
    view.clicked.emit(view.model().index(0, 0))

    assert selected
    assert selected[0].active_brush_id == "brush:ground:10"
```

Update existing item palette integration assertion so Terrain still works by expecting `"grass"` in Terrain values.

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py tests/python/test_item_palette_integration.py -q --tb=short
```

Expected: `brush_selected` missing and placeholder data still present.

- [ ] **Step 3: Implement dock model support**

Change `VirtualBrushModel` to store `BrushPaletteEntry` objects, return display name for `DisplayRole`, return `entry.search_text` for `UserRole`, and expose `entry_at(row)`. Set `QSortFilterProxyModel.setFilterRole(Qt.ItemDataRole.UserRole)`.

In `BrushPaletteDock.__init__`, accept optional `brush_entries`, group with `entries_by_palette()`, load entries into non-Item models, and add:

```python
brush_selected = pyqtSignal(BrushPaletteEntry)
```

Connect each non-Item `QListView.clicked` to a handler that maps proxy index to source row and emits the entry.

- [ ] **Step 4: Run GREEN**

Run same pytest command. Expected: catalog and existing item palette tests pass.

## Task 3: MainWindow Active Brush Wiring

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Test: `tests/python/test_brush_catalog_ui_bridge.py`
- Test: `tests/python/test_main_window_editor_shell_actions.py`

- [ ] **Step 1: Write failing MainWindow tests**

Add fake canvas method capture:

```python
from pyrme.ui.main_window import MainWindow


def test_main_window_catalog_brush_selection_updates_shell_state(
    qtbot,
    settings_workspace,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, "brush-ui.ini"))
    qtbot.addWidget(window)

    assert window.brush_palette_dock is not None
    window.brush_palette_dock.select_palette("Terrain")
    view = window.brush_palette_dock._views["Terrain"]
    view.clicked.emit(view.model().index(0, 0))

    assert window._active_brush_name == "grass"
    assert window._active_brush_id == "brush:ground:10"
    assert window._active_item_id is None
    assert window._editor_context.session.active_brush_id == "brush:ground:10"
    assert window._editor_context.session.active_item_id is None
    assert "brush: grass" in window.statusBar().currentMessage().lower()
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py tests/python/test_main_window_editor_shell_actions.py -q --tb=short
```

Expected: no MainWindow connection or handler.

- [ ] **Step 3: Implement handler**

In `_setup_docks()`, connect:

```python
self.brush_palette_dock.brush_selected.connect(self._handle_brush_palette_selection)
```

Add:

```python
def _handle_brush_palette_selection(self, entry: BrushPaletteEntry) -> None:
    self._active_brush_name = entry.name
    self._active_brush_id = entry.active_brush_id
    self._active_item_id = None
    self._editor_context.session.active_brush_id = self._active_brush_id
    self._editor_context.session.active_item_id = None
    self._sync_canvas_shell_state()
    self._status_bar().showMessage(f"Brush: {entry.name}.", 3000)
```

Import `BrushPaletteEntry` only for annotations.

- [ ] **Step 4: Run GREEN**

Run same pytest command. Expected: all pass.

## Task 4: Find Brush Dialog Catalog Reuse

**Files:**
- Modify: `pyrme/ui/dialogs/find_brush.py`
- Test: `tests/python/test_find_brush_tier2.py`

- [ ] **Step 1: Write failing dialog tests**

Add tests:

```python
def test_find_brush_default_catalog_includes_catalog_brushes(qapp) -> None:
    dialog = FindBrushDialog()
    dialog.search_field.setText("grass")

    result = dialog.selected_result()

    assert result is not None
    assert result.name == "grass"
    assert result.kind == "brush"
    assert result.palette_name == "Terrain"
    assert result.brush_id == 10
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_find_brush_tier2.py -q --tb=short
```

Expected: `FindBrushResult` has no `brush_id` or default catalog lacks grass.

- [ ] **Step 3: Implement reuse**

Add `brush_id: int | None = None` to `FindBrushResult`. Import `default_brush_palette_entries()` and append catalog brush results in `_default_catalog()`:

```python
brush_results = tuple(
    FindBrushResult(
        name=entry.name,
        kind="brush",
        palette_name=entry.palette_name,
        brush_id=entry.brush_id,
    )
    for entry in default_brush_palette_entries()
    if entry.visible_in_palette
)
return palette_results + brush_results + item_results
```

Update `_format_result_text()` so brush entries show `"{name} brush"`.

- [ ] **Step 4: Run GREEN**

Run same pytest command. Expected: all pass.

## Task 5: Closeout Docs and Verification

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M033-brush-catalog-ui-bridge/M033-brush-catalog-ui-bridge-META.json`
- Modify: `.gsd/milestones/M033-brush-catalog-ui-bridge/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M033-brush-catalog-ui-bridge/slices/S01/S01-SUMMARY.md`

- [ ] **Step 1: Mark S01 tasks complete**

Set each task checkbox in `S01-PLAN.md` to `[x]` only after its tests pass.

- [ ] **Step 2: Write summary**

Create `S01-SUMMARY.md` with:

```markdown
# S01 Summary - Brush Catalog UI Bridge

## Done

- Added Python brush catalog view model for visible ground/wall entries.
- Loaded Brush Palette non-Item tabs from catalog entries.
- Wired catalog brush selection into MainWindow active brush state.
- Reused same catalog in Jump to Brush results.
- Kept map mutation, renderer, minimap, Search menu, and PyO3 export out of scope.

## Verification

Record exact executed commands and observed results from Step 3:

- Focused pytest bundle with pass count.
- Ruff command with "All checks passed!".
- Rust brush baseline with pass count.
- `git diff --check` exit 0.
- `rtk npm run preflight --silent` exit 0.
```

- [ ] **Step 3: Run final verification**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py tests/python/test_item_palette_integration.py tests/python/test_find_brush_tier2.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_legacy_search_menu.py -q --tb=short
PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/models/brush_catalog.py pyrme/ui/docks/brush_palette.py pyrme/ui/dialogs/find_brush.py pyrme/ui/main_window.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_find_brush_tier2.py tests/python/test_item_palette_integration.py
PY312="/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu"
PYO3_PYTHON="$PY312/bin/python3.12" LD_LIBRARY_PATH="$PY312/lib:${LD_LIBRARY_PATH:-}" RUSTFLAGS="-L native=$PY312/lib -l dylib=python3.12" PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core brushes --quiet
git diff --check
PATH="/home/marcelo/.local/bin:$PATH" rtk npm run preflight --silent
```

- [ ] **Step 4: caveman-review before commit**

Review the final diff. Required clean result: no placeholders, no Search menu diff, no renderer/minimap mutation.
