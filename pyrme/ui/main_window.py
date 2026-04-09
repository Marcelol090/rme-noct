"""Noct Map Editor main window shell."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMenu,
    QStatusBar,
    QToolBar,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.core_bridge import (
    SHOW_FLAG_DEFAULTS,
    VIEW_FLAG_DEFAULTS,
    create_editor_shell_state,
)
from pyrme.ui.canvas_host import PlaceholderCanvasWidget
from pyrme.ui.dialogs import FindItemDialog, GotoPositionDialog, MapPropertiesDialog
from pyrme.ui.docks import (
    BrushPaletteDock,
    IngamePreviewDock,
    MinimapDock,
    PropertiesDock,
    ToolOptionsDock,
    WaypointsDock,
)
from pyrme.ui.legacy_menu_contract import (
    LEGACY_NAVIGATE_FLOOR_LABELS,
    LEGACY_TOP_LEVEL_MENUS,
    PHASE1_ACTIONS,
)
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY

logger = logging.getLogger(__name__)

CanvasFactory = Callable[[QWidget | None], QWidget]

VIEW_ACTION_SPECS = (
    ("show_all_floors", "Show all Floors", "Ctrl+W"),
    ("show_as_minimap", "Show as Minimap", "Shift+E"),
    ("show_only_colors", "Only show Colors", "Ctrl+E"),
    ("show_only_modified", "Only show Modified", "Ctrl+M"),
    ("always_show_zones", "Always show zones", None),
    ("extended_house_shader", "Extended house shader", None),
    ("show_tooltips", "Show tooltips", "Y"),
    ("show_client_box", "Show client box", "Shift+I"),
    ("ghost_loose_items", "Ghost loose items", "G"),
    ("show_shade", "Show shade", "Q"),
)

SHOW_ACTION_SPECS = (
    ("show_animation", "Show Animation", "L"),
    ("show_light", "Show Light", "Shift+L"),
    ("show_light_strength", "Show Light Strength", "Shift+K"),
    ("show_technical_items", "Show Technical Items", "Shift+T"),
    ("show_invalid_tiles", "Show Invalid Tiles", None),
    ("show_invalid_zones", "Show Invalid Zones", None),
    ("show_creatures", "Show creatures", "F"),
    ("show_spawns", "Show spawns", "S"),
    ("show_special", "Show special", "E"),
    ("show_houses", "Show houses", "Ctrl+H"),
    ("show_pathing", "Show pathing", "O"),
    ("show_towns", "Show towns", None),
    ("show_waypoints", "Show waypoints", "Shift+W"),
    ("highlight_items", "Highlight Items", "V"),
    ("highlight_locked_doors", "Highlight Locked Doors", "U"),
    ("show_wall_hooks", "Show Wall Hooks", "K"),
)


class MainWindow(QMainWindow):
    """Main editor window for Noct Map Editor."""

    WINDOW_MIN_SIZE = QSize(1280, 720)
    WINDOW_DEFAULT_SIZE = QSize(1600, 1000)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        settings: QSettings | None = None,
        canvas_factory: CanvasFactory | None = None,
        enable_docks: bool | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings or QSettings("Noct Map Editor", "Noct")
        self._canvas_factory = canvas_factory or PlaceholderCanvasWidget
        self._core = create_editor_shell_state()
        self._enable_docks = (
            enable_docks
            if enable_docks is not None
            else os.environ.get("QT_QPA_PLATFORM") != "offscreen"
        )
        self._menus: dict[str, QMenu] = {}
        self.floor_actions: list[QAction] = []
        self._navigate_floor_actions: list[QAction] = []
        self._palette_docks: list[BrushPaletteDock] = []
        self.palette_dock: BrushPaletteDock | None = None
        self.brush_palette_dock: BrushPaletteDock | None = None
        self.minimap_dock: MinimapDock | None = None
        self.props_dock: PropertiesDock | None = None
        self.properties_dock: PropertiesDock | None = None
        self.tool_options_dock: ToolOptionsDock | None = None
        self.ingame_preview_dock: IngamePreviewDock | None = None
        self.waypoints_dock: WaypointsDock | None = None
        self.toggle_minimap_action: QAction | None = None
        self.toggle_brush_palette_action: QAction | None = None
        self.toggle_properties_action: QAction | None = None
        self.toggle_waypoints_action: QAction | None = None
        self.toggle_brushes_toolbar_action: QAction | None = None
        self.toggle_position_toolbar_action: QAction | None = None
        self.toggle_floor_toolbar_action: QAction | None = None
        self.toggle_sizes_toolbar_action: QAction | None = None
        self.toggle_standard_toolbar_action: QAction | None = None
        self.brushes_toolbar: QToolBar | None = None
        self.position_toolbar: QToolBar | None = None
        self.floor_toolbar: QToolBar | None = None
        self.sizes_toolbar: QToolBar | None = None
        self.standard_toolbar: QToolBar | None = None
        self._child_views: list[MainWindow] = []
        self._last_screenshot = None
        self._position = self._core.position()
        self._previous_position: tuple[int, int, int] | None = None
        self._floor = self._core.floor()
        self._zoom_percent = self._core.zoom_percent()
        self._show_grid = self._core.show_grid()
        self._ghost_higher = self._core.ghost_higher()
        self._show_lower = self._core.show_lower()
        self._view_flags = self._core.view_flags()
        self._show_flags = self._core.show_flags()
        self._view_actions: dict[str, QAction] = {}
        self._show_actions: dict[str, QAction] = {}
        self._shell_core_available = self._core.is_native()

        self._setup_window()
        self._setup_central_widget()
        if self._enable_docks:
            self._setup_docks()
        self._setup_toolbars()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._restore_window_state()
        self._apply_shell_state_to_canvas()
        self._update_status_labels()

    def _setup_window(self) -> None:
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(self.WINDOW_MIN_SIZE)
        self.resize(self.WINDOW_DEFAULT_SIZE)
        self.setDockNestingEnabled(True)
        self.setStyleSheet(
            f"QMainWindow {{ background-color: {qss_color(THEME.void_black)}; }}"
        )

    def _setup_central_widget(self) -> None:
        self._canvas = self._canvas_factory(self)
        self.setCentralWidget(self._canvas)

    def _setup_docks(self) -> None:
        self.palette_dock = BrushPaletteDock(self)
        self.brush_palette_dock = self.palette_dock
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.palette_dock)
        self._palette_docks.append(self.palette_dock)

        self.minimap_dock = MinimapDock(self)
        self.minimap_dock.z_up_btn.clicked.connect(self._floor_up)
        self.minimap_dock.z_down_btn.clicked.connect(self._floor_down)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.minimap_dock)

        self.props_dock = PropertiesDock(self)
        self.properties_dock = self.props_dock
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.props_dock)

        self.tool_options_dock = ToolOptionsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tool_options_dock)

        self.ingame_preview_dock = IngamePreviewDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ingame_preview_dock)

        self.waypoints_dock = WaypointsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.waypoints_dock)

        self.tabifyDockWidget(self.minimap_dock, self.props_dock)
        self.tabifyDockWidget(self.props_dock, self.tool_options_dock)
        self.tabifyDockWidget(self.tool_options_dock, self.ingame_preview_dock)
        self.tabifyDockWidget(self.ingame_preview_dock, self.waypoints_dock)

    def _setup_toolbars(self) -> None:
        self.new_view_action = self._action("New View", "Ctrl+Shift+N")
        self.new_view_action.triggered.connect(self._open_new_view)
        self.toggle_fullscreen_action = self._action("Enter Fullscreen", "F11")
        self.toggle_fullscreen_action.triggered.connect(self._toggle_fullscreen)
        self.take_screenshot_action = self._action("Take Screenshot", "F10")
        self.take_screenshot_action.triggered.connect(self._capture_screenshot)
        self.zoom_in_action = self._action("Zoom In", "Ctrl++")
        self.zoom_in_action.triggered.connect(lambda: self._set_zoom(self._zoom_percent + 10))
        self.zoom_out_action = self._action("Zoom Out", "Ctrl+-")
        self.zoom_out_action.triggered.connect(lambda: self._set_zoom(self._zoom_percent - 10))
        self.zoom_normal_action = self._action("Zoom Normal", "Ctrl+0")
        self.zoom_normal_action.triggered.connect(lambda: self._set_zoom(100))

        self.brushes_toolbar = self._create_toolbar("Brushes", "brushes_toolbar")
        self.brushes_toolbar.addAction(self._action("Select"))
        self.brushes_toolbar.addAction(self._action("Draw"))
        self.brushes_toolbar.addAction(self._action("Erase"))
        self.brushes_toolbar.addAction(self._action("Fill"))
        self.brushes_toolbar.addSeparator()
        self.brushes_toolbar.addAction(self._action("Move"))
        self.addToolBar(self.brushes_toolbar)

        self.position_toolbar = self._create_toolbar("Position", "position_toolbar")
        self.goto_position_action = self._phase1_action(
            "goto_position", self._show_goto_position
        )
        self.goto_previous_position_action = self._phase1_action(
            "goto_previous_position", self._goto_previous_position
        )
        self.jump_to_brush_action = self._phase1_action(
            "jump_to_brush", self._stub_jump_to_brush
        )
        self.jump_to_item_action = self._phase1_action(
            "jump_to_item", self._stub_jump_to_item
        )
        self.position_toolbar.addAction(self.goto_position_action)
        self.position_toolbar.addAction(self.goto_previous_position_action)
        self.position_toolbar.addSeparator()
        self.position_toolbar.addAction(self.jump_to_brush_action)
        self.position_toolbar.addAction(self.jump_to_item_action)
        self.addToolBar(self.position_toolbar)

        self.floor_toolbar = self._create_toolbar("Floors", "floor_toolbar")
        self.floor_up_action = self._action("Floor Up", "Ctrl+PgUp")
        self.floor_up_action.setObjectName("floor_up_action")
        self.floor_up_action.triggered.connect(self._floor_up)
        self.floor_down_action = self._action("Floor Down", "Ctrl+PgDown")
        self.floor_down_action.setObjectName("floor_down_action")
        self.floor_down_action.triggered.connect(self._floor_down)
        self.ghost_higher_toolbar_action = self._action(
            "Ghost Higher Floors",
            PHASE1_ACTIONS["ghost_higher_floors"].shortcut,
        )
        self.ghost_higher_toolbar_action.setCheckable(True)
        self.ghost_higher_toolbar_action.toggled.connect(
            self._toggle_ghost_higher_from_toolbar
        )
        self.show_lower_action = self._action("Show Lower Floors")
        self.show_lower_action.setObjectName("show_lower_action")
        self.show_lower_action.setCheckable(True)
        self.show_lower_action.setChecked(True)
        self.show_lower_action.toggled.connect(self._set_show_lower)
        self.floor_actions = self._create_floor_actions()
        for action in self.floor_actions:
            self.floor_toolbar.addAction(action)
        self.floor_toolbar.addSeparator()
        self.floor_toolbar.addAction(self.floor_up_action)
        self.floor_toolbar.addAction(self.floor_down_action)
        self.floor_toolbar.addSeparator()
        self.floor_toolbar.addAction(self.ghost_higher_toolbar_action)
        self.floor_toolbar.addAction(self.show_lower_action)
        self.addToolBar(self.floor_toolbar)

        self.sizes_toolbar = self._create_toolbar("Sizes", "sizes_toolbar")
        self.sizes_toolbar.addAction(self.zoom_in_action)
        self.sizes_toolbar.addAction(self.zoom_out_action)
        self.sizes_toolbar.addAction(self.zoom_normal_action)
        self.addToolBar(self.sizes_toolbar)

        self.standard_toolbar = self._create_toolbar("Standard", "standard_toolbar")
        self.standard_toolbar.addAction(self._action("New Map", "Ctrl+N"))
        self.standard_toolbar.addAction(self._action("Open Map...", "Ctrl+O"))
        self.standard_toolbar.addAction(self._action("Save", "Ctrl+S"))
        self.standard_toolbar.addAction(self._action("Save As...", "Ctrl+Shift+S"))
        self.standard_toolbar.addSeparator()
        self.standard_toolbar.addAction(self._action("Preferences...", "Ctrl+,"))
        self.standard_toolbar.addSeparator()
        quit_action = self._action("Quit", "Ctrl+Q")
        quit_action.triggered.connect(self.close)
        self.standard_toolbar.addAction(quit_action)
        self.addToolBar(self.standard_toolbar)

    def _setup_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        assert menu_bar is not None
        menu_bar.setFont(TYPOGRAPHY.ui_label())

        for name in LEGACY_TOP_LEVEL_MENUS:
            menu = menu_bar.addMenu(name)
            assert menu is not None
            self._menus[name] = menu

        self._populate_file_menu()
        self._populate_edit_menu()
        self._populate_editor_menu()
        self._populate_search_menu()
        self._populate_map_menu()
        self._populate_selection_menu()
        self._populate_show_menu()
        self._populate_view_menu()
        self._populate_navigate_menu()
        self._populate_window_menu()
        self._populate_experimental_menu()
        self._populate_scripts_menu()
        self._populate_about_menu()

    def _populate_file_menu(self) -> None:
        menu = self._menus["File"]
        menu.addAction(self._action("New...", "Ctrl+N"))
        menu.addAction(self._action("Open...", "Ctrl+O"))
        menu.addAction(self._action("Save", "Ctrl+S"))
        menu.addAction(self._action("Save As...", "Ctrl+Alt+S"))
        menu.addAction(self._action("Generate Map"))
        close_action = self._action("Close", "Ctrl+Q")
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        menu.addSeparator()

        import_menu = menu.addMenu("Import")
        assert import_menu is not None
        import_menu.addAction(self._action("Import Map..."))
        import_menu.addAction(self._action("Import Monsters/NPC..."))

        export_menu = menu.addMenu("Export")
        assert export_menu is not None
        export_menu.addAction(self._action("Export Minimap..."))
        export_menu.addAction(self._action("Export Tilesets..."))

        reload_menu = menu.addMenu("Reload")
        assert reload_menu is not None
        reload_menu.addAction(self._action("Reload", "F5"))

        menu.addSeparator()
        recent_files_menu = menu.addMenu("Recent Files")
        assert recent_files_menu is not None
        menu.addAction(self._action("Preferences"))
        exit_action = self._action("Exit")
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

    def _populate_edit_menu(self) -> None:
        menu = self._menus["Edit"]
        menu.addAction(self._action("Undo", "Ctrl+Z"))
        menu.addAction(self._action("Redo", "Ctrl+Shift+Z"))
        menu.addSeparator()
        self.replace_items_action = self._phase1_action(
            "replace_items", self._stub_replace_items
        )
        menu.addAction(self.replace_items_action)
        menu.addSeparator()

        border_options_menu = menu.addMenu("Border Options")
        assert border_options_menu is not None
        border_options_menu.addAction(self._action("Border Automagic", "A"))
        border_options_menu.addSeparator()
        border_options_menu.addAction(self._action("Borderize Selection", "Ctrl+B"))
        border_options_menu.addAction(self._action("Borderize Map"))
        border_options_menu.addAction(self._action("Randomize Selection"))
        border_options_menu.addAction(self._action("Randomize Map"))

        other_options_menu = menu.addMenu("Other Options")
        assert other_options_menu is not None
        other_options_menu.addAction(self._action("Remove Items by ID...", "Ctrl+Shift+R"))
        other_options_menu.addAction(self._action("Remove all Corpses..."))
        other_options_menu.addAction(self._action("Remove all Unreachable Tiles..."))
        other_options_menu.addAction(self._action("Clear Invalid Houses"))
        other_options_menu.addAction(self._action("Clear Modified State"))

        menu.addSeparator()
        menu.addAction(self._action("Cut", "Ctrl+X"))
        menu.addAction(self._action("Copy", "Ctrl+C"))
        menu.addAction(self._action("Paste", "Ctrl+V"))

    def _populate_editor_menu(self) -> None:
        menu = self._menus["Editor"]
        menu.addAction(self.new_view_action)
        menu.addAction(self.toggle_fullscreen_action)
        menu.addAction(self.take_screenshot_action)
        menu.addSeparator()

        zoom_menu = menu.addMenu("Zoom")
        assert zoom_menu is not None
        zoom_menu.addAction(self.zoom_in_action)
        zoom_menu.addAction(self.zoom_out_action)
        zoom_menu.addAction(self.zoom_normal_action)

    def _populate_search_menu(self) -> None:
        menu = self._menus["Search"]
        self.find_item_action = self._phase1_action("find_item", self._show_find_item)
        menu.addAction(self.find_item_action)
        menu.addSeparator()
        menu.addAction(self._action("Find Unique"))
        menu.addAction(self._action("Find Action"))
        menu.addAction(self._action("Find Container"))
        menu.addAction(self._action("Find Writeable"))
        menu.addSeparator()
        menu.addAction(self._action("Find Everything"))

    def _populate_map_menu(self) -> None:
        menu = self._menus["Map"]
        menu.addAction(self._action("Edit Towns", "Ctrl+T"))
        menu.addSeparator()
        menu.addAction(self._action("Cleanup invalid tiles..."))
        menu.addAction(self._action("Cleanup invalid zones..."))
        self.map_properties_action = self._phase1_action(
            "map_properties", self._show_map_properties
        )
        self.map_statistics_action = self._phase1_action(
            "map_statistics", self._stub_map_statistics
        )
        menu.addAction(self.map_properties_action)
        menu.addAction(self.map_statistics_action)

    def _populate_selection_menu(self) -> None:
        menu = self._menus["Selection"]
        menu.addAction(self._action("Replace Items on Selection"))
        menu.addAction(self._action("Find Item on Selection"))
        menu.addAction(self._action("Remove Item on Selection"))
        menu.addSeparator()

        find_on_selection_menu = menu.addMenu("Find on Selection")
        assert find_on_selection_menu is not None
        find_on_selection_menu.addAction(self._action("Find Everything"))
        find_on_selection_menu.addSeparator()
        find_on_selection_menu.addAction(self._action("Find Unique"))
        find_on_selection_menu.addAction(self._action("Find Action"))
        find_on_selection_menu.addAction(self._action("Find Container"))
        find_on_selection_menu.addAction(self._action("Find Writeable"))

        menu.addSeparator()
        selection_mode_menu = menu.addMenu("Selection Mode")
        assert selection_mode_menu is not None
        selection_mode_menu.addAction(self._action("Compensate Selection"))
        selection_mode_menu.addSeparator()
        selection_mode_menu.addAction(self._action("Current Floor"))
        selection_mode_menu.addAction(self._action("Lower Floors"))
        selection_mode_menu.addAction(self._action("Visible Floors"))

        menu.addSeparator()
        menu.addAction(self._action("Borderize Selection"))
        menu.addAction(self._action("Randomize Selection"))

    def _populate_view_menu(self) -> None:
        menu = self._menus["View"]
        for flag_name, text, shortcut in VIEW_ACTION_SPECS[:6]:
            action = self._toggle_flag_action(
                text,
                shortcut,
                checked=self._view_flags.get(flag_name, VIEW_FLAG_DEFAULTS[flag_name]),
                slot=lambda checked, name=flag_name: self._set_view_flag(name, checked),
            )
            self._view_actions[flag_name] = action
            menu.addAction(action)
        menu.addSeparator()
        tooltips_action = self._toggle_flag_action(
            "Show tooltips",
            "Y",
            checked=self._view_flags.get("show_tooltips", VIEW_FLAG_DEFAULTS["show_tooltips"]),
            slot=lambda checked: self._set_view_flag("show_tooltips", checked),
        )
        self._view_actions["show_tooltips"] = tooltips_action
        menu.addAction(tooltips_action)
        menu.addAction(self.show_grid_action)
        client_box_action = self._toggle_flag_action(
            "Show client box",
            "Shift+I",
            checked=self._view_flags.get(
                "show_client_box",
                VIEW_FLAG_DEFAULTS["show_client_box"],
            ),
            slot=lambda checked: self._set_view_flag("show_client_box", checked),
        )
        self._view_actions["show_client_box"] = client_box_action
        menu.addAction(client_box_action)
        menu.addSeparator()
        ghost_loose_items_action = self._toggle_flag_action(
            "Ghost loose items",
            "G",
            checked=self._view_flags.get(
                "ghost_loose_items",
                VIEW_FLAG_DEFAULTS["ghost_loose_items"],
            ),
            slot=lambda checked: self._set_view_flag("ghost_loose_items", checked),
        )
        self._view_actions["ghost_loose_items"] = ghost_loose_items_action
        menu.addAction(ghost_loose_items_action)
        menu.addAction(self.ghost_higher_action)
        show_shade_action = self._toggle_flag_action(
            "Show shade",
            "Q",
            checked=self._view_flags.get("show_shade", VIEW_FLAG_DEFAULTS["show_shade"]),
            slot=lambda checked: self._set_view_flag("show_shade", checked),
        )
        self._view_actions["show_shade"] = show_shade_action
        menu.addAction(show_shade_action)

    def _populate_show_menu(self) -> None:
        menu = self._menus["Show"]
        self.show_grid_action = self._phase1_action("show_grid", self._toggle_show_grid)
        self.show_grid_action.setCheckable(True)
        self.show_grid_action.setChecked(self._show_grid)
        self.ghost_higher_action = self._phase1_action(
            "ghost_higher_floors", self._toggle_ghost_higher_from_menu
        )
        self.ghost_higher_action.setObjectName("ghost_higher_action")
        self.ghost_higher_action.setCheckable(True)
        self.ghost_higher_action.setChecked(self._ghost_higher)
        for flag_name, text, shortcut in SHOW_ACTION_SPECS[:6]:
            action = self._toggle_flag_action(
                text,
                shortcut,
                checked=self._show_flags.get(flag_name, SHOW_FLAG_DEFAULTS[flag_name]),
                slot=lambda checked, name=flag_name: self._set_show_flag(name, checked),
            )
            self._show_actions[flag_name] = action
            menu.addAction(action)
        menu.addSeparator()
        for flag_name, text, shortcut in SHOW_ACTION_SPECS[6:13]:
            action = self._toggle_flag_action(
                text,
                shortcut,
                checked=self._show_flags.get(flag_name, SHOW_FLAG_DEFAULTS[flag_name]),
                slot=lambda checked, name=flag_name: self._set_show_flag(name, checked),
            )
            self._show_actions[flag_name] = action
            menu.addAction(action)
        menu.addSeparator()
        for flag_name, text, shortcut in SHOW_ACTION_SPECS[13:]:
            action = self._toggle_flag_action(
                text,
                shortcut,
                checked=self._show_flags.get(flag_name, SHOW_FLAG_DEFAULTS[flag_name]),
                slot=lambda checked, name=flag_name: self._set_show_flag(name, checked),
            )
            self._show_actions[flag_name] = action
            menu.addAction(action)

    def _populate_navigate_menu(self) -> None:
        menu = self._menus["Navigate"]
        menu.addAction(self.goto_previous_position_action)
        menu.addAction(self.goto_position_action)
        menu.addAction(self.jump_to_brush_action)
        menu.addAction(self.jump_to_item_action)
        menu.addSeparator()

        floor_menu = menu.addMenu("Floor")
        assert floor_menu is not None
        for action in self._navigate_floor_actions:
            floor_menu.addAction(action)

    def _populate_window_menu(self) -> None:
        menu = self._menus["Window"]
        self.toggle_minimap_action = self._dock_toggle_action("Minimap", self.minimap_dock)
        self.toggle_brush_palette_action = self._dock_toggle_action(
            "Tool Options", self.tool_options_dock
        )
        self.toggle_properties_action = self._dock_toggle_action(
            "Tile Properties", self.props_dock
        )
        self.toggle_waypoints_action = self._dock_toggle_action(
            "In-game Preview", self.ingame_preview_dock
        )
        menu.addAction(self.toggle_minimap_action)
        menu.addAction(self.toggle_brush_palette_action)
        menu.addAction(self.toggle_properties_action)
        menu.addAction(self.toggle_waypoints_action)
        menu.addSeparator()

        new_palette_action = self._action("New Palette")
        new_palette_action.triggered.connect(self._new_palette_window)
        new_palette_action.setEnabled(self.palette_dock is not None)
        menu.addAction(new_palette_action)

        palette_menu = menu.addMenu("Palette")
        assert palette_menu is not None
        palette_menu.addAction(self._palette_action("Terrain", self._select_palette_terrain))
        palette_menu.addAction(self._palette_action("Doodad", self._select_palette_doodad))
        palette_menu.addAction(self._palette_action("Item", self._select_palette_item))
        palette_menu.addAction(
            self._palette_action("Collection", self._select_palette_collection)
        )
        palette_menu.addAction(self._palette_action("House", self._select_palette_house))
        palette_menu.addAction(self._palette_action("Creature", self._select_palette_creature))
        palette_menu.addAction(self._palette_action("Waypoint", self._select_palette_waypoint))
        palette_menu.addAction(self._palette_action("RAW", self._select_palette_raw))
        palette_menu.setEnabled(self.palette_dock is not None)

        toolbars_menu = menu.addMenu("Toolbars")
        assert toolbars_menu is not None
        self.toggle_brushes_toolbar_action = self._toolbar_toggle_action(self.brushes_toolbar)
        self.toggle_position_toolbar_action = self._toolbar_toggle_action(self.position_toolbar)
        self.toggle_floor_toolbar_action = self._toolbar_toggle_action(self.floor_toolbar)
        self.toggle_sizes_toolbar_action = self._toolbar_toggle_action(self.sizes_toolbar)
        self.toggle_standard_toolbar_action = self._toolbar_toggle_action(
            self.standard_toolbar
        )
        toolbars_menu.addAction(self.toggle_brushes_toolbar_action)
        toolbars_menu.addAction(self.toggle_position_toolbar_action)
        toolbars_menu.addAction(self.toggle_floor_toolbar_action)
        toolbars_menu.addAction(self.toggle_sizes_toolbar_action)
        toolbars_menu.addAction(self.toggle_standard_toolbar_action)

    def _populate_scripts_menu(self) -> None:
        menu = self._menus["Scripts"]
        menu.addAction(self._action("Script Manager..."))
        menu.addSeparator()
        menu.addAction(self._action("Open Scripts Folder"))
        menu.addAction(self._action("Reload Scripts", "Ctrl+Shift+F5"))

    def _populate_about_menu(self) -> None:
        menu = self._menus["About"]
        menu.addAction(self._action("Extensions...", "F2"))
        menu.addAction(self._action("Goto Website", "F3"))
        menu.addAction(self._action("About...", "F1"))

    def _populate_experimental_menu(self) -> None:
        self._menus["Experimental"].addAction(self._action("Fog in light view"))

    def _setup_status_bar(self) -> None:
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self._coord_label = QLabel()
        self._coord_label.setFont(TYPOGRAPHY.coordinate_display())
        self._coord_label.setStyleSheet(
            f"padding: 0 12px; color: {qss_color(THEME.ash_lavender)};"
        )
        status_bar.addPermanentWidget(self._coord_label)

        self._zoom_label = QLabel()
        self._zoom_label.setFont(TYPOGRAPHY.ui_label())
        self._zoom_label.setStyleSheet(
            f"padding: 0 12px; color: {qss_color(THEME.ash_lavender)};"
        )
        status_bar.addPermanentWidget(self._zoom_label)

        self._floor_label = QLabel()
        self._floor_label.setFont(TYPOGRAPHY.ui_label())
        self._floor_label.setStyleSheet(
            f"padding: 0 12px; color: {qss_color(THEME.ash_lavender)};"
        )
        status_bar.addPermanentWidget(self._floor_label)
        status_bar.showMessage(f"{__app_name__} v{__version__} - Ready", 5000)

    def _status_bar(self) -> QStatusBar:
        status_bar = self.statusBar()
        assert status_bar is not None
        return status_bar

    def _create_toolbar(self, title: str, object_name: str) -> QToolBar:
        toolbar = QToolBar(title, self)
        toolbar.setObjectName(object_name)
        toolbar.setMovable(True)
        return toolbar

    def _create_floor_actions(self) -> list[QAction]:
        toolbar_group = QActionGroup(self)
        toolbar_group.setExclusive(True)
        navigate_group = QActionGroup(self)
        navigate_group.setExclusive(True)
        actions: list[QAction] = []
        self._navigate_floor_actions = []
        for floor in range(16):
            action = self._action(f"F{floor}")
            action.setObjectName(f"floor_{floor}")
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, value=floor: self._set_floor(value) if checked else None
            )
            toolbar_group.addAction(action)
            actions.append(action)

            navigate_action = self._action(LEGACY_NAVIGATE_FLOOR_LABELS[floor])
            navigate_action.setCheckable(True)
            navigate_action.triggered.connect(
                lambda checked, value=floor: self._set_floor(value) if checked else None
            )
            navigate_group.addAction(navigate_action)
            self._navigate_floor_actions.append(navigate_action)

            if floor == self._floor:
                action.setChecked(True)
                navigate_action.setChecked(True)
        return actions

    def _dock_toggle_action(self, text: str, dock: QWidget | None) -> QAction:
        action = self._action(text)
        if dock is None:
            action.setEnabled(False)
            return action

        dock_action = dock.toggleViewAction()  # type: ignore[call-arg]
        dock_action.setText(text)
        return dock_action

    def _toolbar_toggle_action(self, toolbar: QToolBar | None) -> QAction:
        if toolbar is None:
            action = self._action("Unavailable")
            action.setEnabled(False)
            return action
        action = toolbar.toggleViewAction()
        action.setChecked(toolbar.isVisible())
        return action

    def _palette_action(self, text: str, slot: Callable[[], None]) -> QAction:
        action = self._action(text)
        action.triggered.connect(slot)
        action.setEnabled(self.palette_dock is not None)
        return action

    def _action(self, text: str, shortcut: str | None = None) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def _status_bar(self) -> QStatusBar:
        status_bar = self.statusBar()
        assert status_bar is not None
        return status_bar

    def _toggle_flag_action(
        self,
        text: str,
        shortcut: str | None,
        *,
        checked: bool,
        slot: Callable[[bool], None],
    ) -> QAction:
        action = self._action(text, shortcut)
        action.setCheckable(True)
        action.setChecked(checked)
        action.toggled.connect(slot)
        return action

    def _phase1_action(
        self, action_id: str, slot: Callable[..., None] | None = None
    ) -> QAction:
        spec = PHASE1_ACTIONS[action_id]
        action = self._action(spec.text, spec.shortcut)
        if spec.status_tip:
            action.setStatusTip(spec.status_tip)
            action.setToolTip(spec.status_tip)
        if slot is not None:
            action.triggered.connect(slot)
        return action

    def _show_map_properties(self) -> None:
        dialog = MapPropertiesDialog(self)
        dialog.exec()

    def _show_find_item(self) -> None:
        dialog = FindItemDialog(self)
        dialog.exec()

    def _show_goto_position(self) -> None:
        dialog = GotoPositionDialog(self)
        if hasattr(dialog, "position_input") and hasattr(
            dialog.position_input, "set_position"
        ):
            dialog.position_input.set_position(*self._position)
        if dialog.exec():
            self._previous_position = self._position
            self.goto_previous_position_action.setEnabled(True)
            self._set_position(*dialog.get_position(), track_history=True)
            self._status_bar().showMessage(
                "Navigation focus moved to "
                f"{self._position[0]}, {self._position[1]}, {self._position[2]:02d}",
                3000,
            )

    def _goto_previous_position(self) -> None:
        if self._previous_position is None:
            self._status_bar().showMessage("No previous position stored.", 3000)
            return
        current = self._position
        previous = self._previous_position
        self._previous_position = current
        self._set_position(*previous)
        self.goto_previous_position_action.setEnabled(True)
        self._status_bar().showMessage(
            f"Returned to previous position {previous[0]}, {previous[1]}, {previous[2]:02d}",
            3000,
        )

    def _set_position(
        self,
        x: int,
        y: int,
        z: int,
        *,
        track_history: bool = False,
    ) -> None:
        next_position = self._core.set_position(x, y, z)
        if track_history and next_position != self._position:
            self._previous_position = self._position
        self._position = next_position
        self._floor = self._core.floor()
        self._sync_floor_actions(self._floor)
        self._apply_shell_state_to_canvas()
        self._update_status_labels()

    def _floor_up(self) -> None:
        if self._floor <= 0:
            self._status_bar().showMessage("Already at the top-most floor", 2000)
            return
        self._set_floor(self._floor - 1, track_history=True)

    def _floor_down(self) -> None:
        if self._floor >= 15:
            self._status_bar().showMessage("Already at the lowest floor", 2000)
            return
        self._set_floor(self._floor + 1, track_history=True)

    def _set_floor(self, floor: int, *, track_history: bool = False) -> None:
        self._set_position(
            self._position[0],
            self._position[1],
            floor,
            track_history=track_history,
        )

    def _set_zoom(self, percent: int) -> None:
        self._zoom_percent = self._core.set_zoom_percent(percent)
        self._apply_shell_state_to_canvas()
        self._update_status_labels()

    def _toggle_show_grid(self, checked: bool) -> None:
        self._show_grid = self._core.set_show_grid(checked)
        self._sync_checkable_action(self.show_grid_action, self._show_grid)
        self._apply_shell_state_to_canvas()
        self._status_bar().showMessage(
            f"Show Grid {'enabled' if checked else 'disabled'}",
            2000,
        )

    def _toggle_ghost_higher_from_menu(self, checked: bool) -> None:
        self._set_ghost_higher(checked, source="menu")

    def _toggle_ghost_higher_from_toolbar(self, checked: bool) -> None:
        self._set_ghost_higher(checked, source="toolbar")

    def _set_ghost_higher(self, checked: bool, source: str | None = None) -> None:
        self._ghost_higher = self._core.set_ghost_higher(checked)
        if source != "menu":
            self._sync_checkable_action(self.ghost_higher_action, checked)
        if source != "toolbar":
            self._sync_checkable_action(self.ghost_higher_toolbar_action, checked)
        self._apply_shell_state_to_canvas()
        self._status_bar().showMessage(
            f"Ghost Higher Floors {'enabled' if checked else 'disabled'}",
            2000,
        )

    def _set_show_lower(self, checked: bool) -> None:
        self._show_lower = self._core.set_show_lower(checked)
        self._sync_checkable_action(self.show_lower_action, checked)
        self._apply_shell_state_to_canvas()
        self._status_bar().showMessage(
            f"Show Lower Floors {'enabled' if checked else 'disabled'}",
            2000,
        )

    def _set_view_flag(self, name: str, checked: bool) -> None:
        self._view_flags[name] = self._core.set_view_flag(name, checked)
        self._apply_shell_state_to_canvas()
        self._status_bar().showMessage(
            f"{self._view_actions[name].text()} {'ON' if checked else 'OFF'}",
            2000,
        )

    def _set_show_flag(self, name: str, checked: bool) -> None:
        self._show_flags[name] = self._core.set_show_flag(name, checked)
        self._apply_shell_state_to_canvas()
        self._status_bar().showMessage(
            f"{self._show_actions[name].text()} {'ON' if checked else 'OFF'}",
            2000,
        )

    def _apply_shell_state_to_canvas(self) -> None:
        if hasattr(self._canvas, "set_position"):
            self._canvas.set_position(*self._position)
        if hasattr(self._canvas, "set_floor"):
            self._canvas.set_floor(self._floor)
        if hasattr(self._canvas, "set_zoom"):
            self._canvas.set_zoom(self._zoom_percent)
        if hasattr(self._canvas, "set_show_grid"):
            self._canvas.set_show_grid(self._show_grid)
        if hasattr(self._canvas, "set_ghost_higher"):
            self._canvas.set_ghost_higher(self._ghost_higher)
        if hasattr(self._canvas, "set_show_lower"):
            self._canvas.set_show_lower(self._show_lower)
        if hasattr(self._canvas, "set_render_summary"):
            self._canvas.set_render_summary(self._core.render_summary())
        if hasattr(self._canvas, "set_core_mode"):
            self._canvas.set_core_mode(
                "native-rust" if self._shell_core_available else "python-fallback"
            )
        if hasattr(self._canvas, "set_view_flag"):
            for name, enabled in self._view_flags.items():
                self._canvas.set_view_flag(name, enabled)
        if hasattr(self._canvas, "set_show_flag"):
            for name, enabled in self._show_flags.items():
                self._canvas.set_show_flag(name, enabled)

    def _update_status_labels(self) -> None:
        x, y, z = self._position
        self._coord_label.setText(f"Pos: (X: {x}, Y: {y}, Z: {z:02d})")
        self._zoom_label.setText(f"{self._zoom_percent}%")
        if z < 7:
            floor_name = "Above Ground"
        elif z == 7:
            floor_name = "Ground"
        else:
            floor_name = "Below Ground"
        self._floor_label.setText(f"Floor {z} ({floor_name})")

        if self.tool_options_dock is not None:
            self.tool_options_dock.set_shell_state(
                brush_name="Select",
                position=self._position,
                zoom_percent=self._zoom_percent,
            )
        if self.ingame_preview_dock is not None:
            self.ingame_preview_dock.set_preview_state(
                f"In-game preview is not wired in this slice.\n"
                f"Position: {x}, {y}, {z:02d} | Zoom: {self._zoom_percent}%\n"
                f"{self._core.render_summary()}"
            )

    def _sync_floor_actions(self, floor: int) -> None:
        floor = max(0, min(15, floor))
        if 0 <= floor < len(self.floor_actions):
            self._sync_checkable_action(self.floor_actions[floor], True)
        for index, action in enumerate(self.floor_actions):
            if index != floor:
                self._sync_checkable_action(action, False)
        if 0 <= floor < len(self._navigate_floor_actions):
            self._sync_checkable_action(self._navigate_floor_actions[floor], True)
        for index, action in enumerate(self._navigate_floor_actions):
            if index != floor:
                self._sync_checkable_action(action, False)
        if self.floor_up_action is not None:
            self.floor_up_action.setEnabled(floor > 0)
        if self.floor_down_action is not None:
            self.floor_down_action.setEnabled(floor < 15)
        if self.minimap_dock is not None:
            self.minimap_dock.pos_label.setText(f"Z: {floor:02d}")
            self.minimap_dock.z_up_btn.setEnabled(floor > 0)
            self.minimap_dock.z_down_btn.setEnabled(floor < 15)

    def _open_new_view(self) -> None:
        view = MainWindow(
            settings=self._settings,
            canvas_factory=self._canvas_factory,
            enable_docks=self._enable_docks,
        )
        view._core = create_editor_shell_state()
        view._position = view._core.set_position(*self._position)
        view._floor = view._core.floor()
        view._zoom_percent = view._core.set_zoom_percent(self._zoom_percent)
        view._show_grid = view._core.set_show_grid(self._show_grid)
        view._ghost_higher = view._core.set_ghost_higher(self._ghost_higher)
        view._show_lower = view._core.set_show_lower(self._show_lower)
        view._sync_checkable_action(view.show_grid_action, view._show_grid)
        view._set_ghost_higher(view._ghost_higher)
        view._set_show_lower(view._show_lower)
        for name, enabled in self._view_flags.items():
            view._view_flags[name] = view._core.set_view_flag(name, enabled)
            if name in view._view_actions:
                view._sync_checkable_action(view._view_actions[name], enabled)
        for name, enabled in self._show_flags.items():
            view._show_flags[name] = view._core.set_show_flag(name, enabled)
            if name in view._show_actions:
                view._sync_checkable_action(view._show_actions[name], enabled)
        view._apply_shell_state_to_canvas()
        view._update_status_labels()
        view.show()
        self._child_views.append(view)
        self._status_bar().showMessage("Opened a secondary editor view.", 2000)

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self._status_bar().showMessage("Fullscreen disabled.", 2000)
            return

        self.showFullScreen()
        self._status_bar().showMessage("Fullscreen enabled.", 2000)

    def _capture_screenshot(self) -> None:
        widget = self.centralWidget() or self
        self._last_screenshot = widget.grab()
        self._status_bar().showMessage("Captured shell screenshot.", 2000)

    def _new_palette_window(self) -> None:
        if self.palette_dock is None:
            return

        dock = BrushPaletteDock(self)
        dock.setObjectName(f"brush_palette_dock_{len(self._palette_docks) + 1}")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        dock.setFloating(True)
        dock.show()
        self._palette_docks.append(dock)
        self._select_palette_page(self.palette_dock.current_palette())

    def _select_palette_page(self, palette_name: str) -> None:
        if self.palette_dock is None:
            return

        self.palette_dock.select_palette(palette_name)
        for dock in self._palette_docks:
            if dock is not self.palette_dock:
                dock.select_palette(palette_name)

    def _select_palette_terrain(self) -> None:
        self._select_palette_page("Terrain")

    def _select_palette_doodad(self) -> None:
        self._select_palette_page("Doodad")

    def _select_palette_item(self) -> None:
        self._select_palette_page("Item")

    def _select_palette_collection(self) -> None:
        self._select_palette_page("Collection")

    def _select_palette_house(self) -> None:
        self._select_palette_page("House")

    def _select_palette_creature(self) -> None:
        self._select_palette_page("Creature")

    def _select_palette_waypoint(self) -> None:
        self._select_palette_page("Waypoint")

    def _select_palette_raw(self) -> None:
        self._select_palette_page("RAW")

    def _sync_checkable_action(self, action: QAction, checked: bool) -> None:
        was_blocked = action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(was_blocked)

    def _restore_window_state(self) -> None:
        geometry = self._settings.value("main_window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self._settings.value("main_window/state")
        if state is not None:
            self.restoreState(state)

        current_x = self._coerce_int(
            self._settings.value("main_window/current_x", self._position[0]),
            self._position[0],
        )
        current_y = self._coerce_int(
            self._settings.value("main_window/current_y", self._position[1]),
            self._position[1],
        )
        current_z = self._coerce_int(
            self._settings.value("main_window/current_z", self._position[2]),
            self._position[2],
        )
        self._toggle_show_grid(
            self._coerce_bool(self._settings.value("main_window/show_grid", False), False)
        )
        self._set_ghost_higher(
            self._coerce_bool(
                self._settings.value("main_window/ghost_higher", False),
                False,
            )
        )
        self._set_show_lower(
            self._coerce_bool(self._settings.value("main_window/show_lower", True), True)
        )
        for flag_name, default in VIEW_FLAG_DEFAULTS.items():
            restored = self._coerce_bool(
                self._settings.value(f"main_window/view_flags/{flag_name}", default),
                default,
            )
            self._view_flags[flag_name] = self._core.set_view_flag(flag_name, restored)
            if flag_name in self._view_actions:
                self._sync_checkable_action(self._view_actions[flag_name], restored)
        for flag_name, default in SHOW_FLAG_DEFAULTS.items():
            restored = self._coerce_bool(
                self._settings.value(f"main_window/show_flags/{flag_name}", default),
                default,
            )
            self._show_flags[flag_name] = self._core.set_show_flag(flag_name, restored)
            if flag_name in self._show_actions:
                self._sync_checkable_action(self._show_actions[flag_name], restored)
        self._set_position(current_x, current_y, current_z)

    def _coerce_int(self, raw: object, default: int) -> int:
        try:
            return int(str(raw))
        except (TypeError, ValueError):
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
        self._settings.setValue("main_window/current_x", self._position[0])
        self._settings.setValue("main_window/current_y", self._position[1])
        self._settings.setValue("main_window/current_z", self._position[2])
        self._settings.setValue("main_window/show_grid", self._show_grid)
        self._settings.setValue("main_window/ghost_higher", self._ghost_higher)
        self._settings.setValue("main_window/show_lower", self._show_lower)
        for flag_name, enabled in self._view_flags.items():
            self._settings.setValue(f"main_window/view_flags/{flag_name}", enabled)
        for flag_name, enabled in self._show_flags.items():
            self._settings.setValue(f"main_window/show_flags/{flag_name}", enabled)
        self._settings.sync()
        super().closeEvent(event)

    def _stub_replace_items(self) -> None:
        logger.warning("Replace Items: awaiting legacy backend port")
        self._status_bar().showMessage("Replace Items is not available yet.", 3000)

    def _stub_map_statistics(self) -> None:
        logger.warning("Map Statistics: awaiting legacy backend port")
        self._status_bar().showMessage("Map Statistics is not available yet.", 3000)

    def _stub_jump_to_brush(self) -> None:
        logger.warning("Jump To Brush: awaiting legacy backend port")
        self._status_bar().showMessage("Jump to Brush is not available yet.", 3000)

    def _stub_jump_to_item(self) -> None:
        logger.warning("Jump To Item Brush: awaiting legacy backend port")
        self._status_bar().showMessage("Jump to Item is not available yet.", 3000)
