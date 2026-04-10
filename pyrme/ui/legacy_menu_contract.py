from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    text: str
    menu_path: tuple[str, ...]
    shortcut: str | None = None
    status_tip: str | None = None


LEGACY_TOP_LEVEL_MENUS = (
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


EDITOR_ACTION_ORDER = ("new_view", "toggle_fullscreen", "take_screenshot")
EDITOR_ZOOM_MENU_TITLE = "Zoom"
EDITOR_ZOOM_ACTION_ORDER = ("zoom_in", "zoom_out", "zoom_normal")


PHASE1_ACTIONS: dict[str, ActionSpec] = {
    "find_item": ActionSpec(
        action_id="find_item",
        text="&Find Item...",
        menu_path=("Search",),
        shortcut="Ctrl+F",
        status_tip="Find all instances of an item type the map.",
    ),
    "replace_items": ActionSpec(
        action_id="replace_items",
        text="&Replace Items...",
        menu_path=("Edit",),
        shortcut="Ctrl+Shift+F",
        status_tip="Replaces all occurrences of one item with another.",
    ),
    "map_properties": ActionSpec(
        action_id="map_properties",
        text="Properties...",
        menu_path=("Map",),
        shortcut="Ctrl+P",
        status_tip="Show and change the map properties.",
    ),
    "map_statistics": ActionSpec(
        action_id="map_statistics",
        text="Statistics",
        menu_path=("Map",),
        shortcut="F8",
        status_tip="Show map statistics.",
    ),
    "goto_previous_position": ActionSpec(
        action_id="goto_previous_position",
        text="Go to Previous Position",
        menu_path=("Navigate",),
        shortcut="P",
        status_tip="Go to the previous screen center position.",
    ),
    "goto_position": ActionSpec(
        action_id="goto_position",
        text="Go to Position...",
        menu_path=("Navigate",),
        shortcut="Ctrl+G",
        status_tip="Go to a specific XYZ position.",
    ),
    "jump_to_brush": ActionSpec(
        action_id="jump_to_brush",
        text="Jump to Brush...",
        menu_path=("Navigate",),
        shortcut="J",
        status_tip="Jump to a brush.",
    ),
    "jump_to_item": ActionSpec(
        action_id="jump_to_item",
        text="Jump to Item...",
        menu_path=("Navigate",),
        shortcut="Ctrl+J",
        status_tip="Jump to an item brush (RAW palette).",
    ),
    "show_grid": ActionSpec(
        action_id="show_grid",
        text="Show grid",
        menu_path=("View",),
        shortcut="Shift+G",
        status_tip="Shows a grid over all items.",
    ),
    "ghost_higher_floors": ActionSpec(
        action_id="ghost_higher_floors",
        text="Ghost higher floors",
        menu_path=("View",),
        shortcut="Ctrl+L",
        status_tip="Ghost floors.",
    ),
}


EDITOR_ACTIONS: dict[str, ActionSpec] = {
    "new_view": ActionSpec(
        action_id="new_view",
        text="New View",
        menu_path=("Editor",),
        shortcut="Ctrl+Shift+N",
        status_tip="Creates a new view of the current map.",
    ),
    "toggle_fullscreen": ActionSpec(
        action_id="toggle_fullscreen",
        text="Enter Fullscreen",
        menu_path=("Editor",),
        shortcut="F11",
        status_tip="Changes between fullscreen mode and windowed mode.",
    ),
    "take_screenshot": ActionSpec(
        action_id="take_screenshot",
        text="Take Screenshot",
        menu_path=("Editor",),
        shortcut="F10",
        status_tip="Saves the current view to the disk.",
    ),
    "zoom_in": ActionSpec(
        action_id="zoom_in",
        text="Zoom In",
        menu_path=("Editor", EDITOR_ZOOM_MENU_TITLE),
        shortcut="Ctrl++",
        status_tip="Increase the zoom.",
    ),
    "zoom_out": ActionSpec(
        action_id="zoom_out",
        text="Zoom Out",
        menu_path=("Editor", EDITOR_ZOOM_MENU_TITLE),
        shortcut="Ctrl+-",
        status_tip="Decrease the zoom.",
    ),
    "zoom_normal": ActionSpec(
        action_id="zoom_normal",
        text="Zoom Normal",
        menu_path=("Editor", EDITOR_ZOOM_MENU_TITLE),
        shortcut="Ctrl+0",
        status_tip="Normal zoom(100%).",
    ),
}
