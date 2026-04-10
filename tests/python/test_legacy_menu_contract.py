from __future__ import annotations

from pyrme.ui.legacy_menu_contract import (
    EDITOR_ACTION_ORDER,
    EDITOR_ACTIONS,
    EDITOR_ZOOM_ACTION_ORDER,
    EDITOR_ZOOM_MENU_TITLE,
    LEGACY_TOP_LEVEL_MENUS,
    PHASE1_ACTIONS,
)


def test_legacy_top_level_menu_order_matches_cpp_contract() -> None:
    assert LEGACY_TOP_LEVEL_MENUS == (
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
    )


def test_phase1_action_metadata_matches_legacy_shortcuts() -> None:
    assert PHASE1_ACTIONS["find_item"].action_id == "find_item"
    assert PHASE1_ACTIONS["replace_items"].action_id == "replace_items"
    assert PHASE1_ACTIONS["map_properties"].action_id == "map_properties"
    assert PHASE1_ACTIONS["map_statistics"].action_id == "map_statistics"
    assert PHASE1_ACTIONS["goto_position"].action_id == "goto_position"
    assert PHASE1_ACTIONS["goto_previous_position"].action_id == "goto_previous_position"
    assert PHASE1_ACTIONS["jump_to_brush"].action_id == "jump_to_brush"
    assert PHASE1_ACTIONS["jump_to_item"].action_id == "jump_to_item"
    assert PHASE1_ACTIONS["show_grid"].action_id == "show_grid"
    assert PHASE1_ACTIONS["ghost_higher_floors"].action_id == "ghost_higher_floors"

    assert PHASE1_ACTIONS["find_item"].shortcut == "Ctrl+F"
    assert PHASE1_ACTIONS["replace_items"].shortcut == "Ctrl+Shift+F"
    assert PHASE1_ACTIONS["map_properties"].shortcut == "Ctrl+P"
    assert PHASE1_ACTIONS["map_statistics"].shortcut == "F8"
    assert PHASE1_ACTIONS["goto_position"].shortcut == "Ctrl+G"
    assert PHASE1_ACTIONS["goto_previous_position"].shortcut == "P"
    assert PHASE1_ACTIONS["jump_to_brush"].shortcut == "J"
    assert PHASE1_ACTIONS["jump_to_item"].shortcut == "Ctrl+J"
    assert PHASE1_ACTIONS["show_grid"].shortcut == "Shift+G"
    assert PHASE1_ACTIONS["ghost_higher_floors"].shortcut == "Ctrl+L"


def test_phase1_action_metadata_matches_legacy_status_tips() -> None:
    assert PHASE1_ACTIONS["find_item"].text == "&Find Item..."
    assert PHASE1_ACTIONS["replace_items"].text == "&Replace Items..."
    assert PHASE1_ACTIONS["map_properties"].text == "Properties..."
    assert PHASE1_ACTIONS["map_statistics"].text == "Statistics"
    assert PHASE1_ACTIONS["goto_position"].text == "Go to Position..."
    assert PHASE1_ACTIONS["goto_previous_position"].text == "Go to Previous Position"
    assert PHASE1_ACTIONS["jump_to_brush"].text == "Jump to Brush..."
    assert PHASE1_ACTIONS["jump_to_item"].text == "Jump to Item..."
    assert PHASE1_ACTIONS["show_grid"].text == "Show grid"
    assert PHASE1_ACTIONS["ghost_higher_floors"].text == "Ghost higher floors"

    assert PHASE1_ACTIONS["find_item"].menu_path == ("Search",)
    assert PHASE1_ACTIONS["replace_items"].menu_path == ("Edit",)
    assert PHASE1_ACTIONS["map_properties"].menu_path == ("Map",)
    assert PHASE1_ACTIONS["map_statistics"].menu_path == ("Map",)
    assert PHASE1_ACTIONS["goto_position"].menu_path == ("Navigate",)
    assert PHASE1_ACTIONS["goto_previous_position"].menu_path == ("Navigate",)
    assert PHASE1_ACTIONS["jump_to_brush"].menu_path == ("Navigate",)
    assert PHASE1_ACTIONS["jump_to_item"].menu_path == ("Navigate",)
    assert PHASE1_ACTIONS["show_grid"].menu_path == ("View",)
    assert PHASE1_ACTIONS["ghost_higher_floors"].menu_path == ("View",)

    assert PHASE1_ACTIONS["find_item"].status_tip == "Find all instances of an item type the map."
    assert (
        PHASE1_ACTIONS["replace_items"].status_tip
        == "Replaces all occurrences of one item with another."
    )
    assert PHASE1_ACTIONS["map_properties"].status_tip == "Show and change the map properties."
    assert PHASE1_ACTIONS["map_statistics"].status_tip == "Show map statistics."
    assert PHASE1_ACTIONS["goto_position"].status_tip == "Go to a specific XYZ position."
    assert (
        PHASE1_ACTIONS["goto_previous_position"].status_tip
        == "Go to the previous screen center position."
    )
    assert PHASE1_ACTIONS["jump_to_brush"].status_tip == "Jump to a brush."
    assert PHASE1_ACTIONS["jump_to_item"].status_tip == "Jump to an item brush (RAW palette)."
    assert PHASE1_ACTIONS["show_grid"].status_tip == "Shows a grid over all items."
    assert PHASE1_ACTIONS["ghost_higher_floors"].status_tip == "Ghost floors."


