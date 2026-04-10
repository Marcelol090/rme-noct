from __future__ import annotations

from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS


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
