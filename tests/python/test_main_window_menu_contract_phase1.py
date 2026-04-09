from __future__ import annotations

from pyrme.ui.main_window import MainWindow


def _menu_titles(window: MainWindow) -> list[str]:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    return [action.text().replace("&", "") for action in menu_bar.actions()]


def test_main_window_exposes_legacy_top_level_menu_tree(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert _menu_titles(window) == [
        "File",
        "Edit",
        "Editor",
        "Search",
        "Map",
        "Selection",
        "View",
        "Show",
        "Navigate",
        "Window",
        "Experimental",
        "Scripts",
        "About",
    ]


def test_main_window_exposes_phase1_action_objects(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.find_item_action.objectName() == "action_find_item"
    assert window.replace_items_action.objectName() == "action_replace_items"
    assert window.map_properties_action.objectName() == "action_map_properties"
    assert window.map_statistics_action.objectName() == "action_map_statistics"
    assert window.goto_previous_position_action.objectName() == "action_goto_previous_position"
    assert window.goto_position_action.objectName() == "action_goto_position"
    assert window.jump_to_brush_action.objectName() == "action_jump_to_brush"
    assert window.jump_to_item_action.objectName() == "action_jump_to_item"
