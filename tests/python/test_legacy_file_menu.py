from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.core_bridge import EditorShellCoreBridge
from pyrme.ui.editor_context import EditorContext
from pyrme.ui.legacy_menu_contract import (
    LEGACY_FILE_EXPORT_ITEMS,
    LEGACY_FILE_IMPORT_ITEMS,
    LEGACY_FILE_MENU_SEQUENCE,
    LEGACY_FILE_RELOAD_ITEMS,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


class _FakeFileLifecycleService:
    def __init__(self) -> None:
        self.open_paths: list[str | None] = []
        self.save_paths: list[str | None] = []
        self.close_decisions: list[str] = []
        self.load_calls: list[str] = []
        self.save_calls: list[str] = []
        self.save_path_requests: list[str | None] = []
        self.close_prompts: list[str] = []
        self.load_context_calls: list[tuple[str, EditorContext]] = []
        self.save_context_calls: list[tuple[str, EditorContext]] = []
        self.load_result: EditorContext | None = None
        self.load_error: Exception | None = None
        self.save_error: Exception | None = None
        self.load_ok = True
        self.save_ok = True

    def choose_open_map_path(self, parent) -> str | None:
        del parent
        return self.open_paths.pop(0) if self.open_paths else None

    def choose_save_map_path(self, parent, current_path: str | None = None) -> str | None:
        del parent
        self.save_path_requests.append(current_path)
        return self.save_paths.pop(0) if self.save_paths else None

    def confirm_close_dirty_document(self, parent, document_name: str) -> str:
        del parent
        self.close_prompts.append(document_name)
        return self.close_decisions.pop(0) if self.close_decisions else "discard"

    def load_map(self, path: str, current_context: EditorContext) -> EditorContext | None:
        self.load_calls.append(path)
        self.load_context_calls.append((path, current_context))
        if self.load_error is not None:
            raise self.load_error
        if not self.load_ok:
            return None
        return self.load_result or current_context

    def save_map(self, path: str, current_context: EditorContext) -> bool:
        self.save_calls.append(path)
        self.save_context_calls.append((path, current_context))
        if self.save_error is not None:
            raise self.save_error
        return self.save_ok


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _file_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "File")
    assert menu is not None
    return menu


def _submenu(menu: QMenu, name: str) -> QMenu:
    submenu = next(action.menu() for action in menu.actions() if action.text() == name)
    assert submenu is not None
    return submenu


def _menu_sequence(menu: QMenu) -> tuple[str | None, ...]:
    return tuple(None if action.isSeparator() else action.text() for action in menu.actions())


def _status_message(window: MainWindow) -> str:
    status_bar = window.statusBar()
    assert status_bar is not None
    return status_bar.currentMessage()


def test_legacy_file_contract_matches_xml() -> None:
    assert LEGACY_FILE_MENU_SEQUENCE == (
        "New...",
        "Open...",
        "Save",
        "Save As...",
        "Generate Map",
        "Close",
        None,
        "Import",
        "Export",
        "Reload",
        "Missing Items Report...",
        None,
        "Recent Files",
        "Preferences",
        "Exit",
    )
    assert LEGACY_FILE_IMPORT_ITEMS == (
        "Import Map...",
        "Import Monsters/NPC...",
    )
    assert LEGACY_FILE_EXPORT_ITEMS == (
        "Export Minimap...",
        "Export Tilesets...",
    )
    assert LEGACY_FILE_RELOAD_ITEMS == ("Reload Data Files",)
    assert PHASE1_ACTIONS["file_new"].shortcut == "Ctrl+N"
    assert PHASE1_ACTIONS["file_open"].shortcut == "Ctrl+O"
    assert PHASE1_ACTIONS["file_save"].shortcut == "Ctrl+S"
    assert PHASE1_ACTIONS["file_save_as"].shortcut == "Ctrl+Alt+S"
    assert PHASE1_ACTIONS["file_close"].shortcut == "Ctrl+Q"
    assert PHASE1_ACTIONS["file_reload_data"].shortcut == "F5"
    assert PHASE1_ACTIONS["file_preferences"].status_tip == "Configure the map editor."


