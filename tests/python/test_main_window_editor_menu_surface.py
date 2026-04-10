from __future__ import annotations

from pyrme.ui.legacy_menu_contract import (
    EDITOR_ACTION_ORDER,
    EDITOR_ACTIONS,
    EDITOR_ZOOM_ACTION_ORDER,
    EDITOR_ZOOM_MENU_TITLE,
)
from pyrme.ui.main_window import MainWindow


def _menus_by_title(window: MainWindow):
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menus = {}
    for action in menu_bar.actions():
        menu = action.menu()
        if menu is not None:
            menus[action.text().replace("&", "")] = menu
    return menus


def test_main_window_exposes_editor_menu_surface_from_contract(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    menus = _menus_by_title(window)
    editor_menu = menus["Editor"]

    top_level_items = [action.text() for action in editor_menu.actions() if action.text()]
    assert top_level_items[:3] == [
        EDITOR_ACTIONS[action_key].text for action_key in EDITOR_ACTION_ORDER
    ]

    zoom_menu_action = next(
        action for action in editor_menu.actions() if action.menu() is not None
    )
    assert zoom_menu_action.text() == EDITOR_ZOOM_MENU_TITLE
    zoom_menu = zoom_menu_action.menu()
    assert zoom_menu is not None
    assert [action.text() for action in zoom_menu.actions()] == [
        EDITOR_ACTIONS[action_key].text for action_key in EDITOR_ZOOM_ACTION_ORDER
    ]

    for action_key in (*EDITOR_ACTION_ORDER, *EDITOR_ZOOM_ACTION_ORDER):
        spec = EDITOR_ACTIONS[action_key]
        menu = editor_menu if len(spec.menu_path) == 1 else zoom_menu
        action = next(action for action in menu.actions() if action.text() == spec.text)
        assert action.objectName() == f"action_{spec.action_id}"
        assert action.shortcut().toString() == (spec.shortcut or "")
        assert action.statusTip() == (spec.status_tip or "")


def test_main_window_editor_actions_are_safe_stubs(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    status_bar = window.statusBar()
    assert status_bar is not None

    assert not window.isFullScreen()
    assert window._zoom_percent == 100
    assert not hasattr(window, "_child_views")
    assert not hasattr(window, "_last_screenshot")

    window.new_view_action.trigger()
    assert status_bar.currentMessage() == "New View is not available yet."
    assert not hasattr(window, "_child_views")

    window.take_screenshot_action.trigger()
    assert status_bar.currentMessage() == "Take Screenshot is not available yet."
    assert not hasattr(window, "_last_screenshot")

    window.toggle_fullscreen_action.trigger()
    assert not window.isFullScreen()
    assert status_bar.currentMessage() == "Enter Fullscreen is not available yet."

    window.zoom_in_action.trigger()
    assert window._zoom_percent == 100
    assert status_bar.currentMessage() == "Zoom In is not available yet."

    window.zoom_out_action.trigger()
    assert window._zoom_percent == 100
    assert status_bar.currentMessage() == "Zoom Out is not available yet."

    window.zoom_normal_action.trigger()
    assert window._zoom_percent == 100
    assert status_bar.currentMessage() == "Zoom Normal is not available yet."
