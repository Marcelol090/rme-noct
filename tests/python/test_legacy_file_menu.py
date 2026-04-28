from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

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

    window.file_new_action.trigger()
    assert _status_message(window) == "New is not available yet."

    window.file_import_map_action.trigger()
    assert _status_message(window) == "Import Map is not available yet."

    window.file_reload_data_action.trigger()
    assert _status_message(window) == "Reload Data Files is not available yet."

    window.file_exit_action.trigger()
    assert _status_message(window) == "Exit is not available yet."
