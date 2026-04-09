# Legacy Menu Parity Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the legacy menu contract foundation in the Python shell and port the previously verified navigation/window shell state into the correct legacy menu structure.

**Architecture:** This phase creates a contract-first menu/action layer, ports the reusable canvas and shell-state seam from the verified M5 worktree, and proves parity for the first execution wave with targeted XML-backed tests. The work executes in the dedicated worktree `.worktrees/feat-legacy-menu-parity`, while the root session remains the Operator-style orchestrator and GSD tracker.

**Tech Stack:** Python 3.10, PyQt6, QSettings, pytest, pytest-qt, XML parsing, GSD 2, Superpowers workflow

---

## File Structure

- Create: `pyrme/ui/legacy_menu_contract.py`
  - Phase 1 source of truth for the legacy menu order and the first action metadata set.
- Create: `pyrme/ui/canvas_host.py`
  - Shell-facing canvas protocol and default placeholder canvas widget.
- Modify: `pyrme/ui/main_window.py`
  - Consume the contract, build the legacy top-level menu tree, and port the verified shell state and window/navigation behavior.
- Modify: `pyrme/ui/dialogs/__init__.py`
  - Export `GotoPositionDialog` so `MainWindow` can inject it cleanly.
- Create: `tests/python/test_legacy_menu_contract.py`
  - Pure contract tests for the phase 1 menu/action metadata.
- Create: `tests/python/test_main_window_menu_contract_phase1.py`
  - Verifies the top-level legacy menu tree and action exposure in `MainWindow`.
- Create: `tests/python/test_canvas_seam_m4.py`
  - Ports the verified injectable canvas seam tests from the M5 worktree.
- Create: `tests/python/test_main_window_navigation_m5.py`
  - Ports the verified shell navigation state tests from the M5 worktree.
- Create: `tests/python/test_main_window_commands_m5.py`
  - Ports the verified shortcut/status-tip tests from the M5 worktree.
- Create: `tests/python/test_main_window_parity_phase1.py`
  - XML-backed parity audit for the phase 1 action surface.

This plan intentionally covers only `LEGACY-00-CONTRACT`, `LEGACY-90-NAVIGATE`, and `LEGACY-100-WINDOW`. Follow-on menu groups (`File`, `Edit`, `Search`, `Map`, `Selection`, `View`, `Show`, `Experimental`, `Scripts`, `About`) should get separate plans after this foundation lands.

### Task 1: Lock the legacy menu contract in code and tests

**Files:**
- Create: `pyrme/ui/legacy_menu_contract.py`
- Create: `tests/python/test_legacy_menu_contract.py`

- [ ] **Step 1: Write the failing contract test**

```python
from __future__ import annotations

from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS


def test_legacy_top_level_menu_order_matches_cpp_contract() -> None:
    assert LEGACY_TOP_LEVEL_MENUS == (
        "File",
        "Edit",
        "Editor",
        "Search",
        "Map",
        "Selection",
        "View",
        "Show",
        "Navigate",
        "Window",
        "Experimental",
        "Scripts",
        "About",
    )


def test_phase1_action_metadata_matches_legacy_shortcuts() -> None:
    assert PHASE1_ACTIONS["find_item"].shortcut == "Ctrl+F"
    assert PHASE1_ACTIONS["replace_items"].shortcut == "Ctrl+Shift+F"
    assert PHASE1_ACTIONS["map_properties"].shortcut == "Ctrl+P"
    assert PHASE1_ACTIONS["map_statistics"].shortcut == "F8"
    assert PHASE1_ACTIONS["goto_position"].shortcut == "Ctrl+G"
    assert PHASE1_ACTIONS["goto_previous_position"].shortcut == "P"
    assert PHASE1_ACTIONS["jump_to_brush"].shortcut == "J"
    assert PHASE1_ACTIONS["jump_to_item"].shortcut == "Ctrl+J"
    assert PHASE1_ACTIONS["show_grid"].shortcut == "Shift+G"
    assert PHASE1_ACTIONS["ghost_higher_floors"].shortcut == "Ctrl+L"


def test_phase1_action_metadata_matches_legacy_status_tips() -> None:
    assert PHASE1_ACTIONS["find_item"].status_tip == "Find all instances of an item type the map."
    assert PHASE1_ACTIONS["replace_items"].status_tip == "Replaces all occurrences of one item with another."
    assert PHASE1_ACTIONS["map_properties"].status_tip == "Show and change the map properties."
    assert PHASE1_ACTIONS["map_statistics"].status_tip == "Show map statistics."
    assert PHASE1_ACTIONS["goto_position"].status_tip == "Go to a specific XYZ position."
    assert PHASE1_ACTIONS["goto_previous_position"].status_tip == "Go to the previous screen center position."
    assert PHASE1_ACTIONS["jump_to_brush"].status_tip == "Jump to a brush."
    assert PHASE1_ACTIONS["jump_to_item"].status_tip == "Jump to an item brush (RAW palette)."
    assert PHASE1_ACTIONS["show_grid"].status_tip == "Shows a grid over all items."
    assert PHASE1_ACTIONS["ghost_higher_floors"].status_tip == "Ghost floors."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/python/test_legacy_menu_contract.py -v --tb=short`

