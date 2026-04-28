from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

from pyrme.ui.dialogs.find_item import FindItemQuery, FindItemResult
from pyrme.ui.legacy_menu_contract import LEGACY_SEARCH_MENU_SEQUENCE, PHASE1_ACTIONS
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMenu


def _build_settings(root, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _search_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "Search")
    assert menu is not None
    return menu


def _menu_sequence(menu: QMenu) -> tuple[str | None, ...]:
    return tuple(None if action.isSeparator() else action.text() for action in menu.actions())


class _FindItemSelectDialog:
    def __init__(self, parent=None) -> None:
        self.parent = parent

    def exec(self) -> int:
        return int(QDialog.DialogCode.Accepted)

    def selected_result(self) -> FindItemResult:
        return FindItemResult(
            2148,
            2148,
            "Gold Coin",
            "sprite-2148",
            "item",
            {"pickupable", "stackable"},
        )

    def last_search_map_query(self) -> None:
        return None


class _FindItemSearchMapDialog:
    def __init__(self, parent=None) -> None:
        self.parent = parent

    def exec(self) -> int:
        return int(QDialog.DialogCode.Rejected)

    def selected_result(self) -> None:
        return None

    def last_search_map_query(self) -> FindItemQuery:
        return FindItemQuery(search_text="wall")


def test_legacy_search_contract_matches_xml() -> None:
    assert LEGACY_SEARCH_MENU_SEQUENCE == (
        "Find Item...",
        None,
        "Find Unique",
        "Find Action",
        "Find Container",
        "Find Writeable",
        None,
        "Find Everything",
    )
    assert PHASE1_ACTIONS["find_item"].shortcut == "Ctrl+F"
    assert PHASE1_ACTIONS["find_item"].status_tip == (
        "Find all instances of an item type the map."
    )
    assert PHASE1_ACTIONS["search_on_map_unique"].status_tip == (
        "Find all items with an unique ID on map."
    )
    assert PHASE1_ACTIONS["search_on_map_action"].status_tip == (
        "Find all items with an action ID on map."
    )
    assert PHASE1_ACTIONS["search_on_map_container"].status_tip == (
        "Find all containers on map."
    )
    assert PHASE1_ACTIONS["search_on_map_writeable"].status_tip == (
        "Find all writeable items on map."
    )
    assert PHASE1_ACTIONS["search_on_map_everything"].status_tip == (
        "Find all unique/action/text/container items."
    )


def test_main_window_search_menu_matches_legacy_order(qtbot, settings_workspace) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "search-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert _menu_sequence(_search_menu(window)) == LEGACY_SEARCH_MENU_SEQUENCE
    assert window.search_on_map_unique_action.objectName() == "action_search_on_map_unique"
    assert window.search_on_map_action_action.objectName() == "action_search_on_map_action"
    assert window.search_on_map_container_action.objectName() == (
        "action_search_on_map_container"
    )
    assert window.search_on_map_writeable_action.objectName() == (
        "action_search_on_map_writeable"
    )
    assert window.search_on_map_everything_action.objectName() == (
        "action_search_on_map_everything"
    )


def test_search_map_actions_are_safe_until_backend_exists(
    qtbot,
    settings_workspace,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "search-stubs.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    for action, expected in (
        (window.search_on_map_unique_action, "unique"),
        (window.search_on_map_action_action, "action"),
        (window.search_on_map_container_action, "container"),
        (window.search_on_map_writeable_action, "writeable"),
        (window.search_on_map_everything_action, "everything"),
    ):
        action.trigger()
        message = window.statusBar().currentMessage().lower()
        assert expected in message
        assert "not available" in message


def test_find_item_action_consumes_selected_result(qtbot, settings_workspace) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "find-item-select.ini"),
        enable_docks=False,
        find_item_dialog_factory=_FindItemSelectDialog,
    )
    qtbot.addWidget(window)

    window.find_item_action.trigger()

    assert "gold coin" in window.statusBar().currentMessage().lower()
    assert "#2148" in window.statusBar().currentMessage()


def test_find_item_action_reports_search_map_gap(qtbot, settings_workspace) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "find-item-search-map.ini"),
        enable_docks=False,
        find_item_dialog_factory=_FindItemSearchMapDialog,
    )
    qtbot.addWidget(window)

    window.find_item_action.trigger()

    message = window.statusBar().currentMessage().lower()
    assert "search on map" in message
    assert "wall" in message
    assert "not available" in message
