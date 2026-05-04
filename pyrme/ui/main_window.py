"""Noct Map Editor Main Window - the editor shell."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, cast

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.core_bridge import create_editor_shell_state
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
    AboutDialog,
    FindBrushDialog,
    FindItemDialog,
    GotoPositionDialog,
    HouseManagerDialog,
    MapPropertiesDialog,
    MapStatisticsDialog,
    PreferencesDialog,
)
from pyrme.ui.dialogs.welcome_dialog import WelcomeDialog
from pyrme.ui.docks import BrushPaletteDock, MinimapDock, PropertiesDock, WaypointsDock
from pyrme.ui.editor_context import EditorContext, EditorViewRecord, ShellStateSnapshot
from pyrme.ui.legacy_menu_contract import (
    LEGACY_EDIT_STATE_DEFAULTS,
    LEGACY_SELECTION_MODE_DEFAULTS,
    LEGACY_SHOW_FLAG_DEFAULTS,
    LEGACY_TOP_LEVEL_MENUS,
    LEGACY_VIEW_FLAG_DEFAULTS,
    PHASE1_ACTIONS,
)
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY

if TYPE_CHECKING:
    from pyrme.ui.models.item_palette_types import ItemEntry
    from pyrme.ui.models.startup_models import StartupLoadRequest

logger = logging.getLogger(__name__)

CanvasFactory = Callable[[QWidget | None], QWidget]
DialogFactory = Callable[[QWidget | None], QDialog]
CloseDirtyDecision = Literal["save", "discard", "cancel"]
FileDataResultStatus = Literal["success", "deferred", "failure"]
ItemReplacement = tuple[int, int]

QSETTINGS_BORDER_AUTOMAGIC = "editor/border_automagic"
QSETTINGS_SELECTION_MODE = "editor/selection_mode"
QSETTINGS_SELECTION_COMPENSATE = "editor/selection_compensate"
QSETTINGS_RECENT_FILES = "file/recent_files"
MAX_RECENT_FILES = 10


class FileLifecycleService(Protocol):
    def choose_open_map_path(self, parent: QWidget) -> str | None: ...

    def choose_save_map_path(
        self,
        parent: QWidget,
        current_path: str | None = None,
    ) -> str | None: ...

    def confirm_close_dirty_document(
        self,
        parent: QWidget,
        document_name: str,
    ) -> CloseDirtyDecision: ...

    def load_map(
        self,
        path: str,
        current_context: EditorContext,
    ) -> EditorContext | None: ...

    def save_map(self, path: str, current_context: EditorContext) -> bool: ...


class QtFileLifecycleService:
    def choose_open_map_path(self, parent: QWidget) -> str | None:
        if QApplication.platformName() == "offscreen":
            return None
        path, _selected_filter = QFileDialog.getOpenFileName(
            parent,
            "Open Map",
            "",
            "OTBM Maps (*.otbm);;All Files (*)",
        )
        return path or None

    def choose_save_map_path(
        self,
        parent: QWidget,
        current_path: str | None = None,
    ) -> str | None:
        if QApplication.platformName() == "offscreen":
            return None
        path, _selected_filter = QFileDialog.getSaveFileName(
            parent,
            "Save Map As",
            current_path or "",
            "OTBM Maps (*.otbm);;All Files (*)",
        )
        return path or None

    def confirm_close_dirty_document(
        self,
        parent: QWidget,
        document_name: str,
    ) -> CloseDirtyDecision:
        if QApplication.platformName() == "offscreen":
            return "discard"
        result = QMessageBox.question(
            parent,
            "Unsaved Changes",
            f"Save changes to {document_name} before closing?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if result == QMessageBox.StandardButton.Save:
            return "save"
        if result == QMessageBox.StandardButton.Discard:
            return "discard"
        return "cancel"

    def load_map(
        self,
        path: str,
        current_context: EditorContext,
    ) -> EditorContext | None:
        del current_context
        bridge = create_editor_shell_state()
        if not bridge.load_otbm(path):
            return None
        context = EditorContext()
        context.session.document.persistence_handle = bridge
        return context

    def save_map(self, path: str, current_context: EditorContext) -> bool:
        handle = current_context.session.document.persistence_handle
        bridge = handle if hasattr(handle, "save_otbm") else create_editor_shell_state()
        if not bridge.save_otbm(path):
            return False
        current_context.session.document.persistence_handle = bridge
        return True


@dataclass(frozen=True, slots=True)
class FileDataActionResult:
    status: FileDataResultStatus
    message: str

    @classmethod
    def success(cls, message: str) -> FileDataActionResult:
        return cls(status="success", message=message)

    @classmethod
    def deferred(cls, message: str) -> FileDataActionResult:
        return cls(status="deferred", message=message)

    @classmethod
    def failure(cls, message: str) -> FileDataActionResult:
        return cls(status="failure", message=message)


class FileDataService(Protocol):
    def import_map(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult: ...

    def import_monsters_npc(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult: ...

    def export_minimap(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult: ...

    def export_tilesets(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult: ...

    def reload_data_files(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult: ...

    def missing_items_report(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult: ...


class DeferredFileDataService:
    def import_map(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult:
        del parent, current_context
        return FileDataActionResult.deferred(
            "Import Map deferred: needs core map merge/import offset/house/spawn "
            "policy backend.",
        )

    def import_monsters_npc(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult:
        del parent, current_context
        return FileDataActionResult.deferred(
            "Import Monsters/NPC deferred: needs OT monster/NPC XML creature-type "
            "catalog import backend.",
        )

    def export_minimap(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult:
        del parent, current_context
        return FileDataActionResult.deferred(
            "Export Minimap deferred: needs real minimap image renderer/exporter; "
            "legacy source is inconsistent.",
        )

    def export_tilesets(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult:
        del parent, current_context
        return FileDataActionResult.deferred(
            "Export Tilesets deferred: needs materials/tileset catalog exporter "
            "equivalent.",
        )

    def reload_data_files(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult:
        del parent, current_context
        return FileDataActionResult.deferred(
            "Reload Data Files deferred: needs selected client data root before client "
            "asset discovery can reload data files.",
        )

    def missing_items_report(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> FileDataActionResult:
        del parent, current_context
        return FileDataActionResult.deferred(
            "Missing Items Report deferred: needs version-manager missing item report "
            "backend.",
        )


class EditTransformService(Protocol):
    def choose_replace_items(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> ItemReplacement | None: ...

    def choose_remove_items_by_id(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> int | None: ...

    def confirm_map_transform(self, parent: QWidget, label: str) -> bool: ...


class DeferredEditTransformService:
    def choose_replace_items(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> ItemReplacement | None:
        del parent, current_context
        return None

    def choose_remove_items_by_id(
        self,
        parent: QWidget,
        current_context: EditorContext,
    ) -> int | None:
        del parent, current_context
        return None

    def confirm_map_transform(self, parent: QWidget, label: str) -> bool:
        if QApplication.platformName() == "offscreen":
            return False
        result = QMessageBox.question(
            parent,
            label,
            f"Apply {label} to the current map?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes


class TownManagerDialog(QDialog):
    """Safe placeholder until the full town manager dialog is mounted."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Town Manager")