Expected: FAIL because `pyrme/ui/legacy_menu_contract.py` does not exist yet.

- [ ] **Step 3: Write the contract module**

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    text: str
    menu_path: tuple[str, ...]
    shortcut: str | None = None
    status_tip: str | None = None


LEGACY_TOP_LEVEL_MENUS = (
    "File",
    "Edit",
    "Editor",
    "Search",
    "Map",
    "Selection",
    "View",
    "Show",
    "Navigate",
    "Window",
    "Experimental",
    "Scripts",
    "About",
)


PHASE1_ACTIONS: dict[str, ActionSpec] = {
    "find_item": ActionSpec(
        action_id="find_item",
        text="&Find Item...",
        menu_path=("Search",),
        shortcut="Ctrl+F",
        status_tip="Find all instances of an item type the map.",
    ),
    "replace_items": ActionSpec(
        action_id="replace_items",
        text="&Replace Items...",
        menu_path=("Edit",),
        shortcut="Ctrl+Shift+F",
        status_tip="Replaces all occurrences of one item with another.",
    ),
    "map_properties": ActionSpec(
        action_id="map_properties",
        text="Properties...",
        menu_path=("Map",),
        shortcut="Ctrl+P",
        status_tip="Show and change the map properties.",
    ),
    "map_statistics": ActionSpec(
        action_id="map_statistics",
        text="Statistics",
        menu_path=("Map",),
        shortcut="F8",
        status_tip="Show map statistics.",
    ),
    "goto_previous_position": ActionSpec(
        action_id="goto_previous_position",
        text="Go to Previous Position",
        menu_path=("Navigate",),
        shortcut="P",
        status_tip="Go to the previous screen center position.",
    ),
    "goto_position": ActionSpec(
        action_id="goto_position",
        text="Go to Position...",
        menu_path=("Navigate",),
        shortcut="Ctrl+G",
        status_tip="Go to a specific XYZ position.",
    ),
    "jump_to_brush": ActionSpec(
        action_id="jump_to_brush",
        text="Jump to Brush...",
        menu_path=("Navigate",),
        shortcut="J",
        status_tip="Jump to a brush.",
    ),
    "jump_to_item": ActionSpec(
        action_id="jump_to_item",
        text="Jump to Item...",
        menu_path=("Navigate",),
        shortcut="Ctrl+J",
        status_tip="Jump to an item brush (RAW palette).",
    ),
    "show_grid": ActionSpec(
        action_id="show_grid",
        text="Show grid",
        menu_path=("View",),
        shortcut="Shift+G",
        status_tip="Shows a grid over all items.",
    ),
    "ghost_higher_floors": ActionSpec(
        action_id="ghost_higher_floors",
        text="Ghost higher floors",
        menu_path=("View",),
        shortcut="Ctrl+L",
        status_tip="Ghost floors.",
    ),
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/python/test_legacy_menu_contract.py -v --tb=short`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyrme/ui/legacy_menu_contract.py tests/python/test_legacy_menu_contract.py
git commit -m "test: lock legacy menu contract metadata"
```

### Task 2: Rebuild the MainWindow menu surface around the legacy top-level tree

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Create: `tests/python/test_main_window_menu_contract_phase1.py`

- [ ] **Step 1: Write the failing menu tree test**

```python
from __future__ import annotations

from pyrme.ui.main_window import MainWindow


def _menu_titles(window: MainWindow) -> list[str]:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    return [action.text().replace("&", "") for action in menu_bar.actions()]


def test_main_window_exposes_legacy_top_level_menu_tree(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert _menu_titles(window) == [
        "File",
        "Edit",
        "Editor",
        "Search",
        "Map",
        "Selection",
        "View",
        "Show",
        "Navigate",
        "Window",
        "Experimental",
        "Scripts",
        "About",
    ]


def test_main_window_exposes_phase1_action_objects(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.find_item_action.objectName() == "action_find_item"
    assert window.replace_items_action.objectName() == "action_replace_items"
    assert window.map_properties_action.objectName() == "action_map_properties"
    assert window.map_statistics_action.objectName() == "action_map_statistics"
    assert window.goto_previous_position_action.objectName() == "action_goto_previous_position"
    assert window.goto_position_action.objectName() == "action_goto_position"
    assert window.jump_to_brush_action.objectName() == "action_jump_to_brush"
    assert window.jump_to_item_action.objectName() == "action_jump_to_item"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/python/test_main_window_menu_contract_phase1.py -v --tb=short`

Expected: FAIL because the root `MainWindow` still exposes the simplified `File/Edit/View/Map/Tools/Help` shell.

- [ ] **Step 3: Replace the menu setup with a contract-driven shell**

Replace the menu-related helpers in `pyrme/ui/main_window.py` with this pattern:

```python
from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS


def _menu_key(title: str) -> str:
    return title.lower().replace(" ", "_")


def _menu_label(title: str) -> str:
    return "&About" if title == "About" else f"&{title}"


def _action_from_spec(self, spec_key: str, handler=None) -> QAction:
    spec = PHASE1_ACTIONS[spec_key]
    action = QAction(spec.text, self)
    action.setObjectName(f"action_{spec.action_id}")
    if spec.shortcut:
        action.setShortcut(spec.shortcut)
    if spec.status_tip:
        action.setStatusTip(spec.status_tip)
    if handler is not None:
        action.triggered.connect(handler)
    return action


def _setup_menu_bar(self) -> None:
    menu_bar = self.menuBar()
    assert menu_bar is not None
    menu_bar.clear()
    menu_bar.setFont(TYPOGRAPHY.ui_label())

    self._menus = {}
    for title in LEGACY_TOP_LEVEL_MENUS:
        menu = menu_bar.addMenu(_menu_label(title))
        assert menu is not None
        self._menus[title] = menu

    self.find_item_action = self._action_from_spec("find_item", self._show_find_item)
    self.replace_items_action = self._action_from_spec("replace_items", self._show_replace_items)
    self.map_properties_action = self._action_from_spec("map_properties", self._show_map_properties)
    self.map_statistics_action = self._action_from_spec("map_statistics", self._show_map_statistics)
    self.goto_previous_position_action = self._action_from_spec("goto_previous_position", self._go_to_previous_position)
    self.goto_position_action = self._action_from_spec("goto_position", self._show_goto_position)
    self.jump_to_brush_action = self._action_from_spec("jump_to_brush", self._show_jump_to_brush)
    self.jump_to_item_action = self._action_from_spec("jump_to_item", self._show_jump_to_item)
    self.show_grid_action = self._action_from_spec("show_grid", self._toggle_show_grid)
    self.show_grid_action.setCheckable(True)
    self.ghost_higher_action.setShortcut(PHASE1_ACTIONS["ghost_higher_floors"].shortcut)
    self.ghost_higher_action.setStatusTip(PHASE1_ACTIONS["ghost_higher_floors"].status_tip)

    self._menus["Search"].addAction(self.find_item_action)
    self._menus["Edit"].addAction(self.replace_items_action)
    self._menus["Map"].addAction(self.map_properties_action)
    self._menus["Map"].addAction(self.map_statistics_action)
    self._menus["Navigate"].addAction(self.goto_previous_position_action)
    self._menus["Navigate"].addAction(self.goto_position_action)
    self._menus["Navigate"].addAction(self.jump_to_brush_action)
    self._menus["Navigate"].addAction(self.jump_to_item_action)
    self._menus["View"].addAction(self.show_grid_action)
    self._menus["View"].addAction(self.ghost_higher_action)
```

Also add minimal no-op handlers so the file imports cleanly before the full shell-state task:

```python
def _show_replace_items(self) -> None:
    self.statusBar().showMessage("Replace Items is not available yet.", 3000)


def _show_map_statistics(self) -> None:
    self.statusBar().showMessage("Map Statistics is not available yet.", 3000)


def _go_to_previous_position(self) -> None:
    self.statusBar().showMessage("No previous position stored.", 3000)


def _show_goto_position(self) -> None:
    self.statusBar().showMessage("Go to Position is not available yet.", 3000)


def _show_jump_to_brush(self) -> None:
    self.statusBar().showMessage("Jump to Brush is not available yet.", 3000)


def _show_jump_to_item(self) -> None:
    self.statusBar().showMessage("Jump to Item is not available yet.", 3000)


def _toggle_show_grid(self, checked: bool) -> None:
    self.statusBar().showMessage(f"Show Grid {'ON' if checked else 'OFF'}", 3000)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/python/test_main_window_menu_contract_phase1.py -v --tb=short`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyrme/ui/main_window.py tests/python/test_main_window_menu_contract_phase1.py
git commit -m "feat: rebuild phase1 shell around legacy menu tree"
```

### Task 3: Port the canvas seam and injectable dialog/canvas dependencies

**Files:**
- Create: `pyrme/ui/canvas_host.py`
- Modify: `pyrme/ui/dialogs/__init__.py`
- Modify: `pyrme/ui/main_window.py`
- Create: `tests/python/test_canvas_seam_m4.py`

- [ ] **Step 1: Write the failing seam test**

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.ui.canvas_host import PlaceholderCanvasWidget
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path


def _build_settings(tmp_path: Path, name: str) -> QSettings:
    return QSettings(str(tmp_path / name), QSettings.Format.IniFormat)


class _FakeCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.position: tuple[int, int, int] | None = None
        self.floor: int | None = None
        self.zoom_percent: int | None = None
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.show_lower: bool | None = None

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)

    def set_floor(self, z: int) -> None:
        self.floor = z

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled


def test_main_window_uses_injected_canvas_factory_and_forwards_shell_state(qtbot, tmp_path: Path) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        holder["canvas"] = canvas
        return canvas

    window = MainWindow(
        settings=_build_settings(tmp_path, "canvas.ini"),
        canvas_factory=_canvas_factory,
    )
    qtbot.addWidget(window)

    canvas = holder["canvas"]
    assert window.centralWidget() is canvas
    assert canvas.position == (32000, 32000, 7)
    assert canvas.floor == 7
    assert canvas.zoom_percent == 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/python/test_canvas_seam_m4.py -v --tb=short`

Expected: FAIL because `pyrme/ui/canvas_host.py` does not exist and `MainWindow` does not accept `settings` or `canvas_factory`.

- [ ] **Step 3: Port the seam and injectable constructor**

Create `pyrme/ui/canvas_host.py` with the verified seam:

```python
from __future__ import annotations

from typing import Protocol

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from pyrme import __app_name__
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY


class CanvasWidgetProtocol(Protocol):
    def set_position(self, x: int, y: int, z: int) -> None: ...
    def set_floor(self, z: int) -> None: ...
    def set_zoom(self, percent: int) -> None: ...
    def set_show_grid(self, enabled: bool) -> None: ...
    def set_ghost_higher(self, enabled: bool) -> None: ...
    def set_show_lower(self, enabled: bool) -> None: ...


class PlaceholderCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.position = (32000, 32000, 7)
        self.floor = 7
        self.zoom_percent = 100
        self.show_grid = False
        self.ghost_higher = False
        self.show_lower = True
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(TYPOGRAPHY.ui_label(size=13))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        self._refresh_label()

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)
        self.floor = z
        self._refresh_label()

    def set_floor(self, z: int) -> None:
        self.floor = z
        self._refresh_label()

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent
        self._refresh_label()

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled
        self._refresh_label()

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled
        self._refresh_label()

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled
        self._refresh_label()

    def _refresh_label(self) -> None:
        x, y, z = self.position
        self._label.setText(
            f"🗺️ {__app_name__} Canvas\\n\\n"
            "Rust-backed wgpu renderer will be integrated in Milestone 4.\\n"
            "This placeholder keeps shell state flowing through a stable widget seam.\\n\\n"
            f"Position: {x}, {y}, {z:02d}\\n"
            f"Zoom: {self.zoom_percent}%\\n"
            f"Grid: {'On' if self.show_grid else 'Off'}\\n"
            f"Ghost Higher Floors: {'On' if self.ghost_higher else 'Off'}\\n"
            f"Show Lower Floors: {'On' if self.show_lower else 'Off'}"
        )
```

Update `pyrme/ui/dialogs/__init__.py`:

```python
from pyrme.ui.dialogs.goto_position import GotoPositionDialog

__all__ = [
    "FindItemDialog",
    "FindItemQuery",
    "FindItemResult",
    "FindItemResultMode",
    "GotoPositionDialog",
    "MapPropertiesDialog",
    "MapPropertiesState",
]
```

Update the `MainWindow` constructor shape:

```python
from typing import TYPE_CHECKING, Protocol

from PyQt6.QtCore import QSettings

from pyrme.ui.canvas_host import CanvasWidgetProtocol, PlaceholderCanvasWidget
from pyrme.ui.dialogs import FindItemDialog, GotoPositionDialog, MapPropertiesDialog


def __init__(
    self,
    parent: QWidget | None = None,
    *,
    settings: QSettings | None = None,
    goto_dialog_factory=None,
    canvas_factory=None,
) -> None:
    super().__init__(parent)
    self._settings = settings or QSettings("Noct Map Editor", "Noct")
    self._goto_dialog_factory = goto_dialog_factory or GotoPositionDialog
    self._canvas_factory = canvas_factory or PlaceholderCanvasWidget
    self._current_x, self._current_y, self._current_z = (32000, 32000, 7)
    self._previous_position: tuple[int, int, int] | None = None
    self._zoom_percent = 100
    self._show_grid_enabled = False
```

Replace `_setup_central_widget()` with:

```python
def _setup_central_widget(self) -> None:
    self._canvas = self._canvas_factory(self)
    self.setCentralWidget(self._canvas)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/python/test_canvas_seam_m4.py -v --tb=short`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyrme/ui/canvas_host.py pyrme/ui/dialogs/__init__.py pyrme/ui/main_window.py tests/python/test_canvas_seam_m4.py
git commit -m "feat: port injectable canvas seam for legacy shell"
```

### Task 4: Port the verified shell navigation and window-state behavior into the legacy shell

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Create: `tests/python/test_main_window_navigation_m5.py`
- Create: `tests/python/test_main_window_commands_m5.py`

- [ ] **Step 1: Write the failing navigation and command tests**

Use the verified M5 tests directly:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QDialog

import pyrme.ui.main_window as main_window_module
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path


def _build_settings(tmp_path: Path, name: str) -> QSettings:
    return QSettings(str(tmp_path / name), QSettings.Format.IniFormat)


def _shortcut(action: QAction) -> str:
    return action.shortcut().toString()


def _status_message(window: MainWindow) -> str:
    status_bar = window.statusBar()
    assert status_bar is not None
    return status_bar.currentMessage()


def test_main_window_exposes_legacy_navigation_shortcuts_and_status_tips(qtbot, tmp_path: Path) -> None:
    window = MainWindow(settings=_build_settings(tmp_path, "commands.ini"))
    qtbot.addWidget(window)

    assert _shortcut(window.find_item_action) == "Ctrl+F"
    assert _shortcut(window.replace_items_action) == "Ctrl+Shift+F"
    assert _shortcut(window.map_properties_action) == "Ctrl+P"
    assert _shortcut(window.map_statistics_action) == "F8"
    assert _shortcut(window.goto_position_action) == "Ctrl+G"
    assert _shortcut(window.goto_previous_position_action) == "P"
    assert _shortcut(window.jump_to_brush_action) == "J"
    assert _shortcut(window.jump_to_item_action) == "Ctrl+J"
    assert _shortcut(window.ghost_higher_action) == "Ctrl+L"
    assert _shortcut(window.show_grid_action) == "Shift+G"
```

and

```python
def test_main_window_goto_position_updates_shell_state(qtbot, monkeypatch, tmp_path: Path) -> None:
    class _FakeGotoDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def get_position(self) -> tuple[int, int, int]:
            return (32123, 32234, 6)

    monkeypatch.setattr(main_window_module, "GotoPositionDialog", _FakeGotoDialog)

    window = MainWindow(settings=_build_settings(tmp_path, "goto.ini"))
    qtbot.addWidget(window)

    window._show_goto_position()

    assert window._coord_label.text() == "Pos: (X: 32123, Y: 32234, Z: 06)"
    assert window._items_label.text() == "Floor 6 (Above Ground)"
    assert window.floor_actions[6].isChecked()
    assert window.minimap_dock.pos_label.text() == "Z: 06"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/python/test_main_window_navigation_m5.py tests/python/test_main_window_commands_m5.py -v --tb=short`

Expected: FAIL because the current root shell does not persist state or drive these actions yet.

- [ ] **Step 3: Port the verified M5 behavior into the root shell**

Store toolbars and docks as attributes:

```python
self.drawing_toolbar = QToolBar("Drawing Tools")
self.floor_toolbar = QToolBar("Floors")
self.brush_palette_dock = BrushPaletteDock(self)
self.minimap_dock = MinimapDock(self)
self.properties_dock = PropertiesDock(self)
self.waypoints_dock = WaypointsDock(self)
```

Add shell-state helpers:

```python
DEFAULT_POSITION = (32000, 32000, 7)


def _set_current_position(self, x: int, y: int, z: int) -> None:
    self._current_x, self._current_y, self._current_z = x, y, z
    self._coord_label.setText(f"Pos: (X: {x}, Y: {y}, Z: {z:02d})")
    floor_name = "Above Ground" if z < 7 else "Ground" if z == 7 else "Underground"
    self._items_label.setText(f"Floor {z} ({floor_name})")
    self.minimap_dock.pos_label.setText(f"Z: {z:02d}")
    self._canvas.set_position(x, y, z)


def _set_floor(self, z: int) -> None:
    z = max(0, min(15, z))
    self.floor_actions[z].setChecked(True)
    self._set_current_position(self._current_x, self._current_y, z)
    self._canvas.set_floor(z)


def _go_to_previous_position(self) -> None:
    if self._previous_position is None:
        self.statusBar().showMessage("No previous position stored.", 3000)
        return
    current = (self._current_x, self._current_y, self._current_z)
    previous = self._previous_position
    self._previous_position = current
    self._set_current_position(*previous)
    self.statusBar().showMessage(
        f"Returned to previous position {previous[0]}, {previous[1]}, {previous[2]:02d}",
        3000,
    )


def _show_goto_position(self) -> None:
    dialog = self._goto_dialog_factory(self)
    if dialog.exec() != int(QDialog.DialogCode.Accepted):
        return
    self._previous_position = (self._current_x, self._current_y, self._current_z)
    x, y, z = dialog.get_position()
    self._set_current_position(x, y, z)
    self.floor_actions[z].setChecked(True)
```

Wire floor/minimap/show-grid/ghost/show-lower:

```python
def _floor_up(self) -> None:
    self._set_floor(self._current_z - 1)


def _floor_down(self) -> None:
    self._set_floor(self._current_z + 1)


def _toggle_show_grid(self, checked: bool) -> None:
    self._show_grid_enabled = checked
    self._canvas.set_show_grid(checked)
    self.statusBar().showMessage(f"Show Grid {'ON' if checked else 'OFF'}", 3000)


def _toggle_ghost_higher(self, checked: bool) -> None:
    self._canvas.set_ghost_higher(checked)
    self.statusBar().showMessage(f"Ghost Higher Floors {'ON' if checked else 'OFF'}", 3000)


def _toggle_show_lower(self, checked: bool) -> None:
    self._canvas.set_show_lower(checked)
    self.statusBar().showMessage(f"Show Lower Floors {'ON' if checked else 'OFF'}", 3000)
```

Persist window geometry, state, and shell state:

```python
def closeEvent(self, event) -> None:
    self._settings.setValue("main_window/geometry", self.saveGeometry())
    self._settings.setValue("main_window/state", self.saveState())
    self._settings.setValue("main_window/position", [self._current_x, self._current_y, self._current_z])
    self._settings.setValue("main_window/previous_position", list(self._previous_position) if self._previous_position else None)
    self._settings.setValue("main_window/show_grid", self.show_grid_action.isChecked())
    self._settings.setValue("main_window/ghost_higher", self.ghost_higher_action.isChecked())
    self._settings.setValue("main_window/show_lower", self.show_lower_action.isChecked())
    super().closeEvent(event)


def _restore_window_state(self) -> None:
    geometry = self._settings.value("main_window/geometry")
    if geometry is not None:
        self.restoreGeometry(geometry)
    state = self._settings.value("main_window/state")
    if state is not None:
        self.restoreState(state)
    position = self._settings.value("main_window/position", self.DEFAULT_POSITION)
    x, y, z = [int(value) for value in position]
    self._set_current_position(x, y, z)
    self.floor_actions[z].setChecked(True)
    previous = self._settings.value("main_window/previous_position")
    self._previous_position = tuple(int(v) for v in previous) if previous else None
    self.show_grid_action.setChecked(self._settings.value("main_window/show_grid", False, bool))
    self.ghost_higher_action.setChecked(self._settings.value("main_window/ghost_higher", False, bool))
    self.show_lower_action.setChecked(self._settings.value("main_window/show_lower", True, bool))
```

Finish wiring:

```python
self.floor_up_action.triggered.connect(self._floor_up)
self.floor_down_action.triggered.connect(self._floor_down)
self.ghost_higher_action.toggled.connect(self._toggle_ghost_higher)
self.show_lower_action.toggled.connect(self._toggle_show_lower)
self.minimap_dock.z_up_btn.clicked.connect(self._floor_up)
self.minimap_dock.z_down_btn.clicked.connect(self._floor_down)
self.toggle_minimap_action = self.minimap_dock.toggleViewAction()
self.toggle_brush_palette_action = self.brush_palette_dock.toggleViewAction()
self.toggle_properties_action = self.properties_dock.toggleViewAction()
self.toggle_waypoints_action = self.waypoints_dock.toggleViewAction()
self.toggle_drawing_toolbar_action = self.drawing_toolbar.toggleViewAction()
self.toggle_floors_toolbar_action = self.floor_toolbar.toggleViewAction()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/python/test_canvas_seam_m4.py tests/python/test_main_window_navigation_m5.py tests/python/test_main_window_commands_m5.py -v --tb=short`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyrme/ui/main_window.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_navigation_m5.py tests/python/test_main_window_commands_m5.py
git commit -m "feat: port phase1 legacy navigation and window state"
```

### Task 5: Add an XML-backed phase 1 parity audit and run the slice verification set

**Files:**
- Create: `tests/python/test_main_window_parity_phase1.py`

- [ ] **Step 1: Write the failing parity audit test**

```python
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS


ROOT = Path(__file__).resolve().parents[2]


def _legacy_root() -> ET.Element:
    tree = ET.parse(ROOT / "remeres-map-editor-redux" / "data" / "menubar.xml")
    return tree.getroot()


def test_legacy_top_level_menu_order_matches_xml() -> None:
    root = _legacy_root()
    top_level = tuple(menu.attrib["name"] for menu in root.findall("./menu"))
    assert top_level[: len(LEGACY_TOP_LEVEL_MENUS)] == LEGACY_TOP_LEVEL_MENUS


def test_phase1_shortcuts_match_xml() -> None:
    root = _legacy_root()
    legacy = {
        item.attrib["action"]: item.attrib.get("hotkey", "")
        for item in root.findall(".//item")
        if item.attrib.get("action")
    }
    assert legacy["FIND_ITEM"] == PHASE1_ACTIONS["find_item"].shortcut
    assert legacy["REPLACE_ITEMS"] == PHASE1_ACTIONS["replace_items"].shortcut
    assert legacy["MAP_PROPERTIES"] == PHASE1_ACTIONS["map_properties"].shortcut
    assert legacy["MAP_STATISTICS"] == PHASE1_ACTIONS["map_statistics"].shortcut
    assert legacy["GOTO_PREVIOUS_POSITION"] == PHASE1_ACTIONS["goto_previous_position"].shortcut
    assert legacy["GOTO_POSITION"] == PHASE1_ACTIONS["goto_position"].shortcut
    assert legacy["JUMP_TO_BRUSH"] == PHASE1_ACTIONS["jump_to_brush"].shortcut
    assert legacy["JUMP_TO_ITEM_BRUSH"] == PHASE1_ACTIONS["jump_to_item"].shortcut
    assert legacy["SHOW_GRID"] == PHASE1_ACTIONS["show_grid"].shortcut
    assert legacy["GHOST_HIGHER_FLOORS"] == PHASE1_ACTIONS["ghost_higher_floors"].shortcut
```

- [ ] **Step 2: Run the parity audit test to verify it fails if contract drift exists**

Run: `python3 -m pytest tests/python/test_main_window_parity_phase1.py -v --tb=short`

Expected: PASS if the earlier tasks are correct. If it fails, fix the drift before proceeding.

- [ ] **Step 3: Run the full phase 1 verification set**

Run: `python3 -m pytest tests/python/test_legacy_menu_contract.py tests/python/test_main_window_menu_contract_phase1.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_navigation_m5.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_parity_phase1.py -v --tb=short`

Expected: PASS

- [ ] **Step 4: Run lint and type checks for touched files**

Run: `ruff check pyrme/ui/main_window.py pyrme/ui/legacy_menu_contract.py pyrme/ui/canvas_host.py pyrme/ui/dialogs/__init__.py tests/python/test_legacy_menu_contract.py tests/python/test_main_window_menu_contract_phase1.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_navigation_m5.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_parity_phase1.py`

Expected: PASS

Run: `mypy pyrme/ui/main_window.py pyrme/ui/legacy_menu_contract.py pyrme/ui/canvas_host.py pyrme/ui/dialogs/__init__.py tests/python/test_legacy_menu_contract.py tests/python/test_main_window_menu_contract_phase1.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_navigation_m5.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_parity_phase1.py --ignore-missing-imports`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/python/test_main_window_parity_phase1.py
git commit -m "test: add phase1 legacy parity audit"
```

## Self-Review Notes
- This plan intentionally stops after the contract foundation and the reusable navigation/window wave.
- Remaining menu groups still need separate plans once this foundation lands cleanly.
- Every action introduced in this plan is grounded in `menubar.xml` or in already-existing local dialogs/docks.
