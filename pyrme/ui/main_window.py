"""Noct Map Editor Main Window – The editor shell."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS
from pyrme.ui.dialogs import FindItemDialog, MapPropertiesDialog
from pyrme.ui.docks import BrushPaletteDock, MinimapDock, PropertiesDock, WaypointsDock
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main editor window for Noct Map Editor."""

    # Responsive design: desktop-only application target
    WINDOW_MIN_SIZE = QSize(1280, 720)
    WINDOW_DEFAULT_SIZE = QSize(1600, 1000)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_window()
        self._setup_menu_bar()
        self._setup_toolbars()
        self._setup_central_widget()
        self._setup_docks()
        self._setup_status_bar()

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
        self._menus: dict[str, object] = {}
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
        self.show_grid_action = self._action_from_spec("show_grid", self._toggle_show_grid)
        self.show_grid_action.setCheckable(True)
        self.ghost_higher_action = self._action_from_spec("ghost_higher_floors")
        self.ghost_higher_action.setCheckable(True)

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
        self.floor_up_action.triggered.connect(self._stub_floor_up)
        self.floor_toolbar.addAction(self.floor_up_action)

        self.floor_down_action = self._action("Floor Down", "Ctrl+PgDown")
        self.floor_down_action.setObjectName("floor_down_action")
        self.floor_down_action.setToolTip("Go to lower floor (Ctrl+PageDown)")
        self.floor_down_action.triggered.connect(self._stub_floor_down)
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

    def _setup_central_widget(self) -> None:
        """Set up the central canvas area (placeholder until Milestone 4)."""
        canvas_placeholder = QLabel(
            f"🗺️ {__app_name__} Canvas\n\n"
            "Rust-backed wgpu renderer will be integrated in Milestone 4.\n"
            "This is the opaque, void-black mapping area."
        )
        canvas_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_placeholder.setStyleSheet(
            "QLabel {"
            f"  color: {qss_color(THEME.ash_lavender)};"
            "  font-size: 18px;"
            "  font-weight: 300;"
            f"  background-color: {qss_color(THEME.void_black)};"
            f"  border: 1px solid {qss_color(THEME.ghost_border)};"
            "  border-radius: 8px;"
            "  padding: 40px;"
            "}"
        )
        self.setCentralWidget(canvas_placeholder)

    def _show_map_properties(self) -> None:
        """Show the map properties dialog."""
        dialog = MapPropertiesDialog(self)
        dialog.exec()

    def _show_find_item(self) -> None:
        """Show the find item dialog."""
        dialog = FindItemDialog(self)
        dialog.exec()

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

    def _setup_docks(self) -> None:
        """Create dock widgets for palettes and tools using Glassmorphism."""
        # Brush Palette dock (left side)
        palette_dock = BrushPaletteDock(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, palette_dock)

        # Minimap dock (right side)
        minimap_dock = MinimapDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, minimap_dock)

        # Properties dock (right side, below minimap)
        props_dock = PropertiesDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, props_dock)

        # Waypoints dock (right side, below properties)
        waypoints_dock = WaypointsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, waypoints_dock)

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

    def _action(self, text: str, shortcut: str | None = None) -> QAction:
        """Helper to create a QAction."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def _menu_label(self, title: str) -> str:
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

    # ── Stub slots (Tier 2: logged NotImplementedError) ──────

    def _stub_floor_up(self) -> None:
        logger.warning("Floor Up: NotImplementedError — awaiting canvas backend")

    def _stub_floor_down(self) -> None:
        logger.warning("Floor Down: NotImplementedError — awaiting canvas backend")

    def _stub_ghost_higher(self, checked: bool) -> None:
        logger.warning(
            "Ghost Higher Floors %s: NotImplementedError — awaiting canvas backend",
            "ON" if checked else "OFF",
        )

    def _stub_show_lower(self, checked: bool) -> None:
        logger.warning(
            "Show Lower Floors %s: NotImplementedError — awaiting canvas backend",
            "ON" if checked else "OFF",
        )
