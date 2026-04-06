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
from pyrme.ui.dialogs import FindItemDialog, MapPropertiesDialog
from pyrme.ui.docks import BrushPaletteDock, MinimapDock, PropertiesDock, WaypointsDock
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
        self.setStyleSheet(f"QMainWindow {{ background-color: {THEME.void_black.name()}; }}")

    def _setup_menu_bar(self) -> None:
        """Create the main menu bar."""
        menu_bar = self.menuBar()
        assert menu_bar is not None
        menu_bar.setFont(TYPOGRAPHY.ui_label())

        # File menu
        file_menu = menu_bar.addMenu("&File")
        assert file_menu is not None
        file_menu.addAction(self._action("&New Map", "Ctrl+N"))
        file_menu.addAction(self._action("&Open Map...", "Ctrl+O"))
        file_menu.addSeparator()
        file_menu.addAction(self._action("&Save", "Ctrl+S"))
        file_menu.addAction(self._action("Save &As...", "Ctrl+Shift+S"))
        file_menu.addSeparator()
        file_menu.addAction(self._action("&Preferences...", "Ctrl+,"))
        file_menu.addSeparator()
        quit_action = self._action("&Quit", "Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        assert edit_menu is not None
        edit_menu.addAction(self._action("&Undo", "Ctrl+Z"))
        edit_menu.addAction(self._action("&Redo", "Ctrl+Y"))
        edit_menu.addSeparator()
        edit_menu.addAction(self._action("Cu&t", "Ctrl+X"))
        edit_menu.addAction(self._action("&Copy", "Ctrl+C"))
        edit_menu.addAction(self._action("&Paste", "Ctrl+V"))
        edit_menu.addAction(self._action("&Delete", "Del"))
        edit_menu.addSeparator()
        find_action = self._action("&Find Item...", "Ctrl+F")
        find_action.triggered.connect(self._show_find_item)
        edit_menu.addAction(find_action)
        edit_menu.addAction(self._action("&Replace Items...", "Ctrl+H"))
        edit_menu.addSeparator()
        edit_menu.addAction(self._action("&Select All", "Ctrl+A"))

        # View menu
        view_menu = menu_bar.addMenu("&View")
        assert view_menu is not None
        view_menu.addAction(self._action("Zoom &In", "Ctrl+="))
        view_menu.addAction(self._action("Zoom &Out", "Ctrl+-"))
        view_menu.addAction(self._action("Zoom &Reset", "Ctrl+0"))
        view_menu.addSeparator()
        view_menu.addAction(self._action("&Go to Position...", "Ctrl+G"))
        view_menu.addSeparator()
        view_menu.addAction(self._action("Toggle &Grid", "G"))
        view_menu.addAction(self._action("Toggle &Minimap", "M"))

        # Map menu
        map_menu = menu_bar.addMenu("&Map")
        assert map_menu is not None

        map_prop_action = self._action("Map &Properties...")
        map_prop_action.triggered.connect(self._show_map_properties)
        map_menu.addAction(map_prop_action)

        map_menu.addAction(self._action("Map &Statistics..."))
        map_menu.addSeparator()
        map_menu.addAction(self._action("&Clean Map"))
        map_menu.addAction(self._action("Clean &Invalid Tiles"))

        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        assert tools_menu is not None
        tools_menu.addAction(self._action("&Extension Manager..."))
        tools_menu.addAction(self._action("&Tileset Editor..."))
        tools_menu.addSeparator()
        tools_menu.addAction(self._action("AI &Assistant...", "Ctrl+Shift+A"))

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        assert help_menu is not None
        help_menu.addAction(self._action("&About Noct Map Editor"))
        help_menu.addAction(self._action("About &Qt"))

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
        floor_toolbar = QToolBar("Floors")
        floor_toolbar.setObjectName("floor_toolbar")
        floor_toolbar.setMovable(True)
        floor_group = QActionGroup(self)
        floor_group.setExclusive(True)
        for i in range(16):
            action = self._action(f"F{i}")
            action.setCheckable(True)
            floor_group.addAction(action)
            floor_toolbar.addAction(action)
            if i == 7:  # Default to ground floor (Z=7 usually, from 0-15)
                action.setChecked(True)

        floor_toolbar.addSeparator()

        # Floor navigation actions (stub slots)
        act_floor_up = self._action("Floor ▲", "Ctrl+PgUp")
        act_floor_up.setToolTip("Go to higher floor (Ctrl+PageUp)")
        act_floor_up.triggered.connect(self._stub_floor_up)
        floor_toolbar.addAction(act_floor_up)

        act_floor_down = self._action("Floor ▼", "Ctrl+PgDown")
        act_floor_down.setToolTip("Go to lower floor (Ctrl+PageDown)")
        act_floor_down.triggered.connect(self._stub_floor_down)
        floor_toolbar.addAction(act_floor_down)

        floor_toolbar.addSeparator()

        # Floor visibility toggle actions (checkable, stub slots)
        act_ghost = self._action("Ghost Higher")
        act_ghost.setCheckable(True)
        act_ghost.setToolTip("Show transparent overlay of higher floors")
        act_ghost.toggled.connect(self._stub_ghost_higher)
        floor_toolbar.addAction(act_ghost)

        act_show_lower = self._action("Show Lower")
        act_show_lower.setCheckable(True)
        act_show_lower.setChecked(True)
        act_show_lower.setToolTip("Show floors below the current one")
        act_show_lower.toggled.connect(self._stub_show_lower)
        floor_toolbar.addAction(act_show_lower)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, floor_toolbar)

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
            f"  color: {THEME.ash_lavender.name()};"
            "  font-size: 18px;"
            "  font-weight: 300;"
            f"  background-color: {THEME.void_black.name()};"
            f"  border: 1px solid {THEME.ghost_border.name()};"
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
        self._coord_label.setStyleSheet(f"padding: 0 12px; color: {THEME.ash_lavender.name()};")
        status_bar.addPermanentWidget(self._coord_label)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setFont(TYPOGRAPHY.ui_label())
        self._zoom_label.setStyleSheet(f"padding: 0 12px; color: {THEME.ash_lavender.name()};")
        status_bar.addPermanentWidget(self._zoom_label)

        self._items_label = QLabel("Floor 7 (Ground)")
        self._items_label.setFont(TYPOGRAPHY.ui_label())
        self._items_label.setStyleSheet(f"padding: 0 12px; color: {THEME.ash_lavender.name()};")
        status_bar.addPermanentWidget(self._items_label)

        status_bar.showMessage(f"{__app_name__} v{__version__} — Ready", 5000)

    def _action(self, text: str, shortcut: str | None = None) -> QAction:
        """Helper to create a QAction."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
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