def test_main_window_file_menu_matches_legacy_order(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "file-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    file_menu = _file_menu(window)
    assert _menu_sequence(file_menu) == LEGACY_FILE_MENU_SEQUENCE
    assert _menu_sequence(_submenu(file_menu, "Import")) == LEGACY_FILE_IMPORT_ITEMS
    assert _menu_sequence(_submenu(file_menu, "Export")) == LEGACY_FILE_EXPORT_ITEMS
    assert _menu_sequence(_submenu(file_menu, "Reload")) == LEGACY_FILE_RELOAD_ITEMS
    assert _menu_sequence(_submenu(file_menu, "Recent Files")) == ()


def test_file_actions_are_safe_until_backend_exists(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "file-actions.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.file_import_map_action.trigger()
    assert _status_message(window) == "Import Map is not available yet."

    window.file_reload_data_action.trigger()
    assert _status_message(window) == "Reload Data Files is not available yet."

    window.file_missing_items_report_action.trigger()
    assert _status_message(window) == "Missing Items Report is not available yet."


def test_file_new_creates_fresh_clean_editor_context(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    window = MainWindow(
        settings=_build_settings(settings_workspace, "file-new.ini"),
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)
    original_context = window._editor_context
    window._editor_context.session.document.path = "/tmp/old.otbm"
    window._editor_context.session.document.is_dirty = True

    window.file_new_action.trigger()

    assert window._editor_context is not original_context
    assert window._editor_context.session.document.path is None
    assert window._editor_context.session.document.is_dirty is False
    assert window._views[0].editor_context is window._editor_context
    assert _status_message(window) == "Created new map."


def test_file_open_loads_selected_path_and_tracks_recent_file(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    service.open_paths.append("/tmp/alpha.otbm")
    settings = _build_settings(settings_workspace, "file-open.ini")
    window = MainWindow(
        settings=settings,
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)

    window.file_open_action.trigger()

    assert service.load_calls == ["/tmp/alpha.otbm"]
    assert service.load_context_calls == [("/tmp/alpha.otbm", window._editor_context)]
    assert window._editor_context.session.document.path == "/tmp/alpha.otbm"
    assert window._editor_context.session.document.name == "alpha.otbm"
    assert window._editor_context.session.document.is_dirty is False
    assert _menu_sequence(window.recent_files_menu) == ("/tmp/alpha.otbm",)
    assert settings.value("file/recent_files") == ["/tmp/alpha.otbm"]
    assert _status_message(window) == "Opened map: /tmp/alpha.otbm"


def test_file_open_replaces_active_context_with_loaded_context(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    loaded_context = EditorContext()
    loaded_context.session.document.name = "Loaded Service Map"
    loaded_context.session.document.is_dirty = True
    service.load_result = loaded_context
    service.open_paths.append("/tmp/loaded.otbm")
    window = MainWindow(
        settings=_build_settings(settings_workspace, "file-open-loaded-context.ini"),
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)
    original_context = window._editor_context

    window.file_open_action.trigger()

    assert service.load_context_calls == [("/tmp/loaded.otbm", original_context)]
    assert window._editor_context is loaded_context
    assert window._views[0].editor_context is loaded_context
    assert window._editor_context.session.document.path == "/tmp/loaded.otbm"
    assert window._editor_context.session.document.is_dirty is False


def test_file_save_uses_current_path_and_save_as_prompts_for_new_path(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    service.save_paths.append("/tmp/beta.otbm")
    settings = _build_settings(settings_workspace, "file-save.ini")
    window = MainWindow(
        settings=settings,
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)
    window._editor_context.session.document.path = "/tmp/alpha.otbm"
    window._editor_context.session.document.is_dirty = True

    window.file_save_action.trigger()

    assert service.save_calls == ["/tmp/alpha.otbm"]
    assert service.save_context_calls == [("/tmp/alpha.otbm", window._editor_context)]
    assert window._editor_context.session.document.path == "/tmp/alpha.otbm"
    assert window._editor_context.session.document.is_dirty is False
    assert _status_message(window) == "Saved map: /tmp/alpha.otbm"

    window._editor_context.session.document.is_dirty = True
    window.file_save_as_action.trigger()

    assert service.save_path_requests == ["/tmp/alpha.otbm"]
    assert service.save_calls == ["/tmp/alpha.otbm", "/tmp/beta.otbm"]
    assert service.save_context_calls[-1] == ("/tmp/beta.otbm", window._editor_context)
    assert window._editor_context.session.document.path == "/tmp/beta.otbm"
    assert window._editor_context.session.document.name == "beta.otbm"
    assert window._editor_context.session.document.is_dirty is False
    assert settings.value("file/recent_files") == ["/tmp/beta.otbm", "/tmp/alpha.otbm"]


def test_file_open_failure_or_exception_preserves_document_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    service.load_ok = False
    service.open_paths.extend(["/tmp/fail.otbm", "/tmp/raise.otbm"])
    settings = _build_settings(settings_workspace, "file-open-failure.ini")
    window = MainWindow(
        settings=settings,
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)
    window._editor_context.session.document.path = "/tmp/current.otbm"
    window._editor_context.session.document.name = "current.otbm"
    window._editor_context.session.document.is_dirty = True

    window.file_open_action.trigger()

    assert window._editor_context.session.document.path == "/tmp/current.otbm"
    assert window._editor_context.session.document.is_dirty is True
    assert settings.value("file/recent_files", []) == []
    assert _menu_sequence(window.recent_files_menu) == ()
    assert _status_message(window) == "Open is not available yet."

    service.load_ok = True
    service.load_error = RuntimeError("native load failed")
    window.file_open_action.trigger()

    assert window._editor_context.session.document.path == "/tmp/current.otbm"
    assert window._editor_context.session.document.is_dirty is True
    assert settings.value("file/recent_files", []) == []
    assert _menu_sequence(window.recent_files_menu) == ()
    assert _status_message(window) == "Open is not available yet."


def test_file_save_failure_or_exception_preserves_document_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    service.save_ok = False
    settings = _build_settings(settings_workspace, "file-save-failure.ini")
    window = MainWindow(
        settings=settings,
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)
    window._editor_context.session.document.path = "/tmp/current.otbm"
    window._editor_context.session.document.name = "current.otbm"
    window._editor_context.session.document.is_dirty = True

    window.file_save_action.trigger()

    assert service.save_context_calls == [("/tmp/current.otbm", window._editor_context)]
    assert window._editor_context.session.document.path == "/tmp/current.otbm"
    assert window._editor_context.session.document.is_dirty is True
    assert settings.value("file/recent_files", []) == []
    assert _menu_sequence(window.recent_files_menu) == ()
    assert _status_message(window) == "Save is not available yet."

    service.save_ok = True
    service.save_error = RuntimeError("native save failed")
    window.file_save_action.trigger()

    assert window._editor_context.session.document.path == "/tmp/current.otbm"
    assert window._editor_context.session.document.is_dirty is True
    assert settings.value("file/recent_files", []) == []
    assert _menu_sequence(window.recent_files_menu) == ()
    assert _status_message(window) == "Save is not available yet."


def test_file_close_and_exit_use_dirty_guard(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    service.close_decisions.extend(["cancel", "save", "cancel"])
    window = MainWindow(
        settings=_build_settings(settings_workspace, "file-close.ini"),
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)
    window._editor_context.session.document.path = "/tmp/dirty.otbm"
    window._editor_context.session.document.name = "dirty.otbm"
    window._editor_context.session.document.is_dirty = True

    window.file_close_action.trigger()

    assert service.close_prompts == ["dirty.otbm"]
    assert service.save_calls == []
    assert window._editor_context.session.document.path == "/tmp/dirty.otbm"
    assert window._editor_context.session.document.is_dirty is True
    assert _status_message(window) == "Close cancelled."

    window.file_close_action.trigger()

    assert service.save_calls == ["/tmp/dirty.otbm"]
    assert window._editor_context.session.document.path is None
    assert window._editor_context.session.document.is_dirty is False
    assert _status_message(window) == "Closed map."

    window._editor_context.session.document.path = "/tmp/exit-dirty.otbm"
    window._editor_context.session.document.name = "exit-dirty.otbm"
    window._editor_context.session.document.is_dirty = True
    window.file_exit_action.trigger()

    assert service.close_prompts[-1] == "exit-dirty.otbm"
    assert window._editor_context.session.document.path == "/tmp/exit-dirty.otbm"
    assert window._editor_context.session.document.is_dirty is True
    assert _status_message(window) == "Close cancelled."


def test_recent_files_menu_loads_from_settings_and_opens_selected_path(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _FakeFileLifecycleService()
    settings = _build_settings(settings_workspace, "file-recents.ini")
    settings.setValue("file/recent_files", ["/tmp/first.otbm", "/tmp/second.otbm"])
    window = MainWindow(
        settings=settings,
        enable_docks=False,
        file_lifecycle_service=service,
    )
    qtbot.addWidget(window)

    assert _menu_sequence(window.recent_files_menu) == (
        "/tmp/first.otbm",
        "/tmp/second.otbm",
    )

    window.recent_files_menu.actions()[1].trigger()

    assert service.load_calls == ["/tmp/second.otbm"]
    assert window._editor_context.session.document.path == "/tmp/second.otbm"
    assert _menu_sequence(window.recent_files_menu) == (
        "/tmp/second.otbm",
        "/tmp/first.otbm",
    )


def test_core_bridge_load_save_failures_return_false() -> None:
    class _FailingNative:
        def load_otbm(self, path: str) -> None:
            raise RuntimeError(f"load failed: {path}")

        def save_otbm(self, path: str) -> None:
            raise RuntimeError(f"save failed: {path}")

    bridge = EditorShellCoreBridge(_FailingNative(), native=True)

    assert bridge.load_otbm("/tmp/fail.otbm") is False
    assert bridge.save_otbm("/tmp/fail.otbm") is False
