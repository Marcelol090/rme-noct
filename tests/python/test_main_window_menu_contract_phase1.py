from __future__ import annotations

from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS
from pyrme.ui.main_window import MainWindow


def test_main_window_exposes_legacy_top_level_menu_tree(qtbot) -> None:
    window = MainWindow(enable_docks=False)
    qtbot.addWidget(window)

    menu_bar = window.menuBar()
    assert menu_bar is not None
    top_level_titles = tuple(action.text() for action in menu_bar.actions())

    assert top_level_titles == LEGACY_TOP_LEVEL_MENUS


def test_main_window_exposes_phase1_legacy_actions(qtbot) -> None:
    window = MainWindow(enable_docks=False)
    qtbot.addWidget(window)

    edit_menu = next(
        action.menu() for action in window.menuBar().actions() if action.text() == "Edit"
    )
    search_menu = next(
        action.menu()
        for action in window.menuBar().actions()
        if action.text() == "Search"
    )
    navigate_menu = next(
        action.menu() for action in window.menuBar().actions() if action.text() == "Navigate"
    )
    view_menu = next(
        action.menu() for action in window.menuBar().actions() if action.text() == "View"
    )

    assert edit_menu is not None
    assert search_menu is not None
    assert navigate_menu is not None
    assert view_menu is not None

    edit_actions = {action.text() for action in edit_menu.actions() if action.text()}
    search_actions = {action.text() for action in search_menu.actions() if action.text()}
    navigate_actions = {action.text() for action in navigate_menu.actions() if action.text()}
    view_actions = {action.text() for action in view_menu.actions() if action.text()}

    assert "Replace Items..." in edit_actions
    assert "Find Item..." in search_actions
    assert "Go to Position..." in navigate_actions
    assert "Go to Previous Position" in navigate_actions
    assert "Jump to Brush..." in navigate_actions
    assert "Jump to Item..." in navigate_actions
    assert "Show grid" in view_actions
    assert "Ghost higher floors" in view_actions
