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
    assert PHASE1_ACTIONS["find_item"].status_tip == "Find all instances of an item type the map."
    assert PHASE1_ACTIONS["replace_items"].status_tip == "Replaces all occurrences of one item with another."
    assert PHASE1_ACTIONS["map_properties"].status_tip == "Show and change the map properties."
    assert PHASE1_ACTIONS["map_statistics"].status_tip == "Show map statistics."
    assert PHASE1_ACTIONS["goto_position"].status_tip == "Go to a specific XYZ position."
    assert PHASE1_ACTIONS["goto_previous_position"].status_tip == "Go to the previous screen center position."
    assert PHASE1_ACTIONS["jump_to_brush"].status_tip == "Jump to a brush."
    assert PHASE1_ACTIONS["jump_to_item"].status_tip == "Jump to an item brush (RAW palette)."
    assert PHASE1_ACTIONS["show_grid"].status_tip == "Shows a grid over all items."
    assert PHASE1_ACTIONS["ghost_higher_floors"].status_tip == "Ghost floors."
