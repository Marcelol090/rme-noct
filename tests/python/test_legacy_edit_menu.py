from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.editor.model import MapPosition
from pyrme.ui.legacy_menu_contract import (
    LEGACY_EDIT_BORDER_ITEMS,
    LEGACY_EDIT_MENU_SEQUENCE,
    LEGACY_EDIT_OTHER_ITEMS,
    LEGACY_EDIT_STATE_DEFAULTS,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _edit_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "Edit")
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


def test_legacy_edit_contract_matches_xml_and_defaults() -> None:
    assert LEGACY_EDIT_MENU_SEQUENCE == (
        "Undo",
        "Redo",
        None,
        "Replace Items...",
        None,
        "Border Options",
        "Other Options",
        None,
        "Cut",
        "Copy",
        "Paste",
    )
    assert LEGACY_EDIT_BORDER_ITEMS == (
        "Border Automagic",
        None,
        "Borderize Selection",
        "Borderize Map",
        "Randomize Selection",
        "Randomize Map",
    )
    assert LEGACY_EDIT_OTHER_ITEMS == (
        "Remove Items by ID...",
        "Remove all Corpses...",
        "Remove all Unreachable Tiles...",
        "Clear Invalid Houses",
        "Clear Modified State",
    )
    assert LEGACY_EDIT_STATE_DEFAULTS == {"border_automagic": True}
    assert PHASE1_ACTIONS["edit_undo"].shortcut == "Ctrl+Z"
    assert PHASE1_ACTIONS["edit_redo"].shortcut == "Ctrl+Shift+Z"
    assert PHASE1_ACTIONS["border_automagic"].shortcut == "A"
    assert PHASE1_ACTIONS["borderize_selection"].shortcut == "Ctrl+B"
    assert PHASE1_ACTIONS["remove_items_by_id"].shortcut == "Ctrl+Shift+R"
    assert PHASE1_ACTIONS["edit_cut"].shortcut == "Ctrl+X"
    assert PHASE1_ACTIONS["edit_copy"].shortcut == "Ctrl+C"
    assert PHASE1_ACTIONS["edit_paste"].shortcut == "Ctrl+V"


def test_main_window_edit_menu_matches_legacy_order_and_defaults(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "edit-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    edit_menu = _edit_menu(window)
    assert _menu_sequence(edit_menu) == LEGACY_EDIT_MENU_SEQUENCE
    assert _menu_sequence(_submenu(edit_menu, "Border Options")) == LEGACY_EDIT_BORDER_ITEMS
    assert _menu_sequence(_submenu(edit_menu, "Other Options")) == LEGACY_EDIT_OTHER_ITEMS

    assert window.edit_menu_actions["border_automagic"].isCheckable()
    assert (
        window.edit_menu_actions["border_automagic"].isChecked()
        is LEGACY_EDIT_STATE_DEFAULTS["border_automagic"]
    )


def test_edit_actions_are_safe_until_backend_exists(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "edit-actions.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.edit_undo_action.trigger()
    assert _status_message(window) == "Undo is not available yet."

    window._editor_context.session.editor.select_position(MapPosition(32000, 32000, 7))
    window._refresh_selection_action_state()
    window.edit_menu_actions["borderize_selection"].trigger()
    assert _status_message(window) == "Borderize Selection is not available yet."

    window.edit_menu_actions["remove_all_corpses"].trigger()
    assert _status_message(window) == "Remove all Corpses is not available yet."

    window.edit_cut_action.trigger()
    assert _status_message(window) == "Cut is not available yet."

    window.edit_menu_actions["border_automagic"].setChecked(False)
    assert _status_message(window) == "Automagic disabled."


def test_border_automagic_persists_as_global_setting(
    qtbot,
    settings_workspace: Path,
) -> None:
    settings = _build_settings(settings_workspace, "edit-automagic.ini")

    window = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.edit_menu_actions["border_automagic"].setChecked(False)
    assert _status_message(window) == "Automagic disabled."

    replacement = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(replacement)

    assert replacement.edit_menu_actions["border_automagic"].isChecked() is False
