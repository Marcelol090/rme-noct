"""Noct Map Editor Main Window - the editor shell."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import cast

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.editor import MapPosition
from pyrme.ui.canvas_host import (
    CanvasWidgetProtocol,
    EditorToolApplyResult,
    RendererHostCanvasWidget,
    implements_canvas_widget_protocol,
    implements_editor_activation_canvas_protocol,
    implements_editor_show_flag_canvas_protocol,
    implements_editor_tool_callback_canvas_protocol,
    implements_editor_tool_canvas_protocol,
    implements_editor_view_flag_canvas_protocol,
    implements_editor_viewport_canvas_protocol,
)
from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.dialogs import (
    FindBrushDialog,
    FindItemDialog,
    GotoPositionDialog,
    MapPropertiesDialog,
)
from pyrme.ui.docks import BrushPaletteDock, MinimapDock, PropertiesDock, WaypointsDock
from pyrme.ui.editor_context import EditorContext, EditorViewRecord, ShellStateSnapshot
from pyrme.ui.legacy_menu_contract import (
    LEGACY_EDIT_STATE_DEFAULTS,
    LEGACY_TOP_LEVEL_MENUS,
    PHASE1_ACTIONS,
)
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY

logger = logging.getLogger(__name__)

CanvasFactory = Callable[[QWidget | None], QWidget]
QSETTINGS_BORDER_AUTOMAGIC = "editor/border_automagic"


class _MinimalResultModel:
    def __init__(self, palette: _MinimalItemPalette) -> None:
        self._palette = palette

    def index(self, row: int):
        return row

    def rowCount(self) -> int:  # noqa: N802
        return len(self._palette._filtered_entries)


class _MinimalItemPalette:
    def __init__(self, window: MainWindow) -> None:
        self._window = window
        self._entries = [
            ("Stone", 1),
            ("Gold Coin", 2148),
            ("Dragon Ham", 3582),
        ]
        self._filtered_entries = list(self._entries)
        self._result_model = _MinimalResultModel(self)

    def set_search_text(self, text: str) -> None:
        needle = text.strip().casefold()
        if not needle:
            self._filtered_entries = list(self._entries)
            return
        self._filtered_entries = [
            entry for entry in self._entries if needle in entry[0].casefold()
        ]

    def _on_result_clicked(self, index) -> None:
        if not self._filtered_entries:
            return
        row = index if isinstance(index, int) else 0
        row = max(0, min(row, len(self._filtered_entries) - 1))
        name, item_id = self._filtered_entries[row]
        self._window._set_active_item_selection(name, item_id)
        self._window._status_bar().showMessage(
            f"Selected item {name} (#{item_id}).",
            3000,
        )


class _ToolOptionsDock(GlassDockWidget):
    """Small tool-options surface for current editor mode."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("TOOL OPTIONS", parent)
        self.setObjectName("tool_options_dock")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        self._mode_label = QLabel("Draw")
        self._mode_label.setFont(TYPOGRAPHY.ui_label())
        self._mode_label.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        layout.addWidget(self._mode_label)
        layout.addStretch()
        self.set_inner_layout(layout)

    def set_mode_label(self, text: str) -> None:
        self._mode_label.setText(text)


