from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.editor.model import MapPosition
from pyrme.ui.legacy_menu_contract import (
    LEGACY_SELECTION_FIND_ITEMS,
    LEGACY_SELECTION_MENU_SEQUENCE,
    LEGACY_SELECTION_MODE_DEFAULTS,
    LEGACY_SELECTION_MODE_ITEMS,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _selection_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(
        action.menu() for action in menu_bar.actions() if action.text() == "Selection"
    )
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


def test_legacy_selection_contract_matches_xml_and_defaults() -> None:
    assert LEGACY_SELECTION_MENU_SEQUENCE == (
        "Replace Items on Selection",
        "Find Item on Selection",
        "Remove Item on Selection",
        None,
        "Find on Selection",
        None,
        "Selection Mode",
        None,
        "Borderize Selection",
        "Randomize Selection",
    )
    assert LEGACY_SELECTION_FIND_ITEMS == (
        "Find Everything",
        None,
        "Find Unique",
        "Find Action",
        "Find Container",
        "Find Writeable",
    )
    assert LEGACY_SELECTION_MODE_ITEMS == (
        "Compensate Selection",
        None,
        "Current Floor",
        "Lower Floors",
        "Visible Floors",
    )
    assert LEGACY_SELECTION_MODE_DEFAULTS == {
        "select_mode_compensate": True,
        "select_mode_current": True,
        "select_mode_lower": False,
        "select_mode_visible": False,
    }
    assert PHASE1_ACTIONS["replace_on_selection_items"].status_tip == (
        "Replace items on selected area."
    )
    assert PHASE1_ACTIONS["search_on_selection_item"].status_tip == (
        "Find items on selected area."
    )
    assert PHASE1_ACTIONS["remove_on_selection_item"].status_tip == (
        "Remove item on selected area."
    )


def test_main_window_selection_menu_matches_legacy_order_and_defaults(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    selection_menu = _selection_menu(window)
    assert _menu_sequence(selection_menu) == LEGACY_SELECTION_MENU_SEQUENCE
    assert _menu_sequence(_submenu(selection_menu, "Find on Selection")) == (
        LEGACY_SELECTION_FIND_ITEMS
    )
    assert _menu_sequence(_submenu(selection_menu, "Selection Mode")) == (
        LEGACY_SELECTION_MODE_ITEMS
    )

    for key, expected in LEGACY_SELECTION_MODE_DEFAULTS.items():
        action = window.selection_menu_actions[key]
        assert action.isCheckable()
        assert action.isChecked() is expected

    assert window.selection_menu_actions["select_mode_lower"].isEnabled() is True
    assert window.selection_menu_actions["select_mode_visible"].isEnabled() is True


def test_selection_actions_follow_selection_presence_and_safe_gaps(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-actions.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    disabled_keys = (
        "replace_on_selection_items",
        "search_on_selection_item",
        "remove_on_selection_item",
        "search_on_selection_everything",
        "search_on_selection_unique",
        "search_on_selection_action",
        "search_on_selection_container",
        "search_on_selection_writeable",
    )
    for key in disabled_keys:
        assert window.selection_menu_actions[key].isEnabled() is False

    assert window.edit_menu_actions["borderize_selection"].isEnabled() is False
    assert window.edit_menu_actions["randomize_selection"].isEnabled() is False

    window._editor_context.session.editor.select_position(MapPosition(32000, 32000, 7))
    window._refresh_selection_action_state()

    for key in disabled_keys:
        assert window.selection_menu_actions[key].isEnabled() is True

    assert window.edit_menu_actions["borderize_selection"].isEnabled() is True
    assert window.edit_menu_actions["randomize_selection"].isEnabled() is True

    window.selection_menu_actions["replace_on_selection_items"].trigger()
    assert _status_message(window) == "Replace Items on Selection is not available yet."


def test_selection_mode_enablement_tracks_show_all_floors(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-mode.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.selection_menu_actions["select_mode_lower"].setChecked(True)
    assert window.selection_menu_actions["select_mode_lower"].isChecked() is True

    window.view_menu_actions["view_show_all_floors"].setChecked(False)

    assert window.selection_menu_actions["select_mode_current"].isChecked() is True
    assert window.selection_menu_actions["select_mode_lower"].isEnabled() is False
    assert window.selection_menu_actions["select_mode_visible"].isEnabled() is False

    window.view_menu_actions["view_show_all_floors"].setChecked(True)

    assert window.selection_menu_actions["select_mode_lower"].isEnabled() is True
    assert window.selection_menu_actions["select_mode_visible"].isEnabled() is True


def test_selection_mode_persists_in_settings(qtbot, settings_workspace: Path) -> None:
    settings = _build_settings(settings_workspace, "selection-persist.ini")

    window = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.selection_menu_actions["select_mode_compensate"].setChecked(False)
    window.selection_menu_actions["select_mode_visible"].setChecked(True)

    replacement = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(replacement)

    assert replacement.selection_menu_actions["select_mode_compensate"].isChecked() is False
    assert replacement.selection_menu_actions["select_mode_visible"].isChecked() is True