def test_editor_action_contract_matches_legacy_metadata() -> None:
    assert EDITOR_ACTION_ORDER == (
        "new_view",
        "toggle_fullscreen",
        "take_screenshot",
    )
    assert EDITOR_ZOOM_MENU_TITLE == "Zoom"
    assert EDITOR_ZOOM_ACTION_ORDER == ("zoom_in", "zoom_out", "zoom_normal")

    assert EDITOR_ACTIONS["new_view"].action_id == "new_view"
    assert EDITOR_ACTIONS["toggle_fullscreen"].action_id == "toggle_fullscreen"
    assert EDITOR_ACTIONS["take_screenshot"].action_id == "take_screenshot"
    assert EDITOR_ACTIONS["zoom_in"].action_id == "zoom_in"
    assert EDITOR_ACTIONS["zoom_out"].action_id == "zoom_out"
    assert EDITOR_ACTIONS["zoom_normal"].action_id == "zoom_normal"

    assert EDITOR_ACTIONS["new_view"].text == "New View"
    assert EDITOR_ACTIONS["toggle_fullscreen"].text == "Enter Fullscreen"
    assert EDITOR_ACTIONS["take_screenshot"].text == "Take Screenshot"
    assert EDITOR_ACTIONS["zoom_in"].text == "Zoom In"
    assert EDITOR_ACTIONS["zoom_out"].text == "Zoom Out"
    assert EDITOR_ACTIONS["zoom_normal"].text == "Zoom Normal"

    assert EDITOR_ACTIONS["new_view"].menu_path == ("Editor",)
    assert EDITOR_ACTIONS["toggle_fullscreen"].menu_path == ("Editor",)
    assert EDITOR_ACTIONS["take_screenshot"].menu_path == ("Editor",)
    assert EDITOR_ACTIONS["zoom_in"].menu_path == ("Editor", "Zoom")
    assert EDITOR_ACTIONS["zoom_out"].menu_path == ("Editor", "Zoom")
    assert EDITOR_ACTIONS["zoom_normal"].menu_path == ("Editor", "Zoom")

    assert EDITOR_ACTIONS["new_view"].shortcut == "Ctrl+Shift+N"
    assert EDITOR_ACTIONS["toggle_fullscreen"].shortcut == "F11"
    assert EDITOR_ACTIONS["take_screenshot"].shortcut == "F10"
    assert EDITOR_ACTIONS["zoom_in"].shortcut == "Ctrl++"
    assert EDITOR_ACTIONS["zoom_out"].shortcut == "Ctrl+-"
    assert EDITOR_ACTIONS["zoom_normal"].shortcut == "Ctrl+0"

    assert EDITOR_ACTIONS["new_view"].status_tip == "Creates a new view of the current map."
    assert (
        EDITOR_ACTIONS["toggle_fullscreen"].status_tip
        == "Changes between fullscreen mode and windowed mode."
    )
    assert EDITOR_ACTIONS["take_screenshot"].status_tip == "Saves the current view to the disk."
    assert EDITOR_ACTIONS["zoom_in"].status_tip == "Increase the zoom."
    assert EDITOR_ACTIONS["zoom_out"].status_tip == "Decrease the zoom."
    assert EDITOR_ACTIONS["zoom_normal"].status_tip == "Normal zoom(100%)."