class MainWindow(QMainWindow):
    """Main editor window for Noct Map Editor."""

    # Responsive design: desktop-only application target
    WINDOW_MIN_SIZE = QSize(1280, 720)
    WINDOW_DEFAULT_SIZE = QSize(1600, 1000)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        settings: QSettings | None = None,
        goto_dialog_factory=None,
        jump_to_brush_dialog_factory=None,
        jump_to_item_dialog_factory=None,
        find_item_dialog_factory=None,
        canvas_factory: CanvasFactory | None = None,
        enable_docks: bool | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings or QSettings("Noct Map Editor", "Noct")
        self._goto_dialog_factory = goto_dialog_factory or GotoPositionDialog
        self._jump_to_brush_dialog_factory = (
            jump_to_brush_dialog_factory or FindBrushDialog
        )
        self._jump_to_item_dialog_factory = jump_to_item_dialog_factory or (
            lambda parent=None: FindItemDialog(parent, window_title="Jump to Item")
        )
        self._find_item_dialog_factory = find_item_dialog_factory or FindItemDialog
        self._canvas_factory = canvas_factory or RendererHostCanvasWidget
        self._enable_docks = True if enable_docks is None else enable_docks
        self._editor_context = EditorContext()
        self._views: list[EditorViewRecord] = []
        self.brush_palette_dock: BrushPaletteDock | None = None
        self.tool_options_dock: _ToolOptionsDock | None = None
        self.minimap_dock: MinimapDock | None = None
        self.properties_dock: PropertiesDock | None = None
        self.waypoints_dock: WaypointsDock | None = None
        self.toggle_minimap_action: QAction | None = None
        self.toggle_floors_toolbar_action: QAction | None = None
        self.floor_toolbar: QToolBar | None = None
        self._current_x, self._current_y, self._current_z = (32000, 32000, 7)
        self._previous_position: tuple[int, int, int] | None = None
        self._zoom_percent = 100
        self._show_grid_enabled = False
        self._ghost_higher_enabled = False
        self._show_lower_enabled = True
        self._active_brush_name = "Select"
        self._active_brush_id: str | None = None
        self._active_item_id: int | None = None
        self._setup_window()
        self._setup_menu_bar()
        self._setup_toolbars()
        self._setup_central_widget()
        if self._enable_docks:
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
        self.jump_to_item_action = self._action_from_spec(
            "jump_to_item", self._show_jump_to_item
        )
        self.show_grid_action = self._action_from_spec("show_grid")
        self.show_grid_action.setCheckable(True)
        self.show_grid_action.toggled.connect(self._toggle_show_grid)
        self.ghost_higher_action = self._action_from_spec("ghost_higher_floors")
        self.ghost_higher_action.setCheckable(True)
        self.ghost_higher_action.toggled.connect(self._stub_ghost_higher)
        self.editor_zoom_in_action = self._action("Zoom In", "Ctrl++")
        self.editor_zoom_in_action.triggered.connect(self._zoom_in)

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
            if spec_key not in phase1_action_attrs:
                continue
            menu = self._menus[spec.menu_path[0]]
            action = phase1_action_attrs[spec_key]
            menu.addAction(action)

        self._setup_file_menu()
        self._setup_edit_menu()

        self.view_menu_actions: dict[str, QAction] = {
            "view_show_as_minimap": self._check_action(
                "Show as Minimap",
                lambda checked: self._set_view_flag("view_show_as_minimap", checked),
            )
        }
        self.show_menu_actions: dict[str, QAction] = {
            "show_light": self._check_action(
                "Show Light",
                lambda checked: self._set_show_flag("show_light", checked),
            )
        }
        self.selection_menu_actions: dict[str, QAction] = {
            "replace_on_selection_items": self._action("Replace on Selection Items")
        }
        self.selection_menu_actions["replace_on_selection_items"].setEnabled(False)

        self.brush_mode_actions: dict[str, QAction] = {}
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)
        for mode, label in (("selection", "Select"), ("drawing", "Draw")):
            action = self._action(label)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, value=mode: self._set_editor_mode(value)
                if checked
                else None
            )
            mode_group.addAction(action)
            self.brush_mode_actions[mode] = action
        self.brush_mode_actions["drawing"].setChecked(True)

    def _setup_file_menu(self) -> None:
        menu = self._menus["File"]
        self.file_new_action = self._action_from_spec(
            "file_new", lambda: self._show_unavailable("New")
        )
        self.file_open_action = self._action_from_spec(
            "file_open", lambda: self._show_unavailable("Open")
        )
        self.file_save_action = self._action_from_spec(
            "file_save", lambda: self._show_unavailable("Save")
        )
        self.file_save_as_action = self._action_from_spec(
            "file_save_as", lambda: self._show_unavailable("Save As")
        )
        self.file_generate_map_action = self._action_from_spec(
            "file_generate_map", lambda: self._show_unavailable("Generate Map")
        )
        self.file_close_action = self._action_from_spec(
            "file_close", lambda: self._show_unavailable("Close")
        )
        menu.addActions(
            [
                self.file_new_action,
                self.file_open_action,
                self.file_save_action,
                self.file_save_as_action,
                self.file_generate_map_action,
                self.file_close_action,
            ]
        )
        menu.addSeparator()

        import_menu = menu.addMenu("Import")
        assert import_menu is not None
        self.file_import_map_action = self._action_from_spec(
            "file_import_map", lambda: self._show_unavailable("Import Map")
        )
        self.file_import_monsters_action = self._action_from_spec(
            "file_import_monsters",
            lambda: self._show_unavailable("Import Monsters/NPC"),
        )
        import_menu.addActions(
            [self.file_import_map_action, self.file_import_monsters_action]
        )

        export_menu = menu.addMenu("Export")
        assert export_menu is not None
        self.file_export_minimap_action = self._action_from_spec(
            "file_export_minimap", lambda: self._show_unavailable("Export Minimap")
        )
        self.file_export_tilesets_action = self._action_from_spec(
            "file_export_tilesets", lambda: self._show_unavailable("Export Tilesets")
        )
        export_menu.addActions(
            [self.file_export_minimap_action, self.file_export_tilesets_action]
        )

        reload_menu = menu.addMenu("Reload")
        assert reload_menu is not None
        self.file_reload_data_action = self._action_from_spec(
            "file_reload_data", lambda: self._show_unavailable("Reload Data Files")
        )
        reload_menu.addAction(self.file_reload_data_action)

        self.file_missing_items_report_action = self._action_from_spec(
            "file_missing_items_report",
            lambda: self._show_unavailable("Missing Items Report"),
        )
        menu.addAction(self.file_missing_items_report_action)
        menu.addSeparator()
        recent_menu = menu.addMenu("Recent Files")
        assert recent_menu is not None
        self.file_preferences_action = self._action_from_spec(
            "file_preferences", lambda: self._show_unavailable("Preferences")
        )
        self.file_exit_action = self._action_from_spec(
            "file_exit", lambda: self._show_unavailable("Exit")
        )
        menu.addAction(self.file_preferences_action)
        menu.addAction(self.file_exit_action)

    def _setup_edit_menu(self) -> None:
        menu = self._menus["Edit"]
        menu.clear()

        self.edit_menu_actions: dict[str, QAction] = {}
        self.edit_undo_action = self._action_from_spec(
            "edit_undo", lambda: self._show_unavailable("Undo")
        )
        self.edit_redo_action = self._action_from_spec(
            "edit_redo", lambda: self._show_unavailable("Redo")
        )
        menu.addActions([self.edit_undo_action, self.edit_redo_action])
        menu.addSeparator()
        menu.addAction(self.replace_items_action)
        menu.addSeparator()

        border_menu = menu.addMenu("Border Options")
        assert border_menu is not None
        self.edit_menu_actions["border_automagic"] = self._action_from_spec(
            "border_automagic"
        )
        self.edit_menu_actions["border_automagic"].setCheckable(True)
        self._sync_checkable_action(
            self.edit_menu_actions["border_automagic"],
            self._coerce_bool(
                self._settings.value(
                    QSETTINGS_BORDER_AUTOMAGIC,
                    LEGACY_EDIT_STATE_DEFAULTS["border_automagic"],
                ),
                LEGACY_EDIT_STATE_DEFAULTS["border_automagic"],
            ),
        )
        self.edit_menu_actions["border_automagic"].toggled.connect(
            self._toggle_border_automagic
        )
        border_menu.addAction(self.edit_menu_actions["border_automagic"])
        border_menu.addSeparator()
        for key, label in (
            ("borderize_selection", "Borderize Selection"),
            ("borderize_map", "Borderize Map"),
            ("randomize_selection", "Randomize Selection"),
            ("randomize_map", "Randomize Map"),
        ):
            self.edit_menu_actions[key] = self._action_from_spec(
                key, lambda _checked=False, value=label: self._show_unavailable(value)
            )
            self.edit_menu_actions[key].setEnabled(False)
            border_menu.addAction(self.edit_menu_actions[key])

        other_menu = menu.addMenu("Other Options")
        assert other_menu is not None
        for key, label in (
            ("remove_items_by_id", "Remove Items by ID"),
            ("remove_all_corpses", "Remove all Corpses"),
            ("remove_all_unreachable_tiles", "Remove all Unreachable Tiles"),
            ("clear_invalid_houses", "Clear Invalid Houses"),
            ("clear_modified_state", "Clear Modified State"),
        ):
            self.edit_menu_actions[key] = self._action_from_spec(
                key, lambda _checked=False, value=label: self._show_unavailable(value)
            )
            other_menu.addAction(self.edit_menu_actions[key])

        menu.addSeparator()
        self.edit_cut_action = self._action_from_spec(
            "edit_cut", lambda: self._show_unavailable("Cut")
        )
        self.edit_copy_action = self._action_from_spec(
            "edit_copy", lambda: self._show_unavailable("Copy")
        )
        self.edit_paste_action = self._action_from_spec(
            "edit_paste", lambda: self._show_unavailable("Paste")
        )
        menu.addActions([self.edit_cut_action, self.edit_copy_action, self.edit_paste_action])

    def _setup_toolbars(self) -> None:
        """Create the main toolbars."""
        drawing_toolbar = QToolBar("Drawing Tools")
        drawing_toolbar.setObjectName("drawing_toolbar")
        drawing_toolbar.setMovable(True)
        drawing_toolbar.addAction(self.brush_mode_actions["selection"])
        drawing_toolbar.addAction(self.brush_mode_actions["drawing"])
        drawing_toolbar.addAction(self._action("Erase"))
        drawing_toolbar.addAction(self._action("Fill"))
        drawing_toolbar.addSeparator()
        drawing_toolbar.addAction(self._action("Move"))
        self.addToolBar(drawing_toolbar)

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

        self.floor_toolbar.addAction(self.editor_zoom_in_action)

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
        raw_canvas = self._canvas_factory(self)
        if not implements_canvas_widget_protocol(raw_canvas):
            raise TypeError("canvas_factory must return a CanvasWidgetProtocol widget")
        self._canvas: CanvasWidgetProtocol = raw_canvas
        self._canvas.bind_editor_context(self._editor_context)
        if implements_editor_tool_callback_canvas_protocol(self._canvas):
            self._canvas.set_tool_applied_callback(self._handle_tool_applied)
        view = EditorViewRecord(
            canvas=cast("CanvasWidgetProtocol", self._canvas),
            editor_context=self._editor_context,
            shell_state=ShellStateSnapshot(
                show_grid_enabled=self._show_grid_enabled,
                ghost_higher_enabled=self._ghost_higher_enabled,
                show_lower_enabled=self._show_lower_enabled,
                view_flags={},
                show_flags={},
            ),
        )
        self._views.append(view)
        self._view_tabs = QTabWidget(self)
        self._view_tabs.addTab(cast("QWidget", raw_canvas), "Untitled")
        self.setCentralWidget(self._view_tabs)

    def _setup_docks(self) -> None:
        """Create dock widgets for palettes and tools."""
        self.brush_palette_dock = BrushPaletteDock(self)
        self.brush_palette_dock.item_palette = _MinimalItemPalette(self)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.brush_palette_dock,
        )

        self.tool_options_dock = _ToolOptionsDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.tool_options_dock,
        )

        self.minimap_dock = MinimapDock(self)
        self.minimap_dock.z_up_btn.clicked.connect(self._floor_up)
        self.minimap_dock.z_down_btn.clicked.connect(self._floor_down)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.minimap_dock)
        self.toggle_minimap_action = self.minimap_dock.toggleViewAction()

        self.properties_dock = PropertiesDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        self.waypoints_dock = WaypointsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.waypoints_dock)

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

    def _check_action(self, text: str, handler) -> QAction:
        action = self._action(text)
        action.setCheckable(True)
        action.toggled.connect(handler)
        return action

    def _menu_label(self, title: str) -> str:
        return title

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

    def _show_unavailable(self, label: str) -> None:
        self._status_bar().showMessage(f"{label} is not available yet.", 3000)

    def _sync_checkable_action(self, action: QAction, checked: bool) -> None:
        was_blocked = action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(was_blocked)

    def _show_map_properties(self) -> None:
        dialog = MapPropertiesDialog(self)
        dialog.exec()

    def _show_find_item(self) -> None:
        dialog = self._find_item_dialog_factory(self)
        if dialog.exec() == int(QDialog.DialogCode.Accepted):
            self._apply_item_dialog_selection(dialog)
            return

        query = (
            dialog.last_search_map_query()
            if hasattr(dialog, "last_search_map_query")
            else None
        )
        if query is not None:
            self._status_bar().showMessage(
                f"Search on map for '{query.search_text}' is not available yet.",
                3000,
            )

    def _apply_item_dialog_selection(self, dialog: object) -> bool:
        selected = dialog.selected_result() if hasattr(dialog, "selected_result") else None
        if selected is None:
            return False
        try:
            item_id = selected.server_id
        except AttributeError:
            item_id = selected.item_id
        if item_id is None:
            item_id = selected.item_id
        self._set_active_item_selection(selected.name, int(item_id))
        self._status_bar().showMessage(
            f"Selected item {selected.name} (#{int(item_id)}).",
            3000,
        )
        return True

    def _show_replace_items(self) -> None:
        self._status_bar().showMessage("Replace Items is not available yet.", 3000)

    def _toggle_border_automagic(self, checked: bool) -> None:
        self._settings.setValue(QSETTINGS_BORDER_AUTOMAGIC, checked)
        self._settings.sync()
        self._status_bar().showMessage(
            f"Automagic {'enabled' if checked else 'disabled'}.",
            3000,
        )

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

    def _show_jump_to_brush(self) -> None:
        dialog = self._jump_to_brush_dialog_factory(self)
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        selected = dialog.selected_result() if hasattr(dialog, "selected_result") else None
        if selected is None:
            return
        if getattr(selected, "kind", None) == "item":
            item_id = getattr(selected, "item_id", None)
            if item_id is not None:
                self._set_active_item_selection(selected.name, int(item_id))
                self._status_bar().showMessage(
                    f"Selected item {selected.name} (#{int(item_id)}).",
                    3000,
                )
            return
        palette_name = getattr(selected, "palette_name", None)
        if palette_name is not None:
            self._show_palette(palette_name)

    def _show_jump_to_item(self) -> None:
        dialog = self._jump_to_item_dialog_factory(self)
        if dialog.exec() == int(QDialog.DialogCode.Accepted):
            self._apply_item_dialog_selection(dialog)
            return
        query = (
            dialog.last_search_map_query()
            if hasattr(dialog, "last_search_map_query")
            else None
        )
        if query is not None:
            self._status_bar().showMessage(
                f"Search on map for '{query.search_text}' is not available yet.",
                3000,
            )

    def _show_palette(self, name: str) -> None:
        if self.brush_palette_dock is None:
            self._status_bar().showMessage("Brush palette is not available.", 3000)
            return
        self.brush_palette_dock.show()
        self.brush_palette_dock.select_palette(name)
        self.brush_palette_dock.clear_search()
        self._active_brush_name = name
        self._active_brush_id = f"palette:{name.casefold()}"
        self._active_item_id = None
        self._editor_context.session.active_brush_id = self._active_brush_id
        self._editor_context.session.active_item_id = None
        self._sync_canvas_shell_state()
        self._status_bar().showMessage(f"Palette switched to {name}.", 3000)

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
        next_position = (
            max(0, min(65000, x)),
            max(0, min(65000, y)),
            max(0, min(15, z)),
        )
        current = (self._current_x, self._current_y, self._current_z)
        if track_history and next_position != current:
            self._previous_position = current

        self._current_x, self._current_y, self._current_z = next_position
        if self._views:
            self._active_view().viewport.set_center(
                self._current_x,
                self._current_y,
                self._current_z,
                track_history=track_history,
            )
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

    def _zoom_in(self) -> None:
        self._zoom_percent = min(800, self._zoom_percent + 10)
        if self._views:
            self._active_view().viewport.set_zoom_percent(self._zoom_percent)
        self._zoom_label.setText(f"{self._zoom_percent}%")
        self._sync_canvas_shell_state()

    def _toggle_show_grid(self, checked: bool) -> None:
        self._show_grid_enabled = checked
        self._canvas.set_show_grid(checked)
        if self._views:
            self._active_view().shell_state.view_flags["show_grid"] = checked
        self._status_bar().showMessage(
            f"Show Grid {'ON' if checked else 'OFF'}",
            3000,
        )

    def _stub_ghost_higher(self, checked: bool) -> None:
        self._ghost_higher_enabled = checked
        self._canvas.set_ghost_higher(checked)

    def _stub_show_lower(self, checked: bool) -> None:
        self._show_lower_enabled = checked
        self._canvas.set_show_lower(checked)

    def _active_view(self) -> EditorViewRecord:
        return self._views[self._view_tabs.currentIndex()]

    def _set_view_flag(self, name: str, enabled: bool) -> None:
        view = self._active_view()
        view.shell_state.view_flags[name] = enabled
        if implements_editor_view_flag_canvas_protocol(self._canvas):
            self._canvas.set_view_flag(name, enabled)

    def _set_show_flag(self, name: str, enabled: bool) -> None:
        view = self._active_view()
        view.shell_state.show_flags[name] = enabled
        if implements_editor_show_flag_canvas_protocol(self._canvas):
            self._canvas.set_show_flag(name, enabled)

    def _set_editor_mode(self, mode: str) -> None:
        self._editor_context.session.mode = self._normalized_editor_mode(mode)
        if implements_editor_activation_canvas_protocol(self._canvas):
            self._canvas.set_editor_mode(self._editor_context.session.mode)
        label = self._mode_label_for(self._editor_context.session.mode)
        if self.tool_options_dock is not None:
            self.tool_options_dock.set_mode_label(label)
        self._status_bar().showMessage(f"Editor mode: {label}.", 3000)

    def _normalized_editor_mode(self, mode: str) -> str:
        return mode if mode in {"selection", "drawing"} else "drawing"

    def _mode_label_for(self, mode: str) -> str:
        return {
            "selection": "Select",
            "drawing": "Draw",
        }.get(mode, "Draw")

    def _set_active_item_selection(self, name: str, item_id: int) -> None:
        self._active_brush_name = name
        self._active_brush_id = f"item:{item_id}"
        self._active_item_id = item_id
        self._editor_context.session.active_brush_id = self._active_brush_id
        self._editor_context.session.active_item_id = item_id
        if implements_editor_activation_canvas_protocol(self._canvas):
            self._canvas.set_active_brush(name, self._active_brush_id, item_id)

    def _apply_active_tool_at_cursor(self) -> bool:
        if implements_editor_tool_canvas_protocol(self._canvas):
            result = self._canvas.apply_active_tool()
        else:
            position = MapPosition(self._current_x, self._current_y, self._current_z)
            result = EditorToolApplyResult(
                changed=self._editor_context.session.editor.apply_active_tool_at(position),
                position=position,
            )
        self._handle_tool_applied(result)
        return result.changed

    def _handle_tool_applied(self, result: EditorToolApplyResult) -> None:
        self._set_current_position(result.position.x, result.position.y, result.position.z)
        self._refresh_selection_actions()
        self._refresh_dirty_chrome()
        mode = self._editor_context.session.mode
        tool_name = (
            "Select" if mode == "selection" else "Draw" if mode == "drawing" else mode.title()
        )
        self._status_bar().showMessage(
            f"Applied {tool_name} tool at {result.position.x}, "
            f"{result.position.y}, {result.position.z:02d}.",
            3000,
        )

    def _refresh_selection_actions(self) -> None:
        enabled = self._editor_context.session.editor.has_selection()
        self.selection_menu_actions["replace_on_selection_items"].setEnabled(enabled)
        if hasattr(self, "edit_menu_actions"):
            self.edit_menu_actions["borderize_selection"].setEnabled(enabled)
            self.edit_menu_actions["randomize_selection"].setEnabled(enabled)

    def _refresh_selection_action_state(self) -> None:
        self._refresh_selection_actions()

    def _refresh_dirty_chrome(self) -> None:
        dirty = self._editor_context.session.document.is_dirty
        label = "Untitled*" if dirty else "Untitled"
        if self._view_tabs.tabText(0) != label:
            self._view_tabs.setTabText(0, label)
        self.setWindowTitle(f"{label} - {__app_name__} v{__version__}")

    def _sync_canvas_shell_state(self) -> None:
        self._editor_context.session.mode = self._normalized_editor_mode(
            self._editor_context.session.mode
        )
        if self._views and implements_editor_viewport_canvas_protocol(self._canvas):
            self._canvas.set_viewport_snapshot(self._active_view().viewport.snapshot())
        self._canvas.set_position(self._current_x, self._current_y, self._current_z)
        self._canvas.set_floor(self._current_z)
        self._canvas.set_zoom(self._zoom_percent)
        self._canvas.set_show_grid(self._show_grid_enabled)
        self._canvas.set_ghost_higher(self._ghost_higher_enabled)
        self._canvas.set_show_lower(self._show_lower_enabled)
        if implements_editor_activation_canvas_protocol(self._canvas):
            self._canvas.set_editor_mode(self._editor_context.session.mode)
            self._canvas.set_active_brush(
                self._active_brush_name,
                self._active_brush_id,
                self._active_item_id,
            )
        mode = self._editor_context.session.mode
        if self.tool_options_dock is not None:
            self.tool_options_dock.set_mode_label(self._mode_label_for(mode))
        if mode in self.brush_mode_actions:
            self._sync_checkable_action(self.brush_mode_actions[mode], True)

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
        self._settings.setValue("main_window/geometry", self.saveGeometry())
        self._settings.setValue("main_window/state", self.saveState())
        self._settings.setValue("main_window/current_x", self._current_x)
        self._settings.setValue("main_window/current_y", self._current_y)
        self._settings.setValue("main_window/current_z", self._current_z)
        self._settings.setValue("main_window/show_grid", self._show_grid_enabled)
        self._settings.setValue("main_window/ghost_higher", self._ghost_higher_enabled)
        self._settings.setValue("main_window/show_lower", self._show_lower_enabled)
        self._settings.sync()
        super().closeEvent(event)
