"""Noct Map Editor Main Window - the editor shell."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QDialog,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.editor import MapPosition
from pyrme.rendering import build_diagnostic_tile_primitives, build_render_frame_plan
from pyrme.ui.canvas_host import (
    EditorFramePrimitivesCanvasProtocol,
    EditorFrameSummaryCanvasProtocol,
    EditorToolApplyResult,
    RendererHostCanvasWidget,
    implements_canvas_widget_protocol,
    implements_editor_activation_canvas_protocol,
    implements_editor_frame_primitives_canvas_protocol,
    implements_editor_frame_summary_canvas_protocol,
    implements_editor_show_flag_canvas_protocol,
    implements_editor_tool_callback_canvas_protocol,
    implements_editor_tool_canvas_protocol,
    implements_editor_view_flag_canvas_protocol,
    implements_editor_viewport_canvas_protocol,
)
from pyrme.ui.dialogs import (
    AboutDialog,
    FindItemDialog,
    GotoPositionDialog,
    MapPropertiesDialog,
    PreferencesDialog,
    TownManagerDialog,
)
from pyrme.ui.docks import (
    BrushPaletteDock,
    IngamePreviewDock,
    MinimapDock,
    PropertiesDock,
    ToolOptionsDock,
    WaypointsDock,
)
from pyrme.ui.editor_context import (
    EditorContext,
    EditorViewRecord,
    MinimapViewportState,
    ShellStateSnapshot,
)
from pyrme.ui.legacy_menu_contract import (
    LEGACY_ABOUT_MENU_SEQUENCE,
    LEGACY_EDIT_BORDER_ITEMS,
    LEGACY_EDIT_MENU_SEQUENCE,
    LEGACY_EDIT_OTHER_ITEMS,
    LEGACY_EDIT_STATE_DEFAULTS,
    LEGACY_EXPERIMENTAL_MENU_SEQUENCE,
    LEGACY_FILE_EXPORT_ITEMS,
    LEGACY_FILE_IMPORT_ITEMS,
    LEGACY_FILE_MENU_SEQUENCE,
    LEGACY_FILE_RELOAD_ITEMS,
    LEGACY_MAP_MENU_SEQUENCE,
    LEGACY_NAVIGATE_FLOOR_LABELS,
    LEGACY_SCRIPTS_MENU_SEQUENCE,
    LEGACY_SEARCH_MENU_SEQUENCE,
    LEGACY_SELECTION_FIND_ITEMS,
    LEGACY_SELECTION_MENU_SEQUENCE,
    LEGACY_SELECTION_MODE_DEFAULTS,
    LEGACY_SELECTION_MODE_ITEMS,
    LEGACY_SHOW_FLAG_DEFAULTS,
    LEGACY_SHOW_MENU_SEQUENCE,
    LEGACY_TOP_LEVEL_MENUS,
    LEGACY_VIEW_FLAG_DEFAULTS,
    LEGACY_VIEW_MENU_SEQUENCE,
    LEGACY_WINDOW_PALETTE_ITEMS,
    LEGACY_WINDOW_TOOLBAR_ITEMS,
    PHASE1_ACTIONS,
)
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot

if TYPE_CHECKING:
    from pyrme.ui.canvas_host import (
        CanvasWidgetProtocol,
        EditorActivationCanvasProtocol,
        EditorShowFlagCanvasProtocol,
        EditorToolCallbackCanvasProtocol,
        EditorToolCanvasProtocol,
        EditorViewFlagCanvasProtocol,
        EditorViewportCanvasProtocol,
    )

logger = logging.getLogger(__name__)

CanvasFactory = Callable[[QWidget | None], QWidget]


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
        find_item_dialog_factory=None,
        map_properties_dialog_factory=None,
        canvas_factory: CanvasFactory | None = None,
        enable_docks: bool | None = None,
        editor_context: EditorContext | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings or QSettings("Noct Map Editor", "Noct")
        self._goto_dialog_factory = goto_dialog_factory or GotoPositionDialog
        self._find_item_dialog_factory = find_item_dialog_factory or FindItemDialog
        self._map_properties_dialog_factory = (
            map_properties_dialog_factory or MapPropertiesDialog
        )
        self._canvas_factory = canvas_factory or RendererHostCanvasWidget
        self._enable_docks = True if enable_docks is None else enable_docks
        self._editor_context = editor_context or EditorContext()
        self._views: list[EditorViewRecord] = []
        self._active_view_index = 0
        self.brush_palette_dock: BrushPaletteDock | None = None
        self.tool_options_dock: ToolOptionsDock | None = None
        self.minimap_dock: MinimapDock | None = None
        self.properties_dock: PropertiesDock | None = None
        self.ingame_preview_dock: IngamePreviewDock | None = None
        self.waypoints_dock: WaypointsDock | None = None
        self.toggle_minimap_action: QAction | None = None
        self.toggle_floors_toolbar_action: QAction | None = None
        self.floor_toolbar: QToolBar | None = None
        self.brushes_toolbar: QToolBar | None = None
        self.brush_mode_actions: dict[str, QAction] = {}
        self.position_toolbar: QToolBar | None = None
        self.sizes_toolbar: QToolBar | None = None
        self.standard_toolbar: QToolBar | None = None
        self.window_minimap_action: QAction | None = None
        self.window_tool_options_action: QAction | None = None
        self.window_tile_properties_action: QAction | None = None
        self.window_ingame_preview_action: QAction | None = None
        self.new_palette_action: QAction | None = None
        self.navigate_floor_actions: list[QAction] = []
        self.edit_menu_actions: dict[str, QAction] = {}
        self.file_menu_actions: dict[str, QAction] = {}
        self.selection_menu_actions: dict[str, QAction] = {}
        self.palette_actions: dict[str, QAction] = {}
        self.toolbar_visibility_actions: dict[str, QAction] = {}
        self.edit_undo_action: QAction | None = None
        self.edit_redo_action: QAction | None = None
        self.edit_cut_action: QAction | None = None
        self.edit_copy_action: QAction | None = None
        self.edit_paste_action: QAction | None = None
        self.file_new_action: QAction | None = None
        self.file_open_action: QAction | None = None
        self.file_save_action: QAction | None = None
        self.file_save_as_action: QAction | None = None
        self.file_generate_map_action: QAction | None = None
        self.file_close_action: QAction | None = None
        self.file_import_map_action: QAction | None = None
        self.file_import_monsters_action: QAction | None = None
        self.file_export_minimap_action: QAction | None = None
        self.file_export_tilesets_action: QAction | None = None
        self.file_reload_data_action: QAction | None = None
        self.file_missing_items_report_action: QAction | None = None
        self.file_preferences_action: QAction | None = None
        self.file_exit_action: QAction | None = None
        self.editor_new_view_action: QAction | None = None
        self.editor_fullscreen_action: QAction | None = None
        self.editor_screenshot_action: QAction | None = None
        self.editor_zoom_in_action: QAction | None = None
        self.editor_zoom_out_action: QAction | None = None
        self.editor_zoom_normal_action: QAction | None = None
        self.search_on_map_unique_action: QAction | None = None
        self.search_on_map_action_action: QAction | None = None
        self.search_on_map_container_action: QAction | None = None
        self.search_on_map_writeable_action: QAction | None = None
        self.search_on_map_everything_action: QAction | None = None
        self._edit_flag_state: dict[str, bool] = dict(LEGACY_EDIT_STATE_DEFAULTS)
        self._selection_compensate = LEGACY_SELECTION_MODE_DEFAULTS[
            "select_mode_compensate"
        ]
        self._selection_mode = "current"
        self.show_menu_actions: dict[str, QAction] = {}
        self.view_menu_actions: dict[str, QAction] = {}
        self._show_flag_state: dict[str, bool] = dict(LEGACY_SHOW_FLAG_DEFAULTS)
        self._view_flag_state: dict[str, bool] = dict(LEGACY_VIEW_FLAG_DEFAULTS)
        self._active_brush_name = "Select"
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
        if self._enable_docks:
            self._setup_docks()
        self._setup_window_menu()
        self._setup_status_bar()
        self._restore_window_state()
        self._sync_canvas_shell_state()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle(self._window_title())
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

        self.edit_undo_action = self._action_from_spec(
            "edit_undo", lambda: self._show_edit_backend_gap("Undo")
        )
        self.edit_redo_action = self._action_from_spec(
            "edit_redo", lambda: self._show_edit_backend_gap("Redo")
        )
        self.find_item_action = self._action_from_spec("find_item", self._show_find_item)
        self.replace_items_action = self._action_from_spec(
            "replace_items", self._show_replace_items
        )
        self.edit_cut_action = self._action_from_spec(
            "edit_cut", lambda: self._show_edit_backend_gap("Cut")
        )
        self.edit_copy_action = self._action_from_spec(
            "edit_copy", lambda: self._show_edit_backend_gap("Copy")
        )
        self.edit_paste_action = self._action_from_spec(
            "edit_paste", lambda: self._show_edit_backend_gap("Paste")
        )
        self.map_edit_towns_action = self._action_from_spec(
            "map_edit_towns",
            self._show_town_manager_dialog,
        )
        self.map_cleanup_invalid_tiles_action = self._action_from_spec(
            "map_cleanup_invalid_tiles",
            lambda: self._show_map_backend_gap("Cleanup invalid tiles"),
        )
        self.map_cleanup_invalid_zones_action = self._action_from_spec(
            "map_cleanup_invalid_zones",
            lambda: self._show_map_backend_gap("Cleanup invalid zones"),
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
        self.jump_to_item_action = self._action_from_spec(
            "jump_to_item", self._show_jump_to_item
        )
        self.show_grid_action = self._action_from_spec("show_grid")
        self.show_grid_action.setCheckable(True)
        self.show_grid_action.toggled.connect(self._toggle_show_grid)
        self.ghost_higher_action = self._action_from_spec("ghost_higher_floors")
        self.ghost_higher_action.setCheckable(True)
        self.ghost_higher_action.toggled.connect(self._stub_ghost_higher)

        phase1_action_attrs: dict[str, QAction] = {}
        for spec_key, spec in PHASE1_ACTIONS.items():
            if spec_key not in phase1_action_attrs:
                continue
            menu = self._menus[spec.menu_path[0]]
            action = phase1_action_attrs[spec_key]
            menu.addAction(action)

        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_editor_menu()
        self._setup_search_menu()
        self._setup_map_menu()
        self._setup_selection_menu()
        self._setup_view_menu()
        self._setup_show_menu()
        self._setup_navigate_menu()
        self._setup_experimental_menu()
        self._setup_scripts_menu()
        self._setup_about_menu()
        self._refresh_selection_action_state()

    def _setup_edit_menu(self) -> None:
        edit_menu = self._menus["Edit"]

        self.edit_menu_actions = {
            "border_automagic": self._edit_flag_action("border_automagic"),
            "borderize_selection": self._action_from_spec(
                "borderize_selection",
                lambda: self._show_edit_backend_gap("Borderize Selection"),
            ),
            "borderize_map": self._action_from_spec(
                "borderize_map",
                lambda: self._show_edit_backend_gap("Borderize Map"),
            ),
            "randomize_selection": self._action_from_spec(
                "randomize_selection",
                lambda: self._show_edit_backend_gap("Randomize Selection"),
            ),
            "randomize_map": self._action_from_spec(
                "randomize_map",
                lambda: self._show_edit_backend_gap("Randomize Map"),
            ),
            "remove_items_by_id": self._action_from_spec(
                "remove_items_by_id",
                lambda: self._show_edit_backend_gap("Remove Items by ID"),
            ),
            "remove_all_corpses": self._action_from_spec(
                "remove_all_corpses",
                lambda: self._show_edit_backend_gap("Remove all Corpses"),
            ),
            "remove_all_unreachable_tiles": self._action_from_spec(
                "remove_all_unreachable_tiles",
                lambda: self._show_edit_backend_gap("Remove all Unreachable Tiles"),
            ),
            "clear_invalid_houses": self._action_from_spec(
                "clear_invalid_houses",
                lambda: self._show_edit_backend_gap("Clear Invalid Houses"),
            ),
            "clear_modified_state": self._action_from_spec(
                "clear_modified_state",
                lambda: self._show_edit_backend_gap("Clear Modified State"),
            ),
        }

        border_menu = edit_menu.addMenu("Border Options")
        assert border_menu is not None
        border_action_by_text = {
            "Border Automagic": self.edit_menu_actions["border_automagic"],
            "Borderize Selection": self.edit_menu_actions["borderize_selection"],
            "Borderize Map": self.edit_menu_actions["borderize_map"],
            "Randomize Selection": self.edit_menu_actions["randomize_selection"],
            "Randomize Map": self.edit_menu_actions["randomize_map"],
        }
        for item in LEGACY_EDIT_BORDER_ITEMS:
            if item is None:
                border_menu.addSeparator()
                continue
            border_menu.addAction(border_action_by_text[item])

        other_menu = edit_menu.addMenu("Other Options")
        assert other_menu is not None
        other_action_by_text = {
            "Remove Items by ID...": self.edit_menu_actions["remove_items_by_id"],
            "Remove all Corpses...": self.edit_menu_actions["remove_all_corpses"],
            "Remove all Unreachable Tiles...": self.edit_menu_actions[
                "remove_all_unreachable_tiles"
            ],
            "Clear Invalid Houses": self.edit_menu_actions["clear_invalid_houses"],
            "Clear Modified State": self.edit_menu_actions["clear_modified_state"],
        }
        for item in LEGACY_EDIT_OTHER_ITEMS:
            other_menu.addAction(other_action_by_text[item])

        action_by_text = {
            "Undo": self.edit_undo_action,
            "Redo": self.edit_redo_action,
            "Replace Items...": self.replace_items_action,
            "Border Options": border_menu.menuAction(),
            "Other Options": other_menu.menuAction(),
            "Cut": self.edit_cut_action,
            "Copy": self.edit_copy_action,
            "Paste": self.edit_paste_action,
        }
        for item in LEGACY_EDIT_MENU_SEQUENCE:
            if item is None:
                edit_menu.addSeparator()
                continue
            edit_menu.addAction(action_by_text[item])

    def _setup_file_menu(self) -> None:
        file_menu = self._menus["File"]
        import_menu = file_menu.addMenu("Import")
        assert import_menu is not None
        export_menu = file_menu.addMenu("Export")
        assert export_menu is not None
        reload_menu = file_menu.addMenu("Reload")
        assert reload_menu is not None
        recent_files_menu = file_menu.addMenu("Recent Files")
        assert recent_files_menu is not None

        self.file_new_action = self._action_from_spec(
            "file_new", lambda: self._show_file_backend_gap("New")
        )
        self.file_open_action = self._action_from_spec(
            "file_open", lambda: self._show_file_backend_gap("Open")
        )
        self.file_save_action = self._action_from_spec(
            "file_save", lambda: self._show_file_backend_gap("Save")
        )
        self.file_save_as_action = self._action_from_spec(
            "file_save_as", lambda: self._show_file_backend_gap("Save As")
        )
        self.file_generate_map_action = self._action_from_spec(
            "file_generate_map",
            lambda: self._show_file_backend_gap("Generate Map"),
        )
        self.file_close_action = self._action_from_spec(
            "file_close", lambda: self._show_file_backend_gap("Close")
        )
        self.file_import_map_action = self._action_from_spec(
            "file_import_map", lambda: self._show_file_backend_gap("Import Map")
        )
        self.file_import_monsters_action = self._action_from_spec(
            "file_import_monsters",
            lambda: self._show_file_backend_gap("Import Monsters/NPC"),
        )
        self.file_export_minimap_action = self._action_from_spec(
            "file_export_minimap",
            lambda: self._show_file_backend_gap("Export Minimap"),
        )
        self.file_export_tilesets_action = self._action_from_spec(
            "file_export_tilesets",
            lambda: self._show_file_backend_gap("Export Tilesets"),
        )
        self.file_reload_data_action = self._action_from_spec(
            "file_reload_data",
            lambda: self._show_file_backend_gap("Reload Data Files"),
        )
        self.file_missing_items_report_action = self._action_from_spec(
            "file_missing_items_report",
            lambda: self._show_file_backend_gap("Missing Items Report"),
        )
        self.file_preferences_action = self._action_from_spec(
            "file_preferences",
            self._show_preferences_dialog,
        )
        self.file_exit_action = self._action_from_spec(
            "file_exit", lambda: self._show_file_backend_gap("Exit")
        )

        self.file_menu_actions = {
            "file_new": self.file_new_action,
            "file_open": self.file_open_action,
            "file_save": self.file_save_action,
            "file_save_as": self.file_save_as_action,
            "file_generate_map": self.file_generate_map_action,
            "file_close": self.file_close_action,
            "file_import_map": self.file_import_map_action,
            "file_import_monsters": self.file_import_monsters_action,
            "file_export_minimap": self.file_export_minimap_action,
            "file_export_tilesets": self.file_export_tilesets_action,
            "file_reload_data": self.file_reload_data_action,
            "file_missing_items_report": self.file_missing_items_report_action,
            "file_preferences": self.file_preferences_action,
            "file_exit": self.file_exit_action,
        }

        import_action_by_text = {
            "Import Map...": self.file_import_map_action,
            "Import Monsters/NPC...": self.file_import_monsters_action,
        }
        for item in LEGACY_FILE_IMPORT_ITEMS:
            import_menu.addAction(import_action_by_text[item])

        export_action_by_text = {
            "Export Minimap...": self.file_export_minimap_action,
            "Export Tilesets...": self.file_export_tilesets_action,
        }
        for item in LEGACY_FILE_EXPORT_ITEMS:
            export_menu.addAction(export_action_by_text[item])

        reload_action_by_text = {
            "Reload Data Files": self.file_reload_data_action,
        }
        for item in LEGACY_FILE_RELOAD_ITEMS:
            reload_menu.addAction(reload_action_by_text[item])

        action_by_text = {
            "New...": self.file_new_action,
            "Open...": self.file_open_action,
            "Save": self.file_save_action,
            "Save As...": self.file_save_as_action,
            "Generate Map": self.file_generate_map_action,
            "Close": self.file_close_action,
            "Import": import_menu.menuAction(),
            "Export": export_menu.menuAction(),
            "Reload": reload_menu.menuAction(),
            "Missing Items Report...": self.file_missing_items_report_action,
            "Recent Files": recent_files_menu.menuAction(),
            "Preferences": self.file_preferences_action,
            "Exit": self.file_exit_action,
        }
        for raw_item in LEGACY_FILE_MENU_SEQUENCE:
            if raw_item is None:
                file_menu.addSeparator()
                continue
            label: str = raw_item
            file_menu.addAction(action_by_text[label])

    def _edit_flag_action(self, spec_key: str) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        action.toggled.connect(
            lambda checked, key=spec_key: self._set_edit_flag(key, checked)
        )
        self._sync_checkable_action(action, LEGACY_EDIT_STATE_DEFAULTS[spec_key])
        return action

    def _setup_editor_menu(self) -> None:
        """Wire the Editor menu to shell seams.

        Structure from menubar.xml:
          New View | Enter Fullscreen | Take Screenshot | ---
          Zoom >
            Zoom In | Zoom Out | Zoom Normal
        """
        editor_menu = self._menus["Editor"]

        self.editor_new_view_action = self._action_from_spec(
            "editor_new_view", self._editor_new_view,
        )
        self.editor_fullscreen_action = self._action_from_spec(
            "editor_fullscreen", self._editor_toggle_fullscreen,
        )
        self.editor_screenshot_action = self._action_from_spec(
            "editor_screenshot", self._editor_take_screenshot,
        )

        editor_menu.addAction(self.editor_new_view_action)
        editor_menu.addAction(self.editor_fullscreen_action)
        editor_menu.addAction(self.editor_screenshot_action)
        editor_menu.addSeparator()

        zoom_menu = editor_menu.addMenu("Zoom")
        assert zoom_menu is not None

        self.editor_zoom_in_action = self._action_from_spec(
            "editor_zoom_in", self._editor_zoom_in,
        )
        self.editor_zoom_out_action = self._action_from_spec(
            "editor_zoom_out", self._editor_zoom_out,
        )
        self.editor_zoom_normal_action = self._action_from_spec(
            "editor_zoom_normal", self._editor_zoom_normal,
        )

        zoom_menu.addAction(self.editor_zoom_in_action)
        zoom_menu.addAction(self.editor_zoom_out_action)
        zoom_menu.addAction(self.editor_zoom_normal_action)

    def _setup_search_menu(self) -> None:
        """Wire the Search menu to the legacy map-search surface.

        SearchResultWindow and MapSearcher are backend work. Until they land,
        non-dialog map searches stay explicit, visible, and safe no-ops.
        """
        search_menu = self._menus["Search"]

        self.search_on_map_unique_action = self._action_from_spec(
            "search_on_map_unique",
            lambda: self._show_search_map_gap("unique"),
        )
        self.search_on_map_action_action = self._action_from_spec(
            "search_on_map_action",
            lambda: self._show_search_map_gap("action"),
        )
        self.search_on_map_container_action = self._action_from_spec(
            "search_on_map_container",
            lambda: self._show_search_map_gap("container"),
        )
        self.search_on_map_writeable_action = self._action_from_spec(
            "search_on_map_writeable",
            lambda: self._show_search_map_gap("writeable"),
        )
        self.search_on_map_everything_action = self._action_from_spec(
            "search_on_map_everything",
            lambda: self._show_search_map_gap("everything"),
        )

        action_by_text = {
            "Find Item...": self.find_item_action,
            "Find Unique": self.search_on_map_unique_action,
            "Find Action": self.search_on_map_action_action,
            "Find Container": self.search_on_map_container_action,
            "Find Writeable": self.search_on_map_writeable_action,
            "Find Everything": self.search_on_map_everything_action,
        }
        for item in LEGACY_SEARCH_MENU_SEQUENCE:
            if item is None:
                search_menu.addSeparator()
                continue
            search_menu.addAction(action_by_text[item])

    def _setup_map_menu(self) -> None:
        """Wire the Map menu to the legacy surface.

        Town editing, cleanup handlers, and statistics depend on editor/map
        backend work. Keep the actions visible but explicit about the gap.
        """
        map_menu = self._menus["Map"]

        action_by_text = {
            "Edit Towns": self.map_edit_towns_action,
            "Cleanup invalid tiles...": self.map_cleanup_invalid_tiles_action,
            "Cleanup invalid zones...": self.map_cleanup_invalid_zones_action,
            "Properties...": self.map_properties_action,
            "Statistics": self.map_statistics_action,
        }
        for item in LEGACY_MAP_MENU_SEQUENCE:
            if item is None:
                map_menu.addSeparator()
                continue
            map_menu.addAction(action_by_text[item])

    def _setup_view_menu(self) -> None:
        """Wire the View menu to legacy checkable view flags.

        Only grid and higher-floor ghosting have direct canvas behavior today.
        Other flags are preserved as local state and sent to the canvas view-flag
        seam when available, without claiming renderer parity.
        """
        view_menu = self._menus["View"]

        self.view_menu_actions = {
            "view_show_all_floors": self._view_flag_action(
                "view_show_all_floors", "show_all_floors"
            ),
            "view_show_as_minimap": self._view_flag_action(
                "view_show_as_minimap", "show_as_minimap"
            ),
            "view_only_show_colors": self._view_flag_action(
                "view_only_show_colors", "only_show_colors"
            ),
            "view_only_show_modified": self._view_flag_action(
                "view_only_show_modified", "only_show_modified"
            ),
            "view_always_show_zones": self._view_flag_action(
                "view_always_show_zones", "always_show_zones"
            ),
            "view_extended_house_shader": self._view_flag_action(
                "view_extended_house_shader", "extended_house_shader"
            ),
            "view_show_tooltips": self._view_flag_action(
                "view_show_tooltips", "show_tooltips"
            ),
            "show_grid": self.show_grid_action,
            "view_show_client_box": self._view_flag_action(
                "view_show_client_box", "show_client_box"
            ),
            "view_ghost_loose_items": self._view_flag_action(
                "view_ghost_loose_items", "ghost_loose_items"
            ),
            "ghost_higher_floors": self.ghost_higher_action,
            "view_show_shade": self._view_flag_action("view_show_shade", "show_shade"),
        }
        self._sync_checkable_action(
            self.show_grid_action,
            LEGACY_VIEW_FLAG_DEFAULTS["show_grid"],
        )
        self._sync_checkable_action(
            self.ghost_higher_action,
            LEGACY_VIEW_FLAG_DEFAULTS["ghost_higher_floors"],
        )

        action_by_text = {
            "Show all Floors": self.view_menu_actions["view_show_all_floors"],
            "Show as Minimap": self.view_menu_actions["view_show_as_minimap"],
            "Only show Colors": self.view_menu_actions["view_only_show_colors"],
            "Only show Modified": self.view_menu_actions["view_only_show_modified"],
            "Always show zones": self.view_menu_actions["view_always_show_zones"],
            "Extended house shader": self.view_menu_actions[
                "view_extended_house_shader"
            ],
            "Show tooltips": self.view_menu_actions["view_show_tooltips"],
            "Show grid": self.show_grid_action,
            "Show client box": self.view_menu_actions["view_show_client_box"],
            "Ghost loose items": self.view_menu_actions["view_ghost_loose_items"],
            "Ghost higher floors": self.ghost_higher_action,
            "Show shade": self.view_menu_actions["view_show_shade"],
        }
        for item in LEGACY_VIEW_MENU_SEQUENCE:
            if item is None:
                view_menu.addSeparator()
                continue
            view_menu.addAction(action_by_text[item])

    def _setup_show_menu(self) -> None:
        """Wire the Show menu to legacy renderer/display flags.

        These toggles stay honest: local shell state plus optional canvas seam.
        Renderer semantics remain backend work.
        """
        show_menu = self._menus["Show"]

        self.show_menu_actions = {
            "show_animation": self._show_flag_action("show_animation", "show_preview"),
            "show_light": self._show_flag_action("show_light", "show_lights"),
            "show_light_strength": self._show_flag_action(
                "show_light_strength", "show_light_strength"
            ),
            "show_technical_items": self._show_flag_action(
                "show_technical_items", "show_technical_items"
            ),
            "show_invalid_tiles": self._show_flag_action(
                "show_invalid_tiles", "show_invalid_tiles"
            ),
            "show_invalid_zones": self._show_flag_action(
                "show_invalid_zones", "show_invalid_zones"
            ),
            "show_creatures": self._show_flag_action("show_creatures", "show_creatures"),
            "show_spawns": self._show_flag_action("show_spawns", "show_spawns"),
            "show_special": self._show_flag_action("show_special", "show_special"),
            "show_houses": self._show_flag_action("show_houses", "show_houses"),
            "show_pathing": self._show_flag_action("show_pathing", "show_pathing"),
            "show_towns": self._show_flag_action("show_towns", "show_towns"),
            "show_waypoints": self._show_flag_action("show_waypoints", "show_waypoints"),
            "highlight_items": self._show_flag_action("highlight_items", "highlight_items"),
            "highlight_locked_doors": self._show_flag_action(
                "highlight_locked_doors", "highlight_locked_doors"
            ),
            "show_wall_hooks": self._show_flag_action(
                "show_wall_hooks", "show_wall_hooks"
            ),
        }

        action_by_text = {
            "Show Animation": self.show_menu_actions["show_animation"],
            "Show Light": self.show_menu_actions["show_light"],
            "Show Light Strength": self.show_menu_actions["show_light_strength"],
            "Show Technical Items": self.show_menu_actions["show_technical_items"],
            "Show Invalid Tiles": self.show_menu_actions["show_invalid_tiles"],
            "Show Invalid Zones": self.show_menu_actions["show_invalid_zones"],
            "Show creatures": self.show_menu_actions["show_creatures"],
            "Show spawns": self.show_menu_actions["show_spawns"],
            "Show special": self.show_menu_actions["show_special"],
            "Show houses": self.show_menu_actions["show_houses"],
            "Show pathing": self.show_menu_actions["show_pathing"],
            "Show towns": self.show_menu_actions["show_towns"],
            "Show waypoints": self.show_menu_actions["show_waypoints"],
            "Highlight Items": self.show_menu_actions["highlight_items"],
            "Highlight Locked Doors": self.show_menu_actions["highlight_locked_doors"],
            "Show Wall Hooks": self.show_menu_actions["show_wall_hooks"],
        }
        for item in LEGACY_SHOW_MENU_SEQUENCE:
            if item is None:
                show_menu.addSeparator()
                continue
            show_menu.addAction(action_by_text[item])

    def _setup_selection_menu(self) -> None:
        selection_menu = self._menus["Selection"]
        find_menu = selection_menu.addMenu("Find on Selection")
        assert find_menu is not None
        mode_menu = selection_menu.addMenu("Selection Mode")
        assert mode_menu is not None

        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)

        self.selection_menu_actions = {
            "replace_on_selection_items": self._action_from_spec(
                "replace_on_selection_items",
                lambda: self._show_selection_backend_gap("Replace Items on Selection"),
            ),
            "search_on_selection_item": self._action_from_spec(
                "search_on_selection_item",
                lambda: self._show_selection_backend_gap("Find Item on Selection"),
            ),
            "remove_on_selection_item": self._action_from_spec(
                "remove_on_selection_item",
                lambda: self._show_selection_backend_gap("Remove Item on Selection"),
            ),
            "search_on_selection_everything": self._action_from_spec(
                "search_on_selection_everything",
                lambda: self._show_selection_backend_gap("Find Everything"),
            ),
            "search_on_selection_unique": self._action_from_spec(
                "search_on_selection_unique",
                lambda: self._show_selection_backend_gap("Find Unique"),
            ),
            "search_on_selection_action": self._action_from_spec(
                "search_on_selection_action",
                lambda: self._show_selection_backend_gap("Find Action"),
            ),
            "search_on_selection_container": self._action_from_spec(
                "search_on_selection_container",
                lambda: self._show_selection_backend_gap("Find Container"),
            ),
            "search_on_selection_writeable": self._action_from_spec(
                "search_on_selection_writeable",
                lambda: self._show_selection_backend_gap("Find Writeable"),
            ),
            "select_mode_compensate": self._selection_compensate_action(),
            "select_mode_current": self._selection_mode_action(
                "select_mode_current", "current", mode_group
            ),
            "select_mode_lower": self._selection_mode_action(
                "select_mode_lower", "lower", mode_group
            ),
            "select_mode_visible": self._selection_mode_action(
                "select_mode_visible", "visible", mode_group
            ),
        }

        action_by_text = {
            "Replace Items on Selection": self.selection_menu_actions[
                "replace_on_selection_items"
            ],
            "Find Item on Selection": self.selection_menu_actions[
                "search_on_selection_item"
            ],
            "Remove Item on Selection": self.selection_menu_actions[
                "remove_on_selection_item"
            ],
            "Find on Selection": find_menu.menuAction(),
            "Selection Mode": mode_menu.menuAction(),
            "Borderize Selection": self.edit_menu_actions["borderize_selection"],
            "Randomize Selection": self.edit_menu_actions["randomize_selection"],
        }
        for item in LEGACY_SELECTION_MENU_SEQUENCE:
            if item is None:
                selection_menu.addSeparator()
                continue
            selection_menu.addAction(action_by_text[item])

        find_action_by_text = {
            "Find Everything": self.selection_menu_actions["search_on_selection_everything"],
            "Find Unique": self.selection_menu_actions["search_on_selection_unique"],
            "Find Action": self.selection_menu_actions["search_on_selection_action"],
            "Find Container": self.selection_menu_actions["search_on_selection_container"],
            "Find Writeable": self.selection_menu_actions["search_on_selection_writeable"],
        }
        for item in LEGACY_SELECTION_FIND_ITEMS:
            if item is None:
                find_menu.addSeparator()
                continue
            find_menu.addAction(find_action_by_text[item])

        mode_action_by_text = {
            "Compensate Selection": self.selection_menu_actions["select_mode_compensate"],
            "Current Floor": self.selection_menu_actions["select_mode_current"],
            "Lower Floors": self.selection_menu_actions["select_mode_lower"],
            "Visible Floors": self.selection_menu_actions["select_mode_visible"],
        }
        for item in LEGACY_SELECTION_MODE_ITEMS:
            if item is None:
                mode_menu.addSeparator()
                continue
            mode_menu.addAction(mode_action_by_text[item])

    def _view_flag_action(self, spec_key: str, view_flag: str) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        action.toggled.connect(
            lambda checked, key=spec_key, flag=view_flag: self._set_view_flag(
                key, flag, checked
            )
        )
        self._sync_checkable_action(action, LEGACY_VIEW_FLAG_DEFAULTS[spec_key])
        return action

    def _show_flag_action(self, spec_key: str, show_flag: str) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        action.toggled.connect(
            lambda checked, key=spec_key, flag=show_flag: self._set_show_flag(
                key, flag, checked
            )
        )
        self._sync_checkable_action(action, LEGACY_SHOW_FLAG_DEFAULTS[spec_key])
        return action

    def _selection_compensate_action(self) -> QAction:
        action = self._action_from_spec("select_mode_compensate")
        action.setCheckable(True)
        action.toggled.connect(self._set_selection_compensate)
        self._sync_checkable_action(
            action,
            LEGACY_SELECTION_MODE_DEFAULTS["select_mode_compensate"],
        )
        return action

    def _selection_mode_action(
        self,
        spec_key: str,
        mode: str,
        group: QActionGroup,
    ) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        group.addAction(action)
        action.toggled.connect(
            lambda checked, value=mode: self._set_selection_mode(value, checked)
        )
        self._sync_checkable_action(action, LEGACY_SELECTION_MODE_DEFAULTS[spec_key])
        return action

    def _brush_mode_action(
        self,
        text: str,
        mode: str,
        group: QActionGroup,
    ) -> QAction:
        action = self._action(text)
        action.setObjectName(f"brush_mode_{mode}_action")
        action.setCheckable(True)
        group.addAction(action)
        action.toggled.connect(
            lambda checked, value=mode: self._set_editor_mode(value, checked)
        )
        return action

    def _setup_toolbars(self) -> None:
        """Create the main toolbars."""
        self.brushes_toolbar = QToolBar("Brushes")
        self.brushes_toolbar.setObjectName("brushes_toolbar")
        self.brushes_toolbar.setMovable(True)
        brush_mode_group = QActionGroup(self)
        brush_mode_group.setExclusive(True)
        self.brush_mode_actions = {
            "selection": self._brush_mode_action("Select", "selection", brush_mode_group),
            "drawing": self._brush_mode_action("Draw", "drawing", brush_mode_group),
            "erasing": self._brush_mode_action("Erase", "erasing", brush_mode_group),
            "fill": self._brush_mode_action("Fill", "fill", brush_mode_group),
            "move": self._brush_mode_action("Move", "move", brush_mode_group),
        }
        self.brushes_toolbar.addAction(self.brush_mode_actions["selection"])
        self.brushes_toolbar.addAction(self.brush_mode_actions["drawing"])
        self.brushes_toolbar.addAction(self.brush_mode_actions["erasing"])
        self.brushes_toolbar.addAction(self.brush_mode_actions["fill"])
        self.brushes_toolbar.addSeparator()
        self.brushes_toolbar.addAction(self.brush_mode_actions["move"])
        self._sync_brush_mode_actions()
        self.addToolBar(self.brushes_toolbar)

        self.position_toolbar = QToolBar("Position")
        self.position_toolbar.setObjectName("position_toolbar")
        self.position_toolbar.setMovable(True)
        self.position_toolbar.addAction(self._action("Center"))
        self.position_toolbar.addAction(self._action("Cursor"))
        self.addToolBar(self.position_toolbar)

        self.sizes_toolbar = QToolBar("Sizes")
        self.sizes_toolbar.setObjectName("sizes_toolbar")
        self.sizes_toolbar.setMovable(True)
        self.sizes_toolbar.addAction(self._action("1x1"))
        self.sizes_toolbar.addAction(self._action("3x3"))
        self.sizes_toolbar.addAction(self._action("5x5"))
        self.addToolBar(self.sizes_toolbar)

        self.standard_toolbar = QToolBar("Standard")
        self.standard_toolbar.setObjectName("standard_toolbar")
        self.standard_toolbar.setMovable(True)
        self.standard_toolbar.addAction(self._action("Open"))
        self.standard_toolbar.addAction(self._action("Save"))
        self.addToolBar(self.standard_toolbar)

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
                lambda checked, value=i: self._select_floor(value) if checked else None
            )
            floor_group.addAction(action)
            self.floor_toolbar.addAction(action)
            self.floor_actions.append(action)
            if i == 7:
                action.setChecked(True)

        self.floor_toolbar.addSeparator()

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
        self._view_tabs = QTabWidget(self)
        self._view_tabs.setObjectName("editor_view_tabs")
        self.setCentralWidget(self._view_tabs)
        self._add_view_tab(self._view_title(), self._default_shell_state())
        self._view_tabs.currentChanged.connect(self._on_view_changed)
        self._canvas = self._active_view().canvas

    def _setup_docks(self) -> None:
        """Create dock widgets for palettes and tools."""
        self.brush_palette_dock = BrushPaletteDock(self)
        self.brush_palette_dock.item_selected.connect(self._select_item_brush)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.brush_palette_dock,
        )

        self.tool_options_dock = ToolOptionsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tool_options_dock)

        self.minimap_dock = MinimapDock(self)
        self.minimap_dock.z_up_btn.clicked.connect(self._floor_up)
        self.minimap_dock.z_down_btn.clicked.connect(self._floor_down)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.minimap_dock)
        self.toggle_minimap_action = self.minimap_dock.toggleViewAction()

        self.properties_dock = PropertiesDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        self.ingame_preview_dock = IngamePreviewDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ingame_preview_dock)

        self.waypoints_dock = WaypointsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.waypoints_dock)

    def _setup_navigate_menu(self) -> None:
        navigate_menu = self._menus["Navigate"]
        navigate_menu.addAction(self.goto_previous_position_action)
        navigate_menu.addAction(self.goto_position_action)
        navigate_menu.addAction(self.jump_to_brush_action)
        navigate_menu.addAction(self.jump_to_item_action)
        navigate_menu.addSeparator()

        floor_menu = navigate_menu.addMenu("Floor")
        assert floor_menu is not None
        self.navigate_floor_actions = []
        for floor, label in enumerate(LEGACY_NAVIGATE_FLOOR_LABELS):
            action = self._action(label)
            action.setObjectName(f"action_navigate_floor_{floor}")
            action.setStatusTip(f"Switch to floor {floor}.")
            action.triggered.connect(
                lambda _checked=False, value=floor: self._select_floor(value)
            )
            floor_menu.addAction(action)
            self.navigate_floor_actions.append(action)

    def _setup_window_menu(self) -> None:
        window_menu = self._menus["Window"]
        self.window_minimap_action = self._create_dock_toggle_action(
            "window_minimap",
            self.minimap_dock,
        )
        self.window_tool_options_action = self._create_dock_toggle_action(
            "window_tool_options",
            self.tool_options_dock,
        )
        self.window_tile_properties_action = self._create_dock_toggle_action(
            "window_tile_properties",
            self.properties_dock,
        )
        self.window_ingame_preview_action = self._create_dock_toggle_action(
            "window_ingame_preview",
            self.ingame_preview_dock,
        )
        self.new_palette_action = self._action_from_spec("new_palette", self._show_new_palette)

        window_menu.addAction(self.window_minimap_action)
        window_menu.addAction(self.window_tool_options_action)
        window_menu.addAction(self.window_tile_properties_action)
        window_menu.addAction(self.window_ingame_preview_action)
        window_menu.addAction(self.new_palette_action)

        palette_menu = window_menu.addMenu("Palette")
        assert palette_menu is not None
        self.palette_actions = {}
        for palette_name in LEGACY_WINDOW_PALETTE_ITEMS:
            spec_key = f"select_palette_{palette_name.lower()}"
            action = self._action_from_spec(
                spec_key,
                lambda _checked=False, value=palette_name: self._show_palette(value),
            )
            palette_menu.addAction(action)
            self.palette_actions[palette_name] = action

        toolbars_menu = window_menu.addMenu("Toolbars")
        assert toolbars_menu is not None
        self.toolbar_visibility_actions = {}
        toolbar_map = {
            "Brushes": self.brushes_toolbar,
            "Position": self.position_toolbar,
            "Sizes": self.sizes_toolbar,
            "Standard": self.standard_toolbar,
        }
        for toolbar_name in LEGACY_WINDOW_TOOLBAR_ITEMS:
            spec_key = f"view_toolbars_{toolbar_name.lower()}"
            action = self._create_toolbar_toggle_action(
                spec_key,
                toolbar_map[toolbar_name],
            )
            toolbars_menu.addAction(action)
            self.toolbar_visibility_actions[toolbar_name] = action

    def _setup_experimental_menu(self) -> None:
        experimental_menu = self._menus["Experimental"]
        self.experimental_fog_action = self._action_from_spec(
            "experimental_fog",
            lambda: self._show_experimental_backend_gap("Fog in light view"),
        )
        for item in LEGACY_EXPERIMENTAL_MENU_SEQUENCE:
            if item == "Fog in light view":
                experimental_menu.addAction(self.experimental_fog_action)
            elif item is None:
                experimental_menu.addSeparator()

    def _setup_scripts_menu(self) -> None:
        scripts_menu = self._menus["Scripts"]
        self.scripts_manager_action = self._action_from_spec(
            "scripts_manager",
            lambda: self._show_scripts_backend_gap("Script Manager"),
        )
        self.scripts_open_folder_action = self._action_from_spec(
            "scripts_open_folder",
            lambda: self._show_scripts_backend_gap("Open Scripts Folder"),
        )
        self.scripts_reload_action = self._action_from_spec(
            "scripts_reload",
            lambda: self._show_scripts_backend_gap("Reload Scripts"),
        )

        action_by_text = {
            "Script Manager...": self.scripts_manager_action,
            "Open Scripts Folder": self.scripts_open_folder_action,
            "Reload Scripts": self.scripts_reload_action,
        }
        for item in LEGACY_SCRIPTS_MENU_SEQUENCE:
            if item is None:
                scripts_menu.addSeparator()
                continue
            scripts_menu.addAction(action_by_text[item])

    def _setup_about_menu(self) -> None:
        about_menu = self._menus["About"]
        self.extensions_action = self._action_from_spec(
            "extensions",
            lambda: self._show_about_backend_gap("Extensions"),
        )
        self.goto_website_action = self._action_from_spec(
            "goto_website",
            lambda: self._show_about_backend_gap("Goto Website"),
        )
        self.about_action = self._action_from_spec(
            "about",
            self._show_about_dialog,
        )

        action_by_text = {
            "Extensions...": self.extensions_action,
            "Goto Website": self.goto_website_action,
            "About...": self.about_action,
        }
        for item in LEGACY_ABOUT_MENU_SEQUENCE:
            if item is None:
                about_menu.addSeparator()
                continue
            about_menu.addAction(action_by_text[item])

    def _setup_status_bar(self) -> None:
        """Create the status bar with coordinate and zoom info."""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self._coord_label = QLabel("Pos: (X: 32000, Y: 32000, Z: 07)")
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
        return title

    def _create_dock_toggle_action(
        self,
        spec_key: str,
        dock: QDockWidget | None,
    ) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        if dock is None:
            action.setEnabled(False)
            return action

        self._sync_checkable_action(action, not dock.isHidden())
        action.toggled.connect(dock.setVisible)
        dock.visibilityChanged.connect(
            lambda visible, target=action: self._sync_checkable_action(target, visible)
        )
        return action

    def _create_toolbar_toggle_action(
        self,
        spec_key: str,
        toolbar: QToolBar | None,
    ) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        if toolbar is None:
            action.setEnabled(False)
            return action

        self._sync_checkable_action(action, not toolbar.isHidden())
        action.toggled.connect(toolbar.setVisible)
        toolbar.visibilityChanged.connect(
            lambda visible, target=action: self._sync_checkable_action(target, visible)
        )
        return action

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

    def _sync_checkable_action(self, action: QAction, checked: bool) -> None:
        was_blocked = action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(was_blocked)

    def _show_map_properties(self) -> None:
        dialog = self._map_properties_dialog_factory(self)
        dialog.exec()

    def _show_find_item(self) -> None:
        dialog = self._find_item_dialog_factory(self)
        result = dialog.exec()

        search_map_query = self._dialog_search_map_query(dialog)
        if search_map_query is not None:
            self._show_find_item_search_map_gap(search_map_query)
            return

        if result == int(QDialog.DialogCode.Accepted):
            selected_result = dialog.selected_result()
            if selected_result is not None:
                self._set_active_item_selection(
                    selected_result.name,
                    selected_result.server_id,
                )

    def _show_search_map_gap(self, search_kind: str) -> None:
        self._status_bar().showMessage(
            f"Search on map ({search_kind}) is not available yet.",
            3000,
        )

    def _dialog_search_map_query(self, dialog) -> object | None:
        if hasattr(dialog, "last_search_map_query"):
            return cast("object | None", dialog.last_search_map_query())
        return cast("object | None", getattr(dialog, "_last_search_map_query", None))

    def _show_find_item_search_map_gap(self, query) -> None:
        search_text = getattr(query, "search_text", "").strip()
        detail = f" for '{search_text}'" if search_text else ""
        self._status_bar().showMessage(
            f"Search on map{detail} is not available yet.",
            3000,
        )

    def _show_replace_items(self) -> None:
        self._status_bar().showMessage("Replace Items is not available yet.", 3000)

    def _show_edit_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_map_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_map_statistics(self) -> None:
        self._status_bar().showMessage("Map Statistics is not available yet.", 3000)

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

    def _go_to_previous_position(self) -> None:
        viewport = self._active_viewport()
        previous = viewport.previous_position
        if previous is None:
            self._status_bar().showMessage("No previous position stored.", 3000)
            return
        current = viewport.center
        viewport.set_previous_position(current)
        self._set_current_position(*previous)
        self._status_bar().showMessage(
            f"Returned to previous position {previous[0]}, {previous[1]}, {previous[2]:02d}",
            3000,
        )

    def _show_jump_to_brush(self) -> None:
        if self.brush_palette_dock is None:
            self._status_bar().showMessage("Palette dock is not available in this window.", 3000)
            return

        active_brush_id = self._editor_context.session.active_brush_id
        if active_brush_id and active_brush_id.startswith("palette:"):
            palette_name = active_brush_id.removeprefix("palette:")
            resolved_palette = next(
                (
                    name
                    for name in self.brush_palette_dock.palette_names()
                    if name.casefold() == palette_name
                ),
                self._active_brush_name,
            )
            self.brush_palette_dock.show()
            self.brush_palette_dock.raise_()
            self.brush_palette_dock.focus_palette(resolved_palette)
            self._status_bar().showMessage(
                f"Palette focused for {resolved_palette}.",
                3000,
            )
            return

        search_text = ""
        if self._active_brush_name not in self.brush_palette_dock.palette_names() and (
            self._active_brush_name != "Select"
        ):
            search_text = self._active_brush_name
        self.brush_palette_dock.show()
        self.brush_palette_dock.raise_()
        if search_text:
            self.brush_palette_dock.focus_palette("Item", search_text)
            self._status_bar().showMessage(
                f"Item palette focused for {search_text}.",
                3000,
            )
            return
        self.brush_palette_dock.focus_palette(self.brush_palette_dock.current_palette())
        self._status_bar().showMessage("Brush palette focused.", 3000)

    def _show_jump_to_item(self) -> None:
        if self.brush_palette_dock is None:
            self._status_bar().showMessage("Palette dock is not available in this window.", 3000)
            return
        search_text = ""
        if self._active_brush_name not in self.brush_palette_dock.palette_names() and (
            self._active_brush_name != "Select"
        ):
            search_text = self._active_brush_name
        self.brush_palette_dock.show()
        self.brush_palette_dock.raise_()
        self.brush_palette_dock.focus_palette("Item", search_text)
        message = "Item palette focused."
        if search_text:
            message = f"Item palette focused for {search_text}."
        self._status_bar().showMessage(message, 3000)

    def _show_new_palette(self) -> None:
        if self.brush_palette_dock is None:
            self._status_bar().showMessage("Palette dock is not available in this window.", 3000)
            return
        self.brush_palette_dock.show()
        self.brush_palette_dock.raise_()
        self._status_bar().showMessage(
            "New Palette reuses the shared palette dock in this slice.",
            3000,
        )

    def _show_palette(self, palette_name: str) -> None:
        if self.brush_palette_dock is None:
            self._status_bar().showMessage("Palette dock is not available in this window.", 3000)
            return
        self.brush_palette_dock.show()
        self.brush_palette_dock.raise_()
        self.brush_palette_dock.focus_palette(palette_name)
        self._active_brush_name = palette_name
        self._editor_context.session.editor.activate_palette_brush(palette_name)
        self._sync_canvas_shell_state()
        self._status_bar().showMessage(f"Palette switched to {palette_name}.", 3000)

    def _select_item_brush(self, entry) -> None:
        item_id = entry.item_id if getattr(entry, "item_id", None) is not None else entry.server_id
        self._set_active_item_selection(entry.name, item_id)

    def _set_active_item_selection(self, name: str, item_id: int) -> None:
        self._active_brush_name = name
        self._editor_context.session.editor.activate_item_brush(item_id)
        self._sync_canvas_shell_state()
        self._status_bar().showMessage(
            f"Selected item {name} (#{item_id}).",
            3000,
        )

    def _describe_floor(self, z: int) -> str:
        if z < 7:
            return "Above Ground"
        if z == 7:
            return "Ground"
        return "Below Ground"

    def _set_current_position(
        self,
        x: int,
        y: int,
        z: int,
        *,
        track_history: bool = False,
        announce: bool = False,
    ) -> None:
        self._active_viewport().set_center(x, y, z, track_history=track_history)
        self._mirror_active_viewport_state()
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
        self._persist_active_view_state()

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
            announce=True,
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

    def _toggle_show_grid(self, checked: bool) -> None:
        self._show_grid_enabled = checked
        self._view_flag_state["show_grid"] = checked
        self._canvas.set_show_grid(checked)
        self._persist_active_view_state()
        self._status_bar().showMessage(
            f"Show Grid {'ON' if checked else 'OFF'}",
            3000,
        )

    def _stub_ghost_higher(self, checked: bool) -> None:
        self._ghost_higher_enabled = checked
        self._view_flag_state["ghost_higher_floors"] = checked
        self._canvas.set_ghost_higher(checked)
        self._persist_active_view_state()

    def _set_view_flag(self, action_key: str, view_flag: str, checked: bool) -> None:
        self._view_flag_state[action_key] = checked
        if implements_editor_view_flag_canvas_protocol(self._canvas):
            canvas = cast("EditorViewFlagCanvasProtocol", self._canvas)
            canvas.set_view_flag(view_flag, checked)
        self._persist_active_view_state()
        if action_key == "view_show_all_floors":
            self._refresh_selection_action_state()
        self._status_bar().showMessage(
            f"{PHASE1_ACTIONS[action_key].text}: {'ON' if checked else 'OFF'}",
            3000,
        )

    def _set_show_flag(self, action_key: str, show_flag: str, checked: bool) -> None:
        self._show_flag_state[action_key] = checked
        if implements_editor_show_flag_canvas_protocol(self._canvas):
            canvas = cast("EditorShowFlagCanvasProtocol", self._canvas)
            canvas.set_show_flag(show_flag, checked)
        self._persist_active_view_state()
        self._status_bar().showMessage(
            f"{PHASE1_ACTIONS[action_key].text}: {'ON' if checked else 'OFF'}",
            3000,
        )

    def _set_edit_flag(self, action_key: str, checked: bool) -> None:
        self._edit_flag_state[action_key] = checked
        if action_key == "border_automagic":
            self._settings.setValue("main_window/border_automagic", checked)
            self._status_bar().showMessage(
                "Automagic enabled." if checked else "Automagic disabled.",
                3000,
            )
            return
        self._status_bar().showMessage(
            f"{PHASE1_ACTIONS[action_key].text}: {'ON' if checked else 'OFF'}",
            3000,
        )

    def _set_selection_compensate(self, checked: bool) -> None:
        self._selection_compensate = checked
        self._settings.setValue("main_window/select_mode_compensate", checked)

    def _set_selection_mode(self, mode: str, checked: bool) -> None:
        if not checked:
            return
        self._selection_mode = mode
        self._settings.setValue("main_window/selection_mode", mode)

    def _set_editor_mode(self, mode: str, checked: bool) -> None:
        if not checked:
            return
        self._editor_context.session.editor.set_mode(mode)
        self._sync_canvas_shell_state()
        self._status_bar().showMessage(
            f"Editor mode: {self._editor_mode_label(mode)}.",
            3000,
        )

    def _editor_mode_label(self, mode: str) -> str:
        labels = {
            "selection": "Select",
            "drawing": "Draw",
            "erasing": "Erase",
            "fill": "Fill",
            "move": "Move",
        }
        return labels.get(mode, "Draw")

    def _sync_brush_mode_actions(self) -> None:
        if not self.brush_mode_actions:
            return
        current_mode = self._editor_context.session.mode
        if current_mode not in self.brush_mode_actions:
            current_mode = "drawing"
            self._editor_context.session.mode = current_mode
        for mode, action in self.brush_mode_actions.items():
            self._sync_checkable_action(action, mode == current_mode)

    def _refresh_selection_action_state(self) -> None:
        has_selection = self._editor_context.session.editor.has_selection()
        selection_keys = (
            "replace_on_selection_items",
            "search_on_selection_item",
            "remove_on_selection_item",
            "search_on_selection_everything",
            "search_on_selection_unique",
            "search_on_selection_action",
            "search_on_selection_container",
            "search_on_selection_writeable",
        )
        for key in selection_keys:
            self.selection_menu_actions[key].setEnabled(has_selection)

        self.edit_menu_actions["borderize_selection"].setEnabled(has_selection)
        self.edit_menu_actions["randomize_selection"].setEnabled(has_selection)

        multi_floor_enabled = self._view_flag_state.get(
            "view_show_all_floors",
            LEGACY_VIEW_FLAG_DEFAULTS["view_show_all_floors"],
        )
        self.selection_menu_actions["select_mode_lower"].setEnabled(multi_floor_enabled)
        self.selection_menu_actions["select_mode_visible"].setEnabled(multi_floor_enabled)
        if not multi_floor_enabled:
            self._selection_mode = "current"
            self._settings.setValue("main_window/selection_mode", self._selection_mode)

        self._sync_checkable_action(
            self.selection_menu_actions["select_mode_compensate"],
            self._selection_compensate,
        )
        self._sync_checkable_action(
            self.selection_menu_actions["select_mode_current"],
            self._selection_mode == "current",
        )
        self._sync_checkable_action(
            self.selection_menu_actions["select_mode_lower"],
            self._selection_mode == "lower",
        )
        self._sync_checkable_action(
            self.selection_menu_actions["select_mode_visible"],
            self._selection_mode == "visible",
        )

    def _show_selection_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_file_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_experimental_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_scripts_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_about_backend_gap(self, action_name: str) -> None:
        self._status_bar().showMessage(f"{action_name} is not available yet.", 3000)

    def _show_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_town_manager_dialog(self) -> None:
        dialog = TownManagerDialog(self)
        dialog.exec()

    def _show_preferences_dialog(self) -> None:
        dialog = PreferencesDialog(self)
        dialog.exec()

    def _stub_show_lower(self, checked: bool) -> None:
        self._show_lower_enabled = checked
        self._canvas.set_show_lower(checked)
        self._persist_active_view_state()

    # ── Editor menu handlers ────────────────────────────────────────

    def _editor_new_view(self) -> None:
        index = self._add_view_tab(
            self._view_title(),
            self._capture_shell_state(),
            viewport=self._capture_viewport_state(),
            minimap_viewport=self._capture_minimap_viewport_state(),
        )
        self._view_tabs.setCurrentIndex(index)
        self._status_bar().showMessage("Opened a new view of the current map.", 3000)

    def _editor_toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and normal windowed mode."""
        if self.isFullScreen():
            self.showNormal()
            self._status_bar().showMessage("Exited fullscreen mode.", 3000)
        else:
            self.showFullScreen()
            self._status_bar().showMessage("Entered fullscreen mode.", 3000)

    def _editor_take_screenshot(self) -> None:
        """Backend gap: screenshot requires canvas rendering (R032)."""
        self._status_bar().showMessage(
            "Take Screenshot is not available yet.", 3000,
        )

    def _editor_zoom_in(self) -> None:
        """Increase zoom by 10%."""
        viewport = self._active_viewport()
        viewport.set_zoom_percent(viewport.zoom_percent + 10)
        self._mirror_active_viewport_state()
        self._zoom_label.setText(f"{self._zoom_percent}%")
        self._sync_canvas_shell_state()
        self._persist_active_view_state()
        self._status_bar().showMessage(f"Zoom: {self._zoom_percent}%", 2000)

    def _editor_zoom_out(self) -> None:
        """Decrease zoom by 10%."""
        viewport = self._active_viewport()
        viewport.set_zoom_percent(viewport.zoom_percent - 10)
        self._mirror_active_viewport_state()
        self._zoom_label.setText(f"{self._zoom_percent}%")
        self._sync_canvas_shell_state()
        self._persist_active_view_state()
        self._status_bar().showMessage(f"Zoom: {self._zoom_percent}%", 2000)

    def _editor_zoom_normal(self) -> None:
        """Reset zoom to 100%."""
        self._active_viewport().set_zoom_percent(100)
        self._mirror_active_viewport_state()
        self._zoom_label.setText("100%")
        self._sync_canvas_shell_state()
        self._persist_active_view_state()
        self._status_bar().showMessage("Zoom: 100%", 2000)

    def _default_shell_state(self) -> ShellStateSnapshot:
        return ShellStateSnapshot(
            show_grid_enabled=False,
            ghost_higher_enabled=False,
            show_lower_enabled=True,
            view_flags=dict(LEGACY_VIEW_FLAG_DEFAULTS),
            show_flags=dict(LEGACY_SHOW_FLAG_DEFAULTS),
        )

    def _add_view_tab(
        self,
        title: str,
        shell_state: ShellStateSnapshot,
        *,
        viewport: ViewportSnapshot | None = None,
        minimap_viewport: MinimapViewportState | None = None,
    ) -> int:
        raw_canvas = self._canvas_factory(self._view_tabs)
        if not implements_canvas_widget_protocol(raw_canvas):
            raise TypeError(
                "canvas_factory must return a QWidget implementing "
                "CanvasWidgetProtocol"
            )
        canvas = cast("CanvasWidgetProtocol", raw_canvas)
        canvas.bind_editor_context(self._editor_context)
        if implements_editor_tool_callback_canvas_protocol(canvas):
            callback_canvas = cast("EditorToolCallbackCanvasProtocol", canvas)
            callback_canvas.set_tool_applied_callback(self._on_canvas_tool_applied)
        record = EditorViewRecord(
            canvas=canvas,
            editor_context=self._editor_context,
            shell_state=shell_state,
            viewport=EditorViewport(viewport or self._default_viewport_state()),
            minimap_viewport=minimap_viewport or self._default_minimap_viewport_state(),
        )
        self._views.append(record)
        return self._view_tabs.addTab(cast("QWidget", canvas), title)

    def _active_view(self) -> EditorViewRecord:
        return self._views[self._active_view_index]

    def _active_viewport(self) -> EditorViewport:
        return self._active_view().viewport

    def _mirror_active_viewport_state(self) -> None:
        viewport = self._active_viewport()
        self._current_x = viewport.center_x
        self._current_y = viewport.center_y
        self._current_z = viewport.floor
        self._zoom_percent = viewport.zoom_percent
        self._previous_position = viewport.previous_position

    def _sync_active_viewport_size_from_canvas(self) -> None:
        widget = cast("QWidget", self._canvas)
        size = widget.size()
        scale_factor = 1.0
        if hasattr(widget, "devicePixelRatioF"):
            scale_factor = float(widget.devicePixelRatioF())
        self._active_viewport().set_view_size(
            size.width(),
            size.height(),
            scale_factor=scale_factor,
        )
        self._mirror_active_viewport_state()

    def _persist_active_view_state(self) -> None:
        if not self._views:
            return
        view = self._active_view()
        view.shell_state = self._capture_shell_state()
        view.minimap_viewport = self._capture_minimap_viewport_state()

    def _on_view_changed(self, index: int) -> None:
        if index < 0 or index >= len(self._views):
            return
        self._persist_active_view_state()
        self._active_view_index = index
        self._canvas = self._active_view().canvas
        self._apply_shell_state(self._active_view().shell_state)

    def _capture_shell_state(self) -> ShellStateSnapshot:
        self._mirror_active_viewport_state()
        return ShellStateSnapshot(
            show_grid_enabled=self._show_grid_enabled,
            ghost_higher_enabled=self._ghost_higher_enabled,
            show_lower_enabled=self._show_lower_enabled,
            view_flags=dict(self._view_flag_state),
            show_flags=dict(self._show_flag_state),
        )

    def _default_viewport_state(self) -> ViewportSnapshot:
        x, y, z = self.DEFAULT_POSITION
        return ViewportSnapshot(
            center_x=x,
            center_y=y,
            floor=z,
            zoom_percent=100,
        )

    def _capture_viewport_state(self) -> ViewportSnapshot:
        return self._active_viewport().snapshot()

    def _default_minimap_viewport_state(self) -> MinimapViewportState:
        return MinimapViewportState(
            center_x=self.DEFAULT_POSITION[0],
            center_y=self.DEFAULT_POSITION[1],
            floor=self.DEFAULT_POSITION[2],
            zoom_percent=100,
        )

    def _capture_minimap_viewport_state(self) -> MinimapViewportState:
        viewport = self._active_viewport()
        return MinimapViewportState(
            center_x=viewport.center_x,
            center_y=viewport.center_y,
            floor=viewport.floor,
            zoom_percent=viewport.zoom_percent,
        )

    def _apply_shell_state(self, shell_state: ShellStateSnapshot) -> None:
        self._mirror_active_viewport_state()
        self._show_grid_enabled = shell_state.show_grid_enabled
        self._ghost_higher_enabled = shell_state.ghost_higher_enabled
        self._show_lower_enabled = shell_state.show_lower_enabled
        self._view_flag_state = dict(LEGACY_VIEW_FLAG_DEFAULTS)
        self._view_flag_state.update(shell_state.view_flags)
        self._show_flag_state = dict(LEGACY_SHOW_FLAG_DEFAULTS)
        self._show_flag_state.update(shell_state.show_flags)

        self._coord_label.setText(
            f"Pos: (X: {self._current_x}, Y: {self._current_y}, Z: {self._current_z:02d})"
        )
        self._items_label.setText(
            f"Floor {self._current_z} ({self._describe_floor(self._current_z)})"
        )
        self._zoom_label.setText(f"{self._zoom_percent}%")
        for action_key, action in self.view_menu_actions.items():
            self._sync_checkable_action(action, self._view_flag_state[action_key])
        for action_key, action in self.show_menu_actions.items():
            self._sync_checkable_action(action, self._show_flag_state[action_key])
        self._sync_checkable_action(self.show_lower_action, self._show_lower_enabled)
        self._sync_floor_actions(self._current_z)
        self._sync_canvas_shell_state()

    def _view_title(self) -> str:
        document = self._editor_context.session.document
        return f"{document.name}{'*' if document.is_dirty else ''}"

    def _window_title(self) -> str:
        return f"{self._view_title()} - {__app_name__} v{__version__}"

    def _refresh_view_titles(self) -> None:
        title = self._view_title()
        for index in range(self._view_tabs.count()):
            self._view_tabs.setTabText(index, title)
        self.setWindowTitle(self._window_title())

    def _finalize_active_tool_application(self, result: EditorToolApplyResult) -> bool:
        x, y, z = result.position.x, result.position.y, result.position.z
        if (x, y, z) != (self._current_x, self._current_y, self._current_z):
            self._set_current_position(x, y, z)
        self._refresh_selection_action_state()
        self._refresh_view_titles()
        self._sync_canvas_shell_state()
        self._persist_active_view_state()
        mode_label = self._editor_mode_label(self._editor_context.session.mode)
        if result.changed:
            self._status_bar().showMessage(
                f"Applied {mode_label} tool at {x}, {y}, {z:02d}.",
                3000,
            )
            return True
        self._status_bar().showMessage(
            f"No change from {mode_label} tool at {x}, {y}, {z:02d}.",
            3000,
        )
        return False

    def _on_canvas_tool_applied(self, result: EditorToolApplyResult) -> None:
        self._finalize_active_tool_application(result)

    def _apply_active_tool_at_cursor(self) -> bool:
        x, y, z = self._current_x, self._current_y, self._current_z
        if implements_editor_tool_canvas_protocol(self._canvas):
            canvas = cast("EditorToolCanvasProtocol", self._canvas)
            result = canvas.apply_active_tool()
        else:
            result = EditorToolApplyResult(
                changed=self._editor_context.session.editor.apply_active_tool_at(
                    MapPosition(x, y, z)
                ),
                position=MapPosition(x, y, z),
            )
        return self._finalize_active_tool_application(result)

    def _sync_canvas_shell_state(self) -> None:
        self._sync_active_viewport_size_from_canvas()
        self._mirror_active_viewport_state()
        self._sync_brush_mode_actions()
        self._canvas.set_position(self._current_x, self._current_y, self._current_z)
        self._canvas.set_floor(self._current_z)
        self._canvas.set_zoom(self._zoom_percent)
        if implements_editor_viewport_canvas_protocol(self._canvas):
            viewport_canvas = cast("EditorViewportCanvasProtocol", self._canvas)
            viewport_canvas.set_viewport_snapshot(self._active_viewport().snapshot())
        if implements_editor_frame_summary_canvas_protocol(self._canvas):
            frame_canvas = cast("EditorFrameSummaryCanvasProtocol", self._canvas)
            frame_plan = build_render_frame_plan(
                self._editor_context.session.editor.map_model,
                self._active_viewport(),
            )
            frame_canvas.set_frame_summary(frame_plan.summary())
            if implements_editor_frame_primitives_canvas_protocol(self._canvas):
                primitive_canvas = cast(
                    "EditorFramePrimitivesCanvasProtocol",
                    self._canvas,
                )
                primitive_canvas.set_frame_primitives(
                    build_diagnostic_tile_primitives(frame_plan, self._active_viewport())
                )
        self._canvas.set_show_grid(self._show_grid_enabled)
        self._canvas.set_ghost_higher(self._ghost_higher_enabled)
        self._canvas.set_show_lower(self._show_lower_enabled)
        if implements_editor_view_flag_canvas_protocol(self._canvas):
            view_flag_canvas = cast("EditorViewFlagCanvasProtocol", self._canvas)
            for action_key, enabled in self._view_flag_state.items():
                if action_key == "show_grid":
                    view_flag = "show_grid"
                elif action_key == "ghost_higher_floors":
                    view_flag = "ghost_higher_floors"
                else:
                    view_flag = action_key.removeprefix("view_")
                view_flag_canvas.set_view_flag(view_flag, enabled)
        if implements_editor_show_flag_canvas_protocol(self._canvas):
            show_flag_canvas = cast("EditorShowFlagCanvasProtocol", self._canvas)
            for action_key, enabled in self._show_flag_state.items():
                show_flag = "show_preview" if action_key == "show_animation" else action_key
                show_flag_canvas.set_show_flag(show_flag, enabled)
        if implements_editor_activation_canvas_protocol(self._canvas):
            activation_canvas = cast("EditorActivationCanvasProtocol", self._canvas)
            activation_canvas.set_editor_mode(self._editor_context.session.mode)
            activation_canvas.set_active_brush(
                self._active_brush_name,
                self._editor_context.session.active_brush_id,
                self._editor_context.session.active_item_id,
            )
        if self.tool_options_dock is not None:
            self.tool_options_dock.set_shell_state(
                mode_name=self._editor_mode_label(self._editor_context.session.mode),
                brush_name=self._active_brush_name,
                position=(self._current_x, self._current_y, self._current_z),
                zoom_percent=self._zoom_percent,
            )
        if self.ingame_preview_dock is not None:
            self.ingame_preview_dock.set_preview_state(
                "In-game preview is not wired in this slice.\n"
                f"Focus: {self._current_x}, {self._current_y}, {self._current_z:02d}"
            )

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

        current_x = self._coerce_int(
            self._settings.value("main_window/current_x", 32000),
            32000,
        )
        current_y = self._coerce_int(
            self._settings.value("main_window/current_y", 32000),
            32000,
        )
        current_z = self._coerce_int(
            self._settings.value("main_window/current_z", 7),
            7,
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
        border_automagic = self._coerce_bool(
            self._settings.value(
                "main_window/border_automagic",
                LEGACY_EDIT_STATE_DEFAULTS["border_automagic"],
            ),
            LEGACY_EDIT_STATE_DEFAULTS["border_automagic"],
        )
        self._sync_checkable_action(
            self.edit_menu_actions["border_automagic"],
            border_automagic,
        )
        self._edit_flag_state["border_automagic"] = border_automagic
        self._selection_compensate = self._coerce_bool(
            self._settings.value(
                "main_window/select_mode_compensate",
                LEGACY_SELECTION_MODE_DEFAULTS["select_mode_compensate"],
            ),
            LEGACY_SELECTION_MODE_DEFAULTS["select_mode_compensate"],
        )
        raw_selection_mode = self._settings.value("main_window/selection_mode", "current")
        self._selection_mode = str(raw_selection_mode)
        if self._selection_mode not in {"current", "lower", "visible"}:
            self._selection_mode = "current"
        self._refresh_selection_action_state()
        self._set_current_position(current_x, current_y, current_z)

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
        self._mirror_active_viewport_state()
        self._settings.setValue("main_window/geometry", self.saveGeometry())
        self._settings.setValue("main_window/state", self.saveState())
        self._settings.setValue("main_window/current_x", self._current_x)
        self._settings.setValue("main_window/current_y", self._current_y)
        self._settings.setValue("main_window/current_z", self._current_z)
        self._settings.setValue("main_window/show_grid", self._show_grid_enabled)
        self._settings.setValue("main_window/ghost_higher", self._ghost_higher_enabled)
        self._settings.setValue("main_window/show_lower", self._show_lower_enabled)
        self._settings.setValue(
            "main_window/border_automagic",
            self._edit_flag_state["border_automagic"],
        )
        self._settings.setValue(
            "main_window/select_mode_compensate",
            self._selection_compensate,
        )
        self._settings.setValue("main_window/selection_mode", self._selection_mode)
        self._settings.sync()
        super().closeEvent(event)