class _ToolOptionsDock(GlassDockWidget):
    """Small honest tool-options surface for current editor mode."""

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
        map_properties_dialog_factory: DialogFactory | None = None,
        house_manager_dialog_factory: DialogFactory | None = None,
        file_lifecycle_service: FileLifecycleService | None = None,
        file_data_service: FileDataService | None = None,
        edit_transform_service: EditTransformService | None = None,
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
        self._map_properties_dialog_factory = (
            map_properties_dialog_factory or MapPropertiesDialog
        )
        self._house_manager_dialog_factory = (
            house_manager_dialog_factory or HouseManagerDialog
        )
        self._file_lifecycle_service = (
            file_lifecycle_service or QtFileLifecycleService()
        )
        self._file_data_service = file_data_service or DeferredFileDataService()
        self._edit_transform_service = (
            edit_transform_service or DeferredEditTransformService()
        )
        self._canvas_factory = canvas_factory or RendererHostCanvasWidget
        self._enable_docks = True if enable_docks is None else enable_docks
        self._editor_context = EditorContext()
        self._views: list[EditorViewRecord] = []
        self.brush_palette_dock: BrushPaletteDock | None = None
        self.tool_options_dock: _ToolOptionsDock | None = None
        self.minimap_dock: MinimapDock | None = None
        self.properties_dock: PropertiesDock | None = None
        self.waypoints_dock: WaypointsDock | None = None
        self.ingame_preview_dock: GlassDockWidget | None = None
        self.toggle_minimap_action: QAction | None = None
        self.toggle_floors_toolbar_action: QAction | None = None
        self.drawing_toolbar: QToolBar | None = None
        self.floor_toolbar: QToolBar | None = None
        self.sizes_toolbar: QToolBar | None = None
        self.standard_toolbar: QToolBar | None = None
        self._current_x, self._current_y, self._current_z = (32000, 32000, 7)
        self._previous_position: tuple[int, int, int] | None = None
        self._zoom_percent = 100
        self._show_grid_enabled = False
        self._ghost_higher_enabled = False
        self._show_lower_enabled = True
        self._active_brush_name = "Select"
        self._active_brush_id: str | None = None
        self._active_item_id: int | None = None
        self._welcome_dialog: WelcomeDialog | None = None
        self._setup_window()
        self._setup_menu_bar()
        self._setup_toolbars()
        self._setup_central_widget()
        if self._enable_docks:
            self._setup_docks()
        self._setup_status_bar()
        self._restore_window_state()
        self._sync_canvas_shell_state()
        self._refresh_selection_action_state()

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

    def show_startup_dashboard(self) -> None:
        """Display the welcome dialog dashboard."""
        if self._welcome_dialog is None:
            self._welcome_dialog = WelcomeDialog(parent=self)
            self._welcome_dialog.new_map_requested.connect(self._on_welcome_new_map)
            self._welcome_dialog.browse_map_requested.connect(
                self._on_welcome_browse_map
            )
            self._welcome_dialog.load_requested.connect(self._on_welcome_load_map)
            self._welcome_dialog.preferences_requested.connect(self._show_preferences)
            self._welcome_dialog.rejected.connect(self._on_welcome_rejected)
        self._welcome_dialog.show()

    def _on_welcome_new_map(self) -> None:
        if self._welcome_dialog is not None:
            self._welcome_dialog.accept()
        self.file_new_action.trigger()

    def _on_welcome_browse_map(self) -> None:
        if self._welcome_dialog is not None:
            self._welcome_dialog.accept()
        self.file_open_action.trigger()

    def _on_welcome_load_map(self, request: StartupLoadRequest) -> None:
        if self._welcome_dialog is not None:
            self._welcome_dialog.accept()
        self._open_map_file(request.map_path)

    def _on_welcome_rejected(self) -> None:
        pass

    def _open_map_file(self, path: str) -> None:
        try:
            loaded_context = self._file_lifecycle_service.load_map(
                path,
                self._editor_context,
            )
        except Exception:
            logger.exception("Failed to load map %s", path)
            loaded_context = None
        if loaded_context is None:
            self._status_bar().showMessage("Open is not available yet.", 3000)
            return
        self._replace_editor_context(loaded_context)
        self._set_current_document_path(path)
        self._editor_context.session.document.is_dirty = False
        self._add_recent_file(path)
        self._refresh_dirty_chrome()
        self._status_bar().showMessage(f"Opened map: {path}", 3000)

    def _setup_menu_bar(self) -> None:
        """Create the main menu bar."""
        menu_bar = self.menuBar()
        assert menu_bar is not None
        menu_bar.clear()
        menu_bar.setFont(TYPOGRAPHY.ui_label())
        self._menus = {}
        for title in LEGACY_TOP_LEVEL_MENUS:
            menu = menu_bar.addMenu(self._menu_label(title))
            assert menu is not None
            self._menus[title] = menu

        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_editor_menu()
        self._setup_search_menu()
        self._setup_map_menu()
        self._setup_selection_menu()
        self._setup_view_menu()
        self._setup_show_menu()
        self._setup_navigate_menu()
        self._setup_window_menu()
        self._setup_tail_menus()

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
        self.file_new_action = self._action_from_spec("file_new", self._new_map)
        self.file_open_action = self._action_from_spec("file_open", self._open_map)
        self.file_save_action = self._action_from_spec("file_save", self._save_map)
        self.file_save_as_action = self._action_from_spec(
            "file_save_as", self._save_map_as
        )
        self.file_generate_map_action = self._action_from_spec(
            "file_generate_map", lambda: self._show_unavailable("Generate Map")
        )
        self.file_close_action = self._action_from_spec("file_close", self._close_map)
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
            "file_import_map", self._import_map
        )
        self.file_import_monsters_action = self._action_from_spec(
            "file_import_monsters",
            self._import_monsters_npc,
        )
        import_menu.addActions(
            [self.file_import_map_action, self.file_import_monsters_action]
        )

        export_menu = menu.addMenu("Export")
        assert export_menu is not None
        self.file_export_minimap_action = self._action_from_spec(
            "file_export_minimap", self._export_minimap
        )
        self.file_export_tilesets_action = self._action_from_spec(
            "file_export_tilesets", self._export_tilesets
        )
        export_menu.addActions(
            [self.file_export_minimap_action, self.file_export_tilesets_action]
        )

        reload_menu = menu.addMenu("Reload")
        assert reload_menu is not None
        self.file_reload_data_action = self._action_from_spec(
            "file_reload_data", self._reload_data_files
        )
        reload_menu.addAction(self.file_reload_data_action)

        self.file_missing_items_report_action = self._action_from_spec(
            "file_missing_items_report",
            self._missing_items_report,
        )
        menu.addAction(self.file_missing_items_report_action)
        menu.addSeparator()
        self.recent_files_menu = menu.addMenu("Recent Files")
        assert self.recent_files_menu is not None
        self._rebuild_recent_files_menu()
        self.file_preferences_action = self._action_from_spec(
            "file_preferences", self._show_preferences
        )
        self.file_exit_action = self._action_from_spec("file_exit", self._exit)
        menu.addAction(self.file_preferences_action)
        menu.addAction(self.file_exit_action)

    def _setup_edit_menu(self) -> None:
        menu = self._menus["Edit"]
        self.edit_menu_actions: dict[str, QAction] = {}
        self.edit_undo_action = self._action_from_spec("edit_undo", self._undo_edit)
        self.edit_redo_action = self._action_from_spec("edit_redo", self._redo_edit)
        self.replace_items_action = self._action_from_spec(
            "replace_items", self._replace_items
        )
        menu.addActions([self.edit_undo_action, self.edit_redo_action])
        menu.addSeparator()
        menu.addAction(self.replace_items_action)
        menu.addSeparator()

        border_menu = menu.addMenu("Border Options")
        assert border_menu is not None
        self.edit_menu_actions["border_automagic"] = self._check_action_from_spec(
            "border_automagic",
            self._restore_bool(
                QSETTINGS_BORDER_AUTOMAGIC,
                LEGACY_EDIT_STATE_DEFAULTS["border_automagic"],
            ),
            self._toggle_border_automagic,
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
                key, lambda _checked=False, value=label: self._defer_edit_transform(value)
            )
            border_menu.addAction(self.edit_menu_actions[key])

        other_menu = menu.addMenu("Other Options")
        assert other_menu is not None
        other_handlers = (
            ("remove_items_by_id", self._remove_items_by_id),
            ("remove_all_corpses", "Remove all Corpses"),
            ("remove_all_unreachable_tiles", "Remove all Unreachable Tiles"),
            ("clear_invalid_houses", "Clear Invalid Houses"),
            ("clear_modified_state", self._clear_modified_state),
        )
        for key, handler in other_handlers:
            callback = (
                handler
                if callable(handler)
                else lambda _checked=False, value=handler: self._defer_edit_transform(value)
            )
            self.edit_menu_actions[key] = self._action_from_spec(
                key,
                callback,
            )
            other_menu.addAction(self.edit_menu_actions[key])

        menu.addSeparator()
        self.edit_cut_action = self._action_from_spec("edit_cut", self._cut_selection)
        self.edit_copy_action = self._action_from_spec("edit_copy", self._copy_selection)
        self.edit_paste_action = self._action_from_spec(
            "edit_paste", self._paste_clipboard
        )
        menu.addActions([self.edit_cut_action, self.edit_copy_action, self.edit_paste_action])
        self.edit_menu_actions.update(
            {
                "edit_undo": self.edit_undo_action,
                "edit_redo": self.edit_redo_action,
                "edit_cut": self.edit_cut_action,
                "edit_copy": self.edit_copy_action,
                "edit_paste": self.edit_paste_action,
            }
        )
        self._refresh_edit_action_state()

    def _setup_editor_menu(self) -> None:
        menu = self._menus["Editor"]
        self.editor_new_view_action = self._action_from_spec(
            "editor_new_view", self._new_view
        )
        self.editor_fullscreen_action = self._action_from_spec(
            "editor_fullscreen", self._toggle_fullscreen
        )
        self.editor_screenshot_action = self._action_from_spec(
            "editor_screenshot", self._take_screenshot
        )
        menu.addActions(
            [
                self.editor_new_view_action,
                self.editor_fullscreen_action,
                self.editor_screenshot_action,
            ]
        )
        menu.addSeparator()
        zoom_menu = menu.addMenu("Zoom")
        assert zoom_menu is not None
        self.editor_zoom_in_action = self._action_from_spec("editor_zoom_in", self._zoom_in)
        self.editor_zoom_out_action = self._action_from_spec(
            "editor_zoom_out", self._zoom_out
        )
        self.editor_zoom_normal_action = self._action_from_spec(
            "editor_zoom_normal", self._zoom_normal
        )
        zoom_menu.addActions(
            [
                self.editor_zoom_in_action,
                self.editor_zoom_out_action,
                self.editor_zoom_normal_action,
            ]
        )

    def _setup_search_menu(self) -> None:
        menu = self._menus["Search"]
        self.find_item_action = self._action_from_spec("find_item", self._show_find_item)
        menu.addAction(self.find_item_action)
        menu.addSeparator()
        self.search_on_map_unique_action = self._search_gap_action(
            "search_on_map_unique", "Find Unique"
        )
        self.search_on_map_action_action = self._search_gap_action(
            "search_on_map_action", "Find Action"
        )
        self.search_on_map_container_action = self._search_gap_action(
            "search_on_map_container", "Find Container"
        )
        self.search_on_map_writeable_action = self._search_gap_action(
            "search_on_map_writeable", "Find Writeable"
        )
        menu.addActions(
            [
                self.search_on_map_unique_action,
                self.search_on_map_action_action,
                self.search_on_map_container_action,
                self.search_on_map_writeable_action,
            ]
        )
        menu.addSeparator()
        self.search_on_map_everything_action = self._search_gap_action(
            "search_on_map_everything", "Find Everything"
        )
        menu.addAction(self.search_on_map_everything_action)

    def _setup_map_menu(self) -> None:
        menu = self._menus["Map"]
        self.map_edit_towns_action = self._action_from_spec(
            "map_edit_towns", self._show_town_manager
        )
        self.map_edit_houses_action = self._action_from_spec(
            "map_edit_houses", self._show_house_manager
        )
        self.map_cleanup_invalid_tiles_action = self._action_from_spec(
            "map_cleanup_invalid_tiles",
            lambda: self._show_unavailable("Cleanup invalid tiles"),
        )
        self.map_cleanup_invalid_zones_action = self._action_from_spec(
            "map_cleanup_invalid_zones",
            lambda: self._show_unavailable("Cleanup invalid zones"),
        )
        self.map_properties_action = self._action_from_spec(
            "map_properties", self._show_map_properties
        )
        self.map_statistics_action = self._action_from_spec(
            "map_statistics", self._show_map_statistics
        )
        menu.addAction(self.map_edit_towns_action)
        menu.addAction(self.map_edit_houses_action)
        menu.addSeparator()
        menu.addActions(
            [
                self.map_cleanup_invalid_tiles_action,
                self.map_cleanup_invalid_zones_action,
                self.map_properties_action,
                self.map_statistics_action,
            ]
        )

    def _setup_selection_menu(self) -> None:
        menu = self._menus["Selection"]
        self.selection_menu_actions = {}
        for key, label in (
            ("replace_on_selection_items", "Replace Items on Selection"),
            ("search_on_selection_item", "Find Item on Selection"),
            ("remove_on_selection_item", "Remove Item on Selection"),
        ):
            self.selection_menu_actions[key] = self._action_from_spec(
                key, lambda _checked=False, value=label: self._show_unavailable(value)
            )
            menu.addAction(self.selection_menu_actions[key])
        menu.addSeparator()

        find_menu = menu.addMenu("Find on Selection")
        assert find_menu is not None
        for key, label in (
            ("search_on_selection_everything", "Find Everything"),
            ("search_on_selection_unique", "Find Unique"),
            ("search_on_selection_action", "Find Action"),
            ("search_on_selection_container", "Find Container"),
            ("search_on_selection_writeable", "Find Writeable"),
        ):
            if key == "search_on_selection_unique":
                find_menu.addSeparator()
            self.selection_menu_actions[key] = self._action_from_spec(
                key, lambda _checked=False, value=label: self._show_unavailable(value)
            )
            find_menu.addAction(self.selection_menu_actions[key])
        menu.addSeparator()

        mode_menu = menu.addMenu("Selection Mode")
        assert mode_menu is not None
        self.selection_menu_actions["select_mode_compensate"] = (
            self._check_action_from_spec(
                "select_mode_compensate",
                self._restore_bool(
                    QSETTINGS_SELECTION_COMPENSATE,
                    LEGACY_SELECTION_MODE_DEFAULTS["select_mode_compensate"],
                ),
                self._persist_selection_mode,
            )
        )
        mode_menu.addAction(self.selection_menu_actions["select_mode_compensate"])
        mode_menu.addSeparator()
        selection_group = QActionGroup(self)
        selection_group.setExclusive(True)
        restored_mode = str(
            self._settings.value(QSETTINGS_SELECTION_MODE, "current")
        ).lower()
        for key, mode in (
            ("select_mode_current", "current"),
            ("select_mode_lower", "lower"),
            ("select_mode_visible", "visible"),
        ):
            action = self._check_action_from_spec(
                key,
                restored_mode == mode,
                self._persist_selection_mode,
            )
            selection_group.addAction(action)
            self.selection_menu_actions[key] = action
            mode_menu.addAction(action)
        if not any(
            self.selection_menu_actions[key].isChecked()
            for key in ("select_mode_current", "select_mode_lower", "select_mode_visible")
        ):
            self.selection_menu_actions["select_mode_current"].setChecked(True)

        menu.addSeparator()
        menu.addAction(self.edit_menu_actions["borderize_selection"])
        menu.addAction(self.edit_menu_actions["randomize_selection"])

    def _setup_view_menu(self) -> None:
        menu = self._menus["View"]
        self.view_menu_actions: dict[str, QAction] = {}
        for key in (
            "view_show_all_floors",
            "view_show_as_minimap",
            "view_only_show_colors",
            "view_only_show_modified",
            "view_always_show_zones",
            "view_extended_house_shader",
        ):
            self._add_view_action(menu, key)
        menu.addSeparator()
        for key in ("view_show_tooltips", "show_grid", "view_show_client_box"):
            self._add_view_action(menu, key)
        menu.addSeparator()
        for key in ("view_ghost_loose_items", "ghost_higher_floors", "view_show_shade"):
            self._add_view_action(menu, key)

        self.show_grid_action = self.view_menu_actions["show_grid"]
        self.ghost_higher_action = self.view_menu_actions["ghost_higher_floors"]

    def _setup_show_menu(self) -> None:
        menu = self._menus["Show"]
        self.show_menu_actions: dict[str, QAction] = {}
        for key in (
            "show_animation",
            "show_light",
            "show_light_strength",
            "show_technical_items",
            "show_invalid_tiles",
            "show_invalid_zones",
        ):
            self._add_show_action(menu, key)
        menu.addSeparator()
        for key in (
            "show_creatures",
            "show_spawns",
            "show_special",
            "show_houses",
            "show_pathing",
            "show_towns",
            "show_waypoints",
        ):
            self._add_show_action(menu, key)
        menu.addSeparator()
        for key in ("highlight_items", "highlight_locked_doors", "show_wall_hooks"):
            self._add_show_action(menu, key)

    def _setup_navigate_menu(self) -> None:
        menu = self._menus["Navigate"]
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
        menu.addActions(
            [
                self.goto_previous_position_action,
                self.goto_position_action,
                self.jump_to_brush_action,
                self.jump_to_item_action,
            ]
        )
        menu.addSeparator()
        floor_menu = menu.addMenu("Floor")
        assert floor_menu is not None
        floor_group = QActionGroup(self)
        floor_group.setExclusive(True)
        self.navigate_floor_actions: list[QAction] = []
        for floor in range(16):
            action = self._action(f"Floor {floor}")
            action.setObjectName(f"action_floor_{floor}")
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, value=floor: self._select_floor(value)
                if checked
                else None
            )
            if floor == 7:
                action.setChecked(True)
            floor_group.addAction(action)
            floor_menu.addAction(action)
            self.navigate_floor_actions.append(action)

    def _setup_window_menu(self) -> None:
        menu = self._menus["Window"]
        self.window_minimap_action = self._action_from_spec(
            "window_minimap", lambda: self._toggle_widget_visibility(self.minimap_dock)
        )
        self.window_tool_options_action = self._action_from_spec(
            "window_tool_options",
            lambda: self._toggle_widget_visibility(self.tool_options_dock),
        )
        self.window_tile_properties_action = self._action_from_spec(
            "window_tile_properties",
            lambda: self._toggle_widget_visibility(self.properties_dock),
        )
        self.window_ingame_preview_action = self._action_from_spec(
            "window_ingame_preview",
            lambda: self._toggle_widget_visibility(self.ingame_preview_dock),
        )
        self.new_palette_action = self._action_from_spec(
            "new_palette", self._show_shared_palette_notice
        )
        menu.addActions(
            [
                self.window_minimap_action,
                self.window_tool_options_action,
                self.window_tile_properties_action,
                self.window_ingame_preview_action,
                self.new_palette_action,
            ]
        )

        palette_menu = menu.addMenu("Palette")
        assert palette_menu is not None
        for key, palette_name in (
            ("select_palette_terrain", "Terrain"),
            ("select_palette_doodad", "Doodads"),
            ("select_palette_item", "Item"),
            ("select_palette_collection", "Collection"),
            ("select_palette_house", "House"),
            ("select_palette_creature", "Creature"),
            ("select_palette_waypoint", "Waypoint"),
            ("select_palette_raw", "RAW"),
        ):
            action = self._action_from_spec(
                key,
                lambda _checked=False, value=palette_name: self._show_palette(value),
            )
            palette_menu.addAction(action)

        toolbars_menu = menu.addMenu("Toolbars")
        assert toolbars_menu is not None
        self.toolbar_window_actions: dict[str, QAction] = {}
        for key, attr in (
            ("view_toolbars_brushes", "drawing_toolbar"),
            ("view_toolbars_position", "floor_toolbar"),
            ("view_toolbars_sizes", "sizes_toolbar"),
            ("view_toolbars_standard", "standard_toolbar"),
        ):
            action = self._check_action_from_spec(
                key,
                True,
                lambda checked, value=attr: self._set_toolbar_visible(value, checked),
            )
            self.toolbar_window_actions[key] = action
            toolbars_menu.addAction(action)

    def _setup_tail_menus(self) -> None:
        experimental = self._menus.get("Experimental")
        if experimental is not None:
            experimental.addAction(
                self._action_from_spec(
                    "experimental_fog",
                    lambda: self._show_unavailable("Fog in light view"),
                )
            )

        scripts = self._menus["Scripts"]
        scripts.addAction(
            self._action_from_spec(
                "scripts_manager", lambda: self._show_unavailable("Script Manager")
            )
        )
        scripts.addSeparator()
        scripts.addAction(
            self._action_from_spec(
                "scripts_open_folder",
                lambda: self._show_unavailable("Open Scripts Folder"),
            )
        )
        scripts.addAction(
            self._action_from_spec(
                "scripts_reload", lambda: self._show_unavailable("Reload Scripts")
            )
        )
        scripts.addSeparator()

        about = self._menus["About"]
        about.addAction(
            self._action_from_spec(
                "about_extensions", lambda: self._show_unavailable("Extensions")
            )
        )
        about.addAction(
            self._action_from_spec(
                "about_goto_website", lambda: self._show_unavailable("Goto Website")
            )
        )
        about.addAction(
            self._action_from_spec("about", self._show_about)
        )

    def _setup_toolbars(self) -> None:
        """Create the main toolbars."""
        self.drawing_toolbar = QToolBar("Drawing Tools")
        self.drawing_toolbar.setObjectName("drawing_toolbar")
        self.drawing_toolbar.setMovable(True)
        self.drawing_toolbar.addAction(self.brush_mode_actions["selection"])
        self.drawing_toolbar.addAction(self.brush_mode_actions["drawing"])
        self.drawing_toolbar.addAction(self._action("Erase"))
        self.drawing_toolbar.addAction(self._action("Fill"))
        self.drawing_toolbar.addSeparator()
        self.drawing_toolbar.addAction(self._action("Move"))
        self.addToolBar(self.drawing_toolbar)

        self.sizes_toolbar = QToolBar("Sizes")
        self.sizes_toolbar.setObjectName("sizes_toolbar")
        self.sizes_toolbar.setMovable(True)
        self.sizes_toolbar.addAction(self._action("1"))
        self.sizes_toolbar.addAction(self._action("3"))
        self.sizes_toolbar.addAction(self._action("5"))
        self.addToolBar(self.sizes_toolbar)

        self.standard_toolbar = QToolBar("Standard")
        self.standard_toolbar.setObjectName("standard_toolbar")
        self.standard_toolbar.setMovable(True)
        self.standard_toolbar.addAction(self.file_new_action)
        self.standard_toolbar.addAction(self.file_open_action)
        self.standard_toolbar.addAction(self.file_save_action)
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
        self._view_tabs.currentChanged.connect(self._on_view_tab_changed)
        self.setCentralWidget(self._view_tabs)

    def _setup_docks(self) -> None:
        """Create dock widgets for palettes and tools."""
        self.brush_palette_dock = BrushPaletteDock(self)
        self.brush_palette_dock.item_selected.connect(self._handle_item_palette_selection)
        if hasattr(self.brush_palette_dock, "manage_houses_requested"):
            self.brush_palette_dock.manage_houses_requested.connect(
                self._show_house_manager
            )
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.brush_palette_dock,
        )

        self.tool_options_dock = _ToolOptionsDock(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tool_options_dock)

        self.minimap_dock = MinimapDock(self)
        self.minimap_dock.z_up_btn.clicked.connect(self._floor_up)
        self.minimap_dock.z_down_btn.clicked.connect(self._floor_down)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.minimap_dock)
        self.toggle_minimap_action = self.minimap_dock.toggleViewAction()

        self.properties_dock = PropertiesDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        self.ingame_preview_dock = GlassDockWidget("IN-GAME PREVIEW", self)
        self.ingame_preview_dock.setObjectName("ingame_preview_dock")
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(8, 8, 8, 8)
        preview_label = QLabel("Preview is not available yet.")
        preview_label.setFont(TYPOGRAPHY.ui_label())
        preview_label.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        preview_layout.addWidget(preview_label)
        self.ingame_preview_dock.set_inner_layout(preview_layout)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.ingame_preview_dock,
        )

        self.waypoints_dock = WaypointsDock(
            self,
            editor=self._editor_context.session.editor,
        )
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
        spec = PHASE1_ACTIONS.get(spec_key)
        if spec is None:
            action = QAction(spec_key.replace("_", " ").title(), self)
            action.setObjectName(f"action_{spec_key}")
        else:
            action = QAction(spec.text, self)
            action.setObjectName(f"action_{spec.action_id}")
            if spec.shortcut:
                action.setShortcut(spec.shortcut)
            if spec.status_tip:
                action.setStatusTip(spec.status_tip)
        if handler is not None:
            action.triggered.connect(handler)
        return action

    def _check_action_from_spec(
        self,
        spec_key: str,
        checked: bool,
        handler,
    ) -> QAction:
        action = self._action_from_spec(spec_key)
        action.setCheckable(True)
        was_blocked = action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(was_blocked)
        action.toggled.connect(handler)
        return action

    def _restore_bool(self, key: str, default: bool) -> bool:
        return self._coerce_bool(self._settings.value(key, default), default)

    def _new_map(self) -> None:
        self._replace_editor_context(EditorContext())
        self._refresh_dirty_chrome()
        self._status_bar().showMessage("Created new map.", 3000)

    def _open_map(self) -> None:
        path = self._file_lifecycle_service.choose_open_map_path(self)
        if path is None:
            return
        self._open_map_file(path)

    def _save_map(self) -> bool:
        path = self._editor_context.session.document.path
        if path is None:
            return self._save_map_as()
        return self._save_map_to_path(path)

    def _save_map_as(self) -> bool:
        path = self._file_lifecycle_service.choose_save_map_path(
            self,
            self._editor_context.session.document.path,
        )
        if path is None:
            return False
        return self._save_map_to_path(path)

    def _save_map_to_path(self, path: str) -> bool:
        try:
            saved = self._file_lifecycle_service.save_map(path, self._editor_context)
        except Exception:
            logger.exception("Failed to save map %s", path)
            saved = False
        if not saved:
            self._status_bar().showMessage("Save is not available yet.", 3000)
            return False
        self._set_current_document_path(path)
        self._editor_context.session.document.is_dirty = False
        self._add_recent_file(path)
        self._refresh_dirty_chrome()
        self._status_bar().showMessage(f"Saved map: {path}", 3000)
        return True

    def _close_map(self) -> bool:
        if not self._confirm_close_current_document():
            return False
        self._replace_editor_context(EditorContext())
        self._refresh_dirty_chrome()
        self._status_bar().showMessage("Closed map.", 3000)
        return True

    def _exit(self) -> None:
        if self._close_map():
            self.close()

    def _confirm_close_current_document(self) -> bool:
        document = self._editor_context.session.document
        if not document.is_dirty:
            return True
        decision = self._file_lifecycle_service.confirm_close_dirty_document(
            self,
            document.name,
        )
        if decision == "cancel":
            self._status_bar().showMessage("Close cancelled.", 3000)
            return False
        if decision == "save":
            return self._save_map()
        return True

    def _replace_editor_context(self, context: EditorContext) -> None:
        self._editor_context = context
        for index, view in enumerate(self._views):
            view.editor_context = context
            view.canvas.bind_editor_context(context)
            if hasattr(self, "_view_tabs"):
                self._view_tabs.setTabText(index, context.session.document.name)
        self._sync_canvas_shell_state()
        self._refresh_selection_action_state()

    def _set_current_document_path(self, path: str) -> None:
        document = self._editor_context.session.document
        document.path = path
        document.name = Path(path).name or "Untitled"

    def _recent_files(self) -> list[str]:
        raw = self._settings.value(QSETTINGS_RECENT_FILES, [])
        if isinstance(raw, str):
            values = [raw] if raw else []
        elif isinstance(raw, (list, tuple)):
            values = [str(value) for value in raw if str(value)]
        else:
            values = []
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        return deduped[:MAX_RECENT_FILES]

    def _add_recent_file(self, path: str) -> None:
        recents = [path, *(item for item in self._recent_files() if item != path)]
        self._settings.setValue(QSETTINGS_RECENT_FILES, recents[:MAX_RECENT_FILES])
        self._settings.sync()
        self._rebuild_recent_files_menu()

    def _rebuild_recent_files_menu(self) -> None:
        menu = getattr(self, "recent_files_menu", None)
        if menu is None:
            return
        menu.clear()
        for path in self._recent_files():
            action = self._action(path)
            action.triggered.connect(
                lambda _checked=False, value=path: self._open_map_file(value)
            )
            menu.addAction(action)

    def _import_map(self) -> None:
        self._run_file_data_action(self._file_data_service.import_map)

    def _import_monsters_npc(self) -> None:
        self._run_file_data_action(self._file_data_service.import_monsters_npc)

    def _export_minimap(self) -> None:
        self._run_file_data_action(self._file_data_service.export_minimap)

    def _export_tilesets(self) -> None:
        self._run_file_data_action(self._file_data_service.export_tilesets)

    def _reload_data_files(self) -> None:
        self._run_file_data_action(self._file_data_service.reload_data_files)

    def _missing_items_report(self) -> None:
        self._run_file_data_action(self._file_data_service.missing_items_report)

    def _run_file_data_action(
        self,
        operation: Callable[[QWidget, EditorContext], FileDataActionResult],
    ) -> None:
        try:
            result = operation(self, self._editor_context)
        except Exception:
            logger.exception("File data action failed")
            result = FileDataActionResult.failure(
                "File data action failed: backend raised an exception.",
            )
        self._status_bar().showMessage(result.message, 3000)

    def _show_unavailable(self, label: str) -> None:
        self._status_bar().showMessage(f"{label} is not available yet.", 3000)

    def _toggle_widget_visibility(self, widget: QWidget | None) -> None:
        if widget is None:
            return
        widget.setVisible(widget.isHidden())

    def _set_toolbar_visible(self, attr: str, visible: bool) -> None:
        toolbar = getattr(self, attr, None)
        if toolbar is not None:
            toolbar.setVisible(visible)

    def _show_shared_palette_notice(self) -> None:
        if self.brush_palette_dock is not None:
            self.brush_palette_dock.show()
        self._status_bar().showMessage(
            "New Palette reuses the shared palette dock in this slice.",
            3000,
        )

    def _search_gap_action(self, spec_key: str, label: str) -> QAction:
        return self._action_from_spec(
            spec_key,
            lambda _checked=False, value=label: self._show_unavailable(value),
        )

    def _toggle_border_automagic(self, checked: bool) -> None:
        self._settings.setValue(QSETTINGS_BORDER_AUTOMAGIC, checked)
        self._status_bar().showMessage(
            f"Automagic {'enabled' if checked else 'disabled'}.",
            3000,
        )

    def _persist_selection_mode(self, _checked: bool = False) -> None:
        if not hasattr(self, "selection_menu_actions"):
            return
        self._settings.setValue(
            QSETTINGS_SELECTION_COMPENSATE,
            self.selection_menu_actions["select_mode_compensate"].isChecked(),
        )
        for key, value in (
            ("select_mode_current", "current"),
            ("select_mode_lower", "lower"),
            ("select_mode_visible", "visible"),
        ):
            if self.selection_menu_actions[key].isChecked():
                self._settings.setValue(QSETTINGS_SELECTION_MODE, value)
                break

    def _add_view_action(self, menu: QMenu, key: str) -> None:
        def _view_flag_handler(checked: bool, *, flag_name: str) -> None:
            self._set_view_flag(flag_name, checked)

        if key == "show_grid":
            handler = self._toggle_show_grid
        elif key == "ghost_higher_floors":
            handler = self._stub_ghost_higher
        else:
            handler = partial(_view_flag_handler, flag_name=key)
        action = self._check_action_from_spec(
            key,
            LEGACY_VIEW_FLAG_DEFAULTS[key],
            handler,
        )
        self.view_menu_actions[key] = action
        menu.addAction(action)

    def _add_show_action(self, menu: QMenu, key: str) -> None:
        action = self._check_action_from_spec(
            key,
            LEGACY_SHOW_FLAG_DEFAULTS[key],
            lambda checked, value=key: self._set_show_flag(value, checked),
        )
        self.show_menu_actions[key] = action
        menu.addAction(action)

    def _canvas_view_flag_name(self, name: str) -> str:
        return {
            "view_show_all_floors": "show_all_floors",
            "view_show_as_minimap": "show_as_minimap",
            "view_only_show_colors": "only_show_colors",
            "view_only_show_modified": "only_show_modified",
            "view_always_show_zones": "always_show_zones",
            "view_extended_house_shader": "extended_house_shader",
            "view_show_tooltips": "show_tooltips",
            "view_show_client_box": "show_client_box",
            "view_ghost_loose_items": "ghost_loose_items",
            "view_show_shade": "show_shade",
        }.get(name, name)

    def _canvas_show_flag_name(self, name: str) -> str:
        return {
            "show_animation": "show_preview",
            "show_light": "show_lights",
            "show_light_strength": "show_light_strength",
            "show_technical_items": "show_technical_items",
            "show_invalid_tiles": "show_invalid_tiles",
            "show_invalid_zones": "show_invalid_zones",
            "show_creatures": "show_creatures",
            "show_spawns": "show_spawns",
            "show_special": "show_special",
            "show_houses": "show_houses",
            "show_pathing": "show_pathing",
            "show_towns": "show_towns",
            "show_waypoints": "show_waypoints",
            "highlight_items": "highlight_items",
            "highlight_locked_doors": "highlight_locked_doors",
            "show_wall_hooks": "show_wall_hooks",
        }.get(name, name)

    def _sync_checkable_action(self, action: QAction, checked: bool) -> None:
        was_blocked = action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(was_blocked)

    def _show_map_properties(self) -> None:
        dialog = self._map_properties_dialog_factory(self)
        dialog.exec()

    def _show_town_manager(self) -> None:
        dialog = TownManagerDialog(self)
        dialog.exec()

    def _show_house_manager(self) -> None:
        dialog = self._house_manager_dialog_factory(self)
        dialog.exec()

    def _show_find_item(self) -> None:
        dialog = self._find_item_dialog_factory(self)
        if dialog.exec() == int(QDialog.DialogCode.Accepted):
            if self._apply_item_dialog_selection(dialog):
                return
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
        selected = (
            dialog.selected_result() if hasattr(dialog, "selected_result") else None
        )
        if selected is None:
            return False

        item_id = getattr(selected, "server_id", None)
        if item_id is None:
            item_id = getattr(selected, "item_id", None)

        if item_id is None:
            raise ValueError(
                f"Dialog selection {selected!r} has no server_id or item_id"
            )

        try:
            item_id = int(item_id)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid item_id {item_id!r}") from exc

        self._set_active_item_selection(selected.name, item_id)
        self._status_bar().showMessage(
            f"Selected item {selected.name} (#{item_id}).",
            3000,
        )
        return True

    def _replace_items(self) -> None:
        item_pair = self._edit_transform_service.choose_replace_items(
            self,
            self._editor_context,
        )
        if item_pair is None:
            self._status_bar().showMessage(
                "Replace Items deferred: no item selection dialog is mounted.",
                3000,
            )
            return
        if not self._edit_transform_service.confirm_map_transform(self, "Replace Items"):
            self._status_bar().showMessage("Replace Items canceled.", 3000)
            return
        old_item_id, new_item_id = item_pair
        count = self._editor_context.session.editor.replace_item_id(
            old_item_id,
            new_item_id,
        )
        self._refresh_edit_action_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage(
            f"Replaced {count} item {self._occurrence_label(count)}.",
            3000,
        )

    def _remove_items_by_id(self) -> None:
        item_id = self._edit_transform_service.choose_remove_items_by_id(
            self,
            self._editor_context,
        )
        if item_id is None:
            self._status_bar().showMessage(
                "Remove Items by ID deferred: no item ID selection dialog is mounted.",
                3000,
            )
            return
        if not self._edit_transform_service.confirm_map_transform(
            self,
            "Remove Items by ID",
        ):
            self._status_bar().showMessage("Remove Items by ID canceled.", 3000)
            return
        count = self._editor_context.session.editor.remove_item_id(item_id)
        self._refresh_edit_action_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage(
            f"Removed {count} item {self._occurrence_label(count)}.",
            3000,
        )

    def _clear_modified_state(self) -> None:
        self._editor_context.session.editor.clear_modified_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage("Cleared modified state.", 3000)

    def _defer_edit_transform(self, label: str) -> None:
        message = {
            "Borderize Selection": (
                "Borderize Selection deferred: rme_core AutoborderPlan has no "
                "Python map mutation bridge."
            ),
            "Borderize Map": (
                "Borderize Map deferred: rme_core AutoborderPlan has no Python "
                "map mutation bridge."
            ),
            "Randomize Selection": (
                "Randomize Selection deferred: TileState has no ground variant catalog."
            ),
            "Randomize Map": (
                "Randomize Map deferred: TileState has no ground variant catalog."
            ),
            "Remove all Corpses": (
                "Remove all Corpses deferred: TileState has no item type flags."
            ),
            "Remove all Unreachable Tiles": (
                "Remove all Unreachable Tiles deferred: no pathing or visibility graph "
                "exists."
            ),
            "Clear Invalid Houses": (
                "Clear Invalid Houses deferred: tiles do not store house IDs."
            ),
        }[label]
        self._status_bar().showMessage(message, 3000)

    @staticmethod
    def _occurrence_label(count: int) -> str:
        return "occurrence" if count == 1 else "occurrences"

    def _undo_edit(self) -> None:
        editor = self._editor_context.session.editor
        if not editor.undo():
            self._status_bar().showMessage("Undo is not available yet.", 3000)
            return
        self._refresh_edit_action_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage("Undid last edit.", 3000)

    def _redo_edit(self) -> None:
        editor = self._editor_context.session.editor
        if not editor.redo():
            self._status_bar().showMessage("Redo is not available yet.", 3000)
            return
        self._refresh_edit_action_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage("Redid last edit.", 3000)

    def _copy_selection(self) -> None:
        editor = self._editor_context.session.editor
        if not editor.copy_selection():
            self._status_bar().showMessage("Copy is not available yet.", 3000)
            return
        self._refresh_edit_action_state()
        self._status_bar().showMessage(
            f"Copied {editor.clipboard_tile_count()} tile.",
            3000,
        )

    def _cut_selection(self) -> None:
        editor = self._editor_context.session.editor
        if not editor.cut_selection():
            self._status_bar().showMessage("Cut is not available yet.", 3000)
            return
        self._refresh_selection_action_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage(
            f"Cut {editor.clipboard_tile_count()} tile.",
            3000,
        )

    def _paste_clipboard(self) -> None:
        editor = self._editor_context.session.editor
        position = MapPosition(self._current_x, self._current_y, self._current_z)
        if not editor.paste_clipboard_at(position):
            self._status_bar().showMessage("Paste is not available yet.", 3000)
            return
        self._refresh_edit_action_state()
        self._refresh_dirty_chrome()
        self._status_bar().showMessage(
            f"Pasted {editor.clipboard_tile_count()} tile.",
            3000,
        )

    def _show_preferences(self) -> None:
        dialog = PreferencesDialog(self)
        dialog.exec()

    def _show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_map_statistics(self) -> None:
        dialog = MapStatisticsDialog(self)
        dialog.exec()

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

    def _zoom_out(self) -> None:
        self._zoom_percent = max(10, self._zoom_percent - 10)
        if self._views:
            self._active_view().viewport.set_zoom_percent(self._zoom_percent)
        self._zoom_label.setText(f"{self._zoom_percent}%")
        self._sync_canvas_shell_state()

    def _zoom_normal(self) -> None:
        self._zoom_percent = 100
        if self._views:
            self._active_view().viewport.set_zoom_percent(self._zoom_percent)
        self._zoom_label.setText("100%")
        self._sync_canvas_shell_state()

    def _take_screenshot(self) -> None:
        self._status_bar().showMessage("Take Screenshot is not available yet.", 3000)

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _new_view(self) -> None:
        raw_canvas = self._canvas_factory(self)
        if not implements_canvas_widget_protocol(raw_canvas):
            raise TypeError("canvas_factory must return a CanvasWidgetProtocol widget")
        raw_canvas.bind_editor_context(self._editor_context)
        if implements_editor_tool_callback_canvas_protocol(raw_canvas):
            raw_canvas.set_tool_applied_callback(self._handle_tool_applied)

        active = self._active_view()
        view = EditorViewRecord(
            canvas=cast("CanvasWidgetProtocol", raw_canvas),
            editor_context=self._editor_context,
            shell_state=ShellStateSnapshot(
                show_grid_enabled=self._show_grid_enabled,
                ghost_higher_enabled=self._ghost_higher_enabled,
                show_lower_enabled=self._show_lower_enabled,
                view_flags=dict(active.shell_state.view_flags),
                show_flags=dict(active.shell_state.show_flags),
            ),
        )
        view.viewport.restore(active.viewport.snapshot())
        view.minimap_viewport.center_x = view.viewport.center_x
        view.minimap_viewport.center_y = view.viewport.center_y
        view.minimap_viewport.floor = view.viewport.floor
        view.minimap_viewport.zoom_percent = view.viewport.zoom_percent
        self._views.append(view)
        self._view_tabs.addTab(cast("QWidget", raw_canvas), "Untitled")
        self._view_tabs.setCurrentIndex(self._view_tabs.count() - 1)
        self._canvas = cast("CanvasWidgetProtocol", raw_canvas)
        self._sync_canvas_shell_state()
        self._status_bar().showMessage("Opened a new view.", 3000)

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
        if self._views:
            self._active_view().shell_state.view_flags["ghost_higher_floors"] = checked

    def _stub_show_lower(self, checked: bool) -> None:
        self._show_lower_enabled = checked
        self._canvas.set_show_lower(checked)

    def _active_view(self) -> EditorViewRecord:
        return self._views[self._view_tabs.currentIndex()]

    def _on_view_tab_changed(self, index: int) -> None:
        if not 0 <= index < len(self._views):
            return
        view = self._views[index]
        self._canvas = view.canvas
        self._current_x = view.viewport.center_x
        self._current_y = view.viewport.center_y
        self._current_z = view.viewport.floor
        self._previous_position = view.viewport.previous_position
        self._zoom_percent = view.viewport.zoom_percent
        self._show_grid_enabled = view.shell_state.show_grid_enabled
        self._ghost_higher_enabled = view.shell_state.ghost_higher_enabled
        self._show_lower_enabled = view.shell_state.show_lower_enabled
        self._coord_label.setText(
            f"Pos: (X: {self._current_x}, Y: {self._current_y}, Z: {self._current_z:02d})"
        )
        self._zoom_label.setText(f"{self._zoom_percent}%")
        self._items_label.setText(
            f"Floor {self._current_z} ({self._describe_floor(self._current_z)})"
        )
        for key, checked in view.shell_state.view_flags.items():
            action = self.view_menu_actions.get(key)
            if action is not None:
                self._sync_checkable_action(action, checked)
        for key, checked in view.shell_state.show_flags.items():
            action = self.show_menu_actions.get(key)
            if action is not None:
                self._sync_checkable_action(action, checked)
        self._sync_canvas_shell_state()

    def _set_view_flag(self, name: str, enabled: bool) -> None:
        view = self._active_view()
        view.shell_state.view_flags[name] = enabled
        if name == "view_show_all_floors":
            self._sync_selection_floor_mode_enablement(enabled)
        if implements_editor_view_flag_canvas_protocol(self._canvas):
            self._canvas.set_view_flag(self._canvas_view_flag_name(name), enabled)

    def _set_show_flag(self, name: str, enabled: bool) -> None:
        view = self._active_view()
        view.shell_state.show_flags[name] = enabled
        if implements_editor_show_flag_canvas_protocol(self._canvas):
            self._canvas.set_show_flag(self._canvas_show_flag_name(name), enabled)

    def _sync_selection_floor_mode_enablement(self, show_all_floors: bool) -> None:
        if not hasattr(self, "selection_menu_actions"):
            return
        lower = self.selection_menu_actions["select_mode_lower"]
        visible = self.selection_menu_actions["select_mode_visible"]
        lower.setEnabled(show_all_floors)
        visible.setEnabled(show_all_floors)
        if not show_all_floors:
            self.selection_menu_actions["select_mode_current"].setChecked(True)
            self._persist_selection_mode()

    def _set_editor_mode(self, mode: str) -> None:
        self._editor_context.session.mode = self._normalized_editor_mode(mode)
        if implements_editor_activation_canvas_protocol(self._canvas):
            self._canvas.set_editor_mode(self._editor_context.session.mode)
        label = self._mode_label_for(self._editor_context.session.mode)
        if self.tool_options_dock is not None:
            self.tool_options_dock.set_mode_label(label)
        self._status_bar().showMessage(f"Editor mode: {label}.", 3000)

    def _normalized_editor_mode(self, mode: str) -> str:
        return (
            mode
            if mode in {"selection", "drawing", "erasing", "fill", "move"}
            else "drawing"
        )

    def _mode_label_for(self, mode: str) -> str:
        return {
            "selection": "Select",
            "drawing": "Draw",
            "erasing": "Erase",
            "fill": "Fill",
            "move": "Move",
        }.get(mode, "Draw")

    def _handle_item_palette_selection(self, item: ItemEntry) -> None:
        self._set_active_item_selection(item.name, item.item_id)
        self._status_bar().showMessage(
            f"Selected item {item.name} (#{item.item_id}).",
            3000,
        )

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
        for key in (
            "replace_on_selection_items",
            "search_on_selection_item",
            "remove_on_selection_item",
            "search_on_selection_everything",
            "search_on_selection_unique",
            "search_on_selection_action",
            "search_on_selection_container",
            "search_on_selection_writeable",
        ):
            self.selection_menu_actions[key].setEnabled(enabled)
        self.edit_menu_actions["borderize_selection"].setEnabled(enabled)
        self.edit_menu_actions["randomize_selection"].setEnabled(enabled)
        self._refresh_edit_action_state()

    def _refresh_selection_action_state(self) -> None:
        self._refresh_selection_actions()

    def _refresh_edit_action_state(self) -> None:
        if not hasattr(self, "edit_menu_actions"):
            return
        editor = self._editor_context.session.editor
        self.edit_undo_action.setEnabled(editor.can_undo())
        self.edit_redo_action.setEnabled(editor.can_redo())
        self.edit_cut_action.setEnabled(editor.has_selection())
        self.edit_copy_action.setEnabled(editor.has_selection())
        self.edit_paste_action.setEnabled(editor.has_clipboard())

    def _refresh_dirty_chrome(self) -> None:
        document = self._editor_context.session.document
        label = f"{document.name}*" if document.is_dirty else document.name
        for index in range(self._view_tabs.count()):
            if self._view_tabs.tabText(index) != label:
                self._view_tabs.setTabText(index, label)
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
        if self._views and implements_editor_view_flag_canvas_protocol(self._canvas):
            for name, enabled in self._active_view().shell_state.view_flags.items():
                self._canvas.set_view_flag(self._canvas_view_flag_name(name), enabled)
        if self._views and implements_editor_show_flag_canvas_protocol(self._canvas):
            for name, enabled in self._active_view().shell_state.show_flags.items():
                self._canvas.set_show_flag(self._canvas_show_flag_name(name), enabled)
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
        if hasattr(self, "brush_mode_actions") and mode in self.brush_mode_actions:
            self._sync_checkable_action(self.brush_mode_actions[mode], True)

    def _sync_floor_actions(self, floor: int) -> None:
        floor = max(0, min(15, floor))
        for index, action in enumerate(self.floor_actions):
            self._sync_checkable_action(action, index == floor)
        if hasattr(self, "navigate_floor_actions"):
            for index, action in enumerate(self.navigate_floor_actions):
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
        if not self._confirm_close_current_document():
            if event is not None:
                event.ignore()
            return
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
