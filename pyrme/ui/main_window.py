"""Noct Map Editor Main Window – The editor shell."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QStatusBar,
    QToolBar,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.ui.canvas_host import CanvasWidgetProtocol, PlaceholderCanvasWidget
from pyrme.ui.dialogs import FindItemDialog, GotoPositionDialog, MapPropertiesDialog
from pyrme.ui.docks import BrushPaletteDock, MinimapDock, PropertiesDock, WaypointsDock
from pyrme.ui.legacy_menu_contract import (
    EDITOR_ACTION_ORDER,
    EDITOR_ACTIONS,
    EDITOR_ZOOM_ACTION_ORDER,
    EDITOR_ZOOM_MENU_TITLE,
    LEGACY_TOP_LEVEL_MENUS,
    PHASE1_ACTIONS,
)
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main editor window for Noct Map Editor."""

    # Responsive design: desktop-only application target
    WINDOW_MIN_SIZE = QSize(1280, 720)
    WINDOW_DEFAULT_SIZE = QSize(1600, 1000)
    DEFAULT_POSITION = (32000, 32000, 7)

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
        self.brush_palette_dock: BrushPaletteDock | None = None
        self.minimap_dock: MinimapDock | None = None
        self.properties_dock: PropertiesDock | None = None
        self.waypoints_dock: WaypointsDock | None = None
        self.toggle_minimap_action: QAction | None = None
        self.toggle_floors_toolbar_action: QAction | None = None
        self._current_x, self._current_y, self._current_z = self.DEFAULT_POSITION
        self._previous_position: tuple[int, int, int] | None = None
        self._zoom_percent = 100
        self._show_grid_enabled = False
        self._ghost_higher_enabled = False
        self._show_lower_enabled = True
        self._setup_window()
        self._setup_menu_bar()
        self._setup_toolbars()
        self._setup_central_widget()
        self._setup_docks()
        self._setup_status_bar()
        self._restore_window_state()
        self._sync_canvas_shell_state()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(self.WINDOW_MIN_SIZE)
        self.resize(self.WINDOW_DEFAULT_SIZE)
        self.setDockNestingEnabled(True)
        # Main application background: Void Black
        self.setStyleSheet(
            f"QMainWindow {{ background-color: {qss_color(THEME.void_black)}; }}"
        )

    def _setup_menu_bar(self) -> None:
        """Create the main menu bar."""
        menu_bar = self.menuBar()
        assert menu_bar is not None
        menu_bar.clear()
        menu_bar.setFont(TYPOGRAPHY.ui_label())
        self._menus: dict[str, QMenu] = {}
        for title in LEGACY_TOP_LEVEL_MENUS:
            menu = menu_bar.addMenu(self._menu_label(title))
            assert menu is not None
            self._menus[title] = menu

        self.find_item_action = self._action_from_spec("find_item", self._show_find_item)
        self.replace_items_action = self._action_from_spec(
            "replace_items", self._show_replace_items
        )
        self.map_properties_action = self._action_from_spec(
            "map_properties", self._show_map_properties
        )
        self.map_statistics_action = self._action_from_spec(
            "map_statistics", self._show_map_statistics
        )
        self.goto_previous_position_action = self._action_from_spec(
            "goto_previous_position", self._go_to_previous_position
        )
        self.goto_position_action = self._action_from_spec(
            "goto_position", self._show_goto_position
        )
        self.jump_to_brush_action = self._action_from_spec(
            "jump_to_brush", self._show_jump_to_brush
        )
        self.jump_to_item_action = self._action_from_spec("jump_to_item", self._show_jump_to_item)
        self.show_grid_action = self._action_from_spec("show_grid")
        self.show_grid_action.setCheckable(True)
        self.show_grid_action.toggled.connect(self._toggle_show_grid)
        self.ghost_higher_action = self._action_from_spec("ghost_higher_floors")
        self.ghost_higher_action.setCheckable(True)
        self.ghost_higher_action.toggled.connect(self._stub_ghost_higher)

        phase1_action_attrs = {
            "find_item": self.find_item_action,
            "replace_items": self.replace_items_action,
            "map_properties": self.map_properties_action,
            "map_statistics": self.map_statistics_action,
            "goto_previous_position": self.goto_previous_position_action,
            "goto_position": self.goto_position_action,
            "jump_to_brush": self.jump_to_brush_action,
            "jump_to_item": self.jump_to_item_action,
            "show_grid": self.show_grid_action,
            "ghost_higher_floors": self.ghost_higher_action,
        }
        for spec_key, spec in PHASE1_ACTIONS.items():
            menu = self._menus[spec.menu_path[0]]
            action = phase1_action_attrs[spec_key]
            menu.addAction(action)

        self._setup_editor_menu()

    def _setup_toolbars(self) -> None:
        """Create the main toolbars."""
        # Drawing tools toolbar
        drawing_toolbar = QToolBar("Drawing Tools")
        drawing_toolbar.setObjectName("drawing_toolbar")
        drawing_toolbar.setMovable(True)
        drawing_toolbar.addAction(self._action("Select"))
        drawing_toolbar.addAction(self._action("Draw"))
        drawing_toolbar.addAction(self._action("Erase"))
        drawing_toolbar.addAction(self._action("Fill"))
        drawing_toolbar.addSeparator()
        drawing_toolbar.addAction(self._action("Move"))
        self.addToolBar(drawing_toolbar)

        # Floor toolbar (Layers Toolbar)
        self.floor_toolbar = QToolBar("Floors")
        self.floor_toolbar.setObjectName("floor_toolbar")
        self.floor_toolbar.setMovable(True)
        floor_group = QActionGroup(self)
        floor_group.setExclusive(True)
        self.floor_actions: list[QAction] = []
        for i in range(16):
            action = self._action(f"F{i}")
            action.setObjectName(f"floor_{i}")
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked=False, value=i: self._select_floor(value) if checked else None
            )
            floor_group.addAction(action)
            self.floor_toolbar.addAction(action)
            self.floor_actions.append(action)
            if i == 7:  # Default to ground floor (Z=7 usually, from 0-15)
                action.setChecked(True)

        self.floor_toolbar.addSeparator()

        # Floor navigation actions (stub slots)
        self.floor_up_action = self._action("Floor Up", "Ctrl+PgUp")
        self.floor_up_action.setObjectName("floor_up_action")
        self.floor_up_action.setToolTip("Go to higher floor (Ctrl+PageUp)")
        self.floor_up_action.triggered.connect(self._floor_up)
        self.floor_toolbar.addAction(self.floor_up_action)

        self.floor_down_action = self._action("Floor Down", "Ctrl+PgDown")
        self.floor_down_action.setObjectName("floor_down_action")
        self.floor_down_action.setToolTip("Go to lower floor (Ctrl+PageDown)")
        self.floor_down_action.triggered.connect(self._floor_down)
        self.floor_toolbar.addAction(self.floor_down_action)

        self.floor_toolbar.addSeparator()

        # Floor visibility toggle actions (checkable, stub slots)
        self.floor_ghost_higher_action = self._action("Ghost Higher Floors")
        self.floor_ghost_higher_action.setObjectName("ghost_higher_toolbar_action")
        self.floor_ghost_higher_action.setCheckable(True)
        self.floor_ghost_higher_action.setToolTip(
            "Show transparent overlay of higher floors"
        )
        self.floor_ghost_higher_action.toggled.connect(self._stub_ghost_higher)
        self.floor_toolbar.addAction(self.floor_ghost_higher_action)

        self.show_lower_action = self._action("Show Lower Floors")
        self.show_lower_action.setObjectName("show_lower_action")
        self.show_lower_action.setCheckable(True)
        self.show_lower_action.setChecked(True)
        self.show_lower_action.setToolTip("Show floors below the current one")
        self.show_lower_action.toggled.connect(self._stub_show_lower)
        self.floor_toolbar.addAction(self.show_lower_action)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.floor_toolbar)
        self.toggle_floors_toolbar_action = self.floor_toolbar.toggleViewAction()

    def _setup_central_widget(self) -> None:
        """Set up the central canvas area."""
        self._canvas: CanvasWidgetProtocol = self._canvas_factory(self)
        self.setCentralWidget(self._canvas)
        self._sync_canvas_shell_state()

    def _show_map_properties(self) -> None:
        """Show the map properties dialog."""
        dialog = MapPropertiesDialog(self)
        dialog.exec()

    def _show_find_item(self) -> None:
        """Show the find item dialog."""
        dialog = FindItemDialog(self)
        dialog.exec()

    def _show_replace_items(self) -> None:
        self._status_bar().showMessage("Replace Items is not available yet.", 3000)

    def _show_map_statistics(self) -> None:
        self._status_bar().showMessage("Map Statistics is not available yet.", 3000)

    def _show_new_view(self) -> None:
        self._status_bar().showMessage("New View is not available yet.", 3000)

    def _show_take_screenshot(self) -> None:
        self._status_bar().showMessage("Take Screenshot is not available yet.", 3000)

    def _show_toggle_fullscreen(self) -> None:
        self._status_bar().showMessage("Enter Fullscreen is not available yet.", 3000)

    def _show_zoom_in(self) -> None:
        self._status_bar().showMessage("Zoom In is not available yet.", 3000)

    def _show_zoom_out(self) -> None:
        self._status_bar().showMessage("Zoom Out is not available yet.", 3000)

    def _show_zoom_normal(self) -> None:
        self._status_bar().showMessage("Zoom Normal is not available yet.", 3000)

    def _go_to_previous_position(self) -> None:
        if self._previous_position is None:
            self._status_bar().showMessage("No previous position stored.", 3000)
            return

        current = (self._current_x, self._current_y, self._current_z)
        previous = self._previous_position
        self._previous_position = current
        self._set_current_position(*previous)
        self._status_bar().showMessage(
            f"Returned to previous position {previous[0]}, {previous[1]}, {previous[2]:02d}",
            3000,
        )

    def _show_goto_position(self) -> None:
        dialog = self._goto_dialog_factory(self)
        if hasattr(dialog, "position_input") and hasattr(
            dialog.position_input, "set_position"
        ):
            dialog.position_input.set_position(
                self._current_x,
                self._current_y,
                self._current_z,
            )
        if dialog.exec() == int(QDialog.DialogCode.Accepted):
            self._set_current_position(
                *dialog.get_position(),
                track_history=True,
                announce=True,
            )

    def _show_jump_to_brush(self) -> None:
        self._status_bar().showMessage("Jump to Brush is not available yet.", 3000)

    def _show_jump_to_item(self) -> None:
        self._status_bar().showMessage("Jump to Item is not available yet.", 3000)

    def _toggle_show_grid(self, checked: bool) -> None:
        self._show_grid_enabled = checked
        self._canvas.set_show_grid(checked)
        self._status_bar().showMessage(f"Show Grid {'ON' if checked else 'OFF'}", 3000)

    def _setup_docks(self) -> None:
        """Create dock widgets for palettes and tools using Glassmorphism."""
        # Brush Palette dock (left side)
        self.brush_palette_dock = BrushPaletteDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.brush_palette_dock,
        )

        # Minimap dock (right side)
        self.minimap_dock = MinimapDock(self)
        self.minimap_dock.z_up_btn.clicked.connect(self._floor_up)
        self.minimap_dock.z_down_btn.clicked.connect(self._floor_down)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.minimap_dock)
        self.toggle_minimap_action = self.minimap_dock.toggleViewAction()

        # Properties dock (right side, below minimap)
        self.properties_dock = PropertiesDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        # Waypoints dock (right side, below properties)
        self.waypoints_dock = WaypointsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.waypoints_dock)

    def _setup_status_bar(self) -> None:
        """Create the status bar with coordinate and zoom info."""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self._coord_label = QLabel("Pos: (X: 32000, Y: 32000, Z: 07)")
        # Must use JetBrains Mono for coordinates!
        self._coord_label.setFont(TYPOGRAPHY.coordinate_display())
        self._coord_label.setStyleSheet(
            f"padding: 0 12px; color: {qss_color(THEME.ash_lavender)};"
        )
        status_bar.addPermanentWidget(self._coord_label)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setFont(TYPOGRAPHY.ui_label())
        self._zoom_label.setStyleSheet(
            f"padding: 0 12px; color: {qss_color(THEME.ash_lavender)};"
        )
        status_bar.addPermanentWidget(self._zoom_label)

        self._items_label = QLabel("Floor 7 (Ground)")
        self._items_label.setFont(TYPOGRAPHY.ui_label())
        self._items_label.setStyleSheet(
            f"padding: 0 12px; color: {qss_color(THEME.ash_lavender)};"
        )
        status_bar.addPermanentWidget(self._items_label)

        status_bar.showMessage(f"{__app_name__} v{__version__} — Ready", 5000)

    def _status_bar(self) -> QStatusBar:
        status_bar = self.statusBar()
        assert status_bar is not None
        return status_bar

    def _action(self, text: str, shortcut: str | None = None) -> QAction:
        """Helper to create a QAction."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def _menu_label(self, title: str) -> str:
        return "&About" if title == "About" else f"&{title}"

    def _action_from_contract_spec(self, spec, handler=None) -> QAction:
        action = QAction(spec.text, self)
        action.setObjectName(f"action_{spec.action_id}")
        if spec.shortcut:
            action.setShortcut(spec.shortcut)
        if spec.status_tip:
            action.setStatusTip(spec.status_tip)
        if handler is not None:
            action.triggered.connect(handler)
        return action

    def _action_from_spec(self, spec_key: str, handler=None) -> QAction:
        spec = PHASE1_ACTIONS[spec_key]
        return self._action_from_contract_spec(spec, handler)

    def _setup_editor_menu(self) -> None:
        editor_menu = self._menus["Editor"]

        editor_handlers = {
            "new_view": self._show_new_view,
            "toggle_fullscreen": self._show_toggle_fullscreen,
            "take_screenshot": self._show_take_screenshot,
            "zoom_in": self._show_zoom_in,
            "zoom_out": self._show_zoom_out,
            "zoom_normal": self._show_zoom_normal,
        }

        self.new_view_action = self._action_from_contract_spec(
            EDITOR_ACTIONS["new_view"],
            editor_handlers["new_view"],
        )
        self.toggle_fullscreen_action = self._action_from_contract_spec(
            EDITOR_ACTIONS["toggle_fullscreen"],
            editor_handlers["toggle_fullscreen"],
        )
        self.take_screenshot_action = self._action_from_contract_spec(
            EDITOR_ACTIONS["take_screenshot"],
            editor_handlers["take_screenshot"],
        )
        self.zoom_in_action = self._action_from_contract_spec(
            EDITOR_ACTIONS["zoom_in"],
            editor_handlers["zoom_in"],
        )
        self.zoom_out_action = self._action_from_contract_spec(
            EDITOR_ACTIONS["zoom_out"],
            editor_handlers["zoom_out"],
        )
        self.zoom_normal_action = self._action_from_contract_spec(
            EDITOR_ACTIONS["zoom_normal"],
            editor_handlers["zoom_normal"],
        )

        editor_top_level_actions = {
            "new_view": self.new_view_action,
            "toggle_fullscreen": self.toggle_fullscreen_action,
            "take_screenshot": self.take_screenshot_action,
        }
        for action_key in EDITOR_ACTION_ORDER:
            editor_menu.addAction(editor_top_level_actions[action_key])

        editor_menu.addSeparator()

        zoom_menu = editor_menu.addMenu(EDITOR_ZOOM_MENU_TITLE)
        assert zoom_menu is not None
        editor_zoom_actions = {
            "zoom_in": self.zoom_in_action,
            "zoom_out": self.zoom_out_action,
            "zoom_normal": self.zoom_normal_action,
        }
        for action_key in EDITOR_ZOOM_ACTION_ORDER:
            zoom_menu.addAction(editor_zoom_actions[action_key])

    def _sync_checkable_action(self, action: QAction, checked: bool) -> None:
        was_blocked = action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(was_blocked)

    # ── Stub slots (Tier 2: logged NotImplementedError) ──────

    def _stub_floor_up(self) -> None:
        logger.warning("Floor Up: NotImplementedError — awaiting canvas backend")

    def _stub_floor_down(self) -> None:
        logger.warning("Floor Down: NotImplementedError — awaiting canvas backend")

    def _stub_ghost_higher(self, checked: bool) -> None:
        self._ghost_higher_enabled = checked
        self._canvas.set_ghost_higher(checked)
        logger.warning(
            "Ghost Higher Floors %s: NotImplementedError — awaiting canvas backend",
            "ON" if checked else "OFF",
        )

    def _stub_show_lower(self, checked: bool) -> None:
        self._show_lower_enabled = checked
        self._canvas.set_show_lower(checked)
        logger.warning(
            "Show Lower Floors %s: NotImplementedError — awaiting canvas backend",
            "ON" if checked else "OFF",
        )

    def _describe_floor(self, z: int) -> str:
        if z < 7:
            return "Above Ground"
        if z == 7:
            return "Ground"
        return "Underground"

    def _set_current_position(
        self,
        x: int,
        y: int,
        z: int,
        *,
        track_history: bool = False,
        announce: bool = False,
    ) -> None:
        next_position = (
            max(0, min(65000, x)),
            max(0, min(65000, y)),
            max(0, min(15, z)),
        )
        current = (self._current_x, self._current_y, self._current_z)
        if track_history and next_position != current:
            self._previous_position = current

        self._current_x, self._current_y, self._current_z = next_position
        self._coord_label.setText(
            f"Pos: (X: {self._current_x}, Y: {self._current_y}, Z: {self._current_z:02d})"
        )
        self._items_label.setText(
            f"Floor {self._current_z} ({self._describe_floor(self._current_z)})"
        )
        if self.minimap_dock is not None:
            self.minimap_dock.pos_label.setText(f"Z: {self._current_z:02d}")

        self._sync_floor_actions(self._current_z)
        self._sync_canvas_shell_state()

        if announce:
            self._status_bar().showMessage(
                "Navigation focus moved to "
                f"{self._current_x}, {self._current_y}, {self._current_z:02d}",
                3000,
            )

    def _select_floor(self, floor: int) -> None:
        self._set_current_position(
            self._current_x,
            self._current_y,
            floor,
            track_history=True,
        )

    def _floor_up(self) -> None:
        if self._current_z <= 0:
            self._status_bar().showMessage("Already at the top-most floor", 2000)
            return
        self._select_floor(self._current_z - 1)

    def _floor_down(self) -> None:
        if self._current_z >= 15:
            self._status_bar().showMessage("Already at the lowest floor", 2000)
            return
        self._select_floor(self._current_z + 1)

    def _sync_canvas_shell_state(self) -> None:
        self._canvas.set_position(self._current_x, self._current_y, self._current_z)
        self._canvas.set_floor(self._current_z)
        self._canvas.set_zoom(self._zoom_percent)
        self._canvas.set_show_grid(self._show_grid_enabled)
        self._canvas.set_ghost_higher(self._ghost_higher_enabled)
        self._canvas.set_show_lower(self._show_lower_enabled)

    def _sync_floor_actions(self, floor: int) -> None:
        floor = max(0, min(15, floor))
        for index, action in enumerate(self.floor_actions):
            self._sync_checkable_action(action, index == floor)
        if self.floor_up_action is not None:
            self.floor_up_action.setEnabled(floor > 0)
        if self.floor_down_action is not None:
            self.floor_down_action.setEnabled(floor < 15)
        if self.minimap_dock is not None:
            self.minimap_dock.z_up_btn.setEnabled(floor > 0)
            self.minimap_dock.z_down_btn.setEnabled(floor < 15)

    def _restore_window_state(self) -> None:
        geometry = self._settings.value("main_window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self._settings.value("main_window/state")
        if state is not None:
            self.restoreState(state)

        current_x, current_y, current_z = self._coerce_position(
            self._settings.value("main_window/position", list(self.DEFAULT_POSITION)),
            self.DEFAULT_POSITION,
        )
        self._sync_checkable_action(
            self.show_grid_action,
            self._coerce_bool(self._settings.value("main_window/show_grid", False), False),
        )
        self._show_grid_enabled = self.show_grid_action.isChecked()
        self._sync_checkable_action(
            self.ghost_higher_action,
            self._coerce_bool(
                self._settings.value("main_window/ghost_higher", False),
                False,
            ),
        )
        self._ghost_higher_enabled = self.ghost_higher_action.isChecked()
        self._sync_checkable_action(
            self.show_lower_action,
            self._coerce_bool(self._settings.value("main_window/show_lower", True), True),
        )
        self._show_lower_enabled = self.show_lower_action.isChecked()
        previous = self._settings.value("main_window/previous_position")
        self._previous_position = (
            self._coerce_position(previous, self.DEFAULT_POSITION)
            if isinstance(previous, (list, tuple)) and len(previous) == 3
            else None
        )
        self._set_current_position(current_x, current_y, current_z)

    def _coerce_int(self, raw: object, default: int) -> int:
        try:
            return int(str(raw))
        except (TypeError, ValueError):
            return default

    def _coerce_position(
        self,
        raw: object,
        default: tuple[int, int, int],
    ) -> tuple[int, int, int]:
        if isinstance(raw, (list, tuple)) and len(raw) == 3:
            return (
                self._coerce_int(raw[0], default[0]),
                self._coerce_int(raw[1], default[1]),
                self._coerce_int(raw[2], default[2]),
            )
        return default

    def _coerce_bool(self, raw: object, default: bool) -> bool:
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, str):
            normalized = raw.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        return default

    def closeEvent(self, event: QCloseEvent | None) -> None:  # noqa: N802
        self._settings.setValue("main_window/geometry", self.saveGeometry())
        self._settings.setValue("main_window/state", self.saveState())
        self._settings.setValue(
            "main_window/position",
            [self._current_x, self._current_y, self._current_z],
        )
        self._settings.setValue(
            "main_window/previous_position",
            list(self._previous_position) if self._previous_position else None,
        )
        self._settings.setValue("main_window/show_grid", self._show_grid_enabled)
        self._settings.setValue("main_window/ghost_higher", self._ghost_higher_enabled)
        self._settings.setValue("main_window/show_lower", self._show_lower_enabled)
        self._settings.sync()
        super().closeEvent(event)
