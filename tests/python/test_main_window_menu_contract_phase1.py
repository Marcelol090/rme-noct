from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMenu


def _menu_titles(window: MainWindow) -> list[str]:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    return [action.text().replace("&", "") for action in menu_bar.actions()]


def _menus_by_title(window: MainWindow) -> dict[str, QMenu]:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menus: dict[str, QMenu] = {}
    for action in menu_bar.actions():
        menu = action.menu()
        if menu is not None:
            menus[action.text().replace("&", "")] = menu
    return menus


def _menu_action_texts(menu: QMenu) -> list[str]:
    return [action.text() for action in menu.actions() if action.text()]


def test_main_window_exposes_legacy_top_level_menu_tree(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert _menu_titles(window) == list(LEGACY_TOP_LEVEL_MENUS)


def test_main_window_wires_phase1_actions_by_contract(qtbot, caplog) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    menus = _menus_by_title(window)
    assert set(menus) >= {"Edit", "Map", "Search", "View", "Navigate"}

    for spec_key, spec in PHASE1_ACTIONS.items():
        assert spec.menu_path, spec_key

        menu = menus[spec.menu_path[0]]
        action = next(action for action in menu.actions() if action.text() == spec.text)

        assert action.objectName() == f"action_{spec.action_id}"
        assert action.text() == spec.text
        assert action.shortcut().toString() == (spec.shortcut or "")
        assert action.statusTip() == (spec.status_tip or "")

    search_menu = menus["Search"]
    assert "&Find Item..." in _menu_action_texts(search_menu)

    edit_menu = menus["Edit"]
    assert "&Replace Items..." in _menu_action_texts(edit_menu)

    map_menu = menus["Map"]
    assert "Properties..." in _menu_action_texts(map_menu)
    assert "Statistics" in _menu_action_texts(map_menu)

    navigate_menu = menus["Navigate"]
    assert "Go to Previous Position" in _menu_action_texts(navigate_menu)
    assert "Go to Position..." in _menu_action_texts(navigate_menu)
    assert "Jump to Brush..." in _menu_action_texts(navigate_menu)
    assert "Jump to Item..." in _menu_action_texts(navigate_menu)

    view_menu = menus["View"]
    assert "Show grid" in _menu_action_texts(view_menu)
    assert "Ghost higher floors" in _menu_action_texts(view_menu)

    show_grid_action = next(
        action for action in view_menu.actions() if action.text() == "Show grid"
    )
    ghost_higher_action = next(
        action for action in view_menu.actions() if action.text() == "Ghost higher floors"
    )

    assert show_grid_action.isCheckable()
    assert ghost_higher_action.isCheckable()
    assert not ghost_higher_action.isChecked()

    with caplog.at_level(logging.WARNING, logger="pyrme.ui.main_window"):
        ghost_higher_action.trigger()

    assert ghost_higher_action.isChecked()
    assert any(
        record.levelno == logging.WARNING
        and (
            record.message
            == "Ghost Higher Floors ON: NotImplementedError — awaiting canvas backend"
        )
        for record in caplog.records
    )
