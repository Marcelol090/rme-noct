"""Legacy menu contract for the Python editor shell.

This module freezes the first wave of menu parity against the legacy
redux C++ editor so the shell can converge on one source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionSpec:
    """Declarative metadata for one legacy-facing action."""

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

LEGACY_NAVIGATE_FLOOR_LABELS = tuple(f"Floor {floor}" for floor in range(16))

LEGACY_WINDOW_PRIMARY_ITEMS = (
    "Minimap",
    "Tool Options",
    "Tile Properties",
    "In-game Preview",
    "New Palette",
)

LEGACY_WINDOW_PALETTE_ITEMS = (
    "Terrain",
    "Doodad",
    "Item",
    "Collection",
    "House",
    "Creature",
    "Waypoint",
    "RAW",
)

LEGACY_WINDOW_TOOLBAR_ITEMS = (
    "Brushes",
    "Position",
    "Sizes",
    "Standard",
)

LEGACY_EDITOR_ITEMS = (
    "New View",
    "Enter Fullscreen",
    "Take Screenshot",
)

LEGACY_EDITOR_ZOOM_ITEMS = (
    "Zoom In",
    "Zoom Out",
    "Zoom Normal",
)


PHASE1_ACTIONS: dict[str, ActionSpec] = {
    "find_item": ActionSpec(
        action_id="find_item",
        text="Find Item...",
        menu_path=("Search",),
        shortcut="Ctrl+F",
        status_tip="Find all instances of an item type the map.",
    ),
    "replace_items": ActionSpec(
        action_id="replace_items",
        text="Replace Items...",
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
    "goto_position": ActionSpec(
        action_id="goto_position",
        text="Go to Position...",
        menu_path=("Navigate",),
        shortcut="Ctrl+G",
        status_tip="Go to a specific XYZ position.",
    ),
    "goto_previous_position": ActionSpec(
        action_id="goto_previous_position",
        text="Go to Previous Position",
        menu_path=("Navigate",),
        shortcut="P",
        status_tip="Go to the previous screen center position.",
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
    "window_minimap": ActionSpec(
        action_id="window_minimap",
        text="Minimap",
        menu_path=("Window",),
        shortcut="M",
        status_tip="Displays the minimap window.",
    ),
    "window_tool_options": ActionSpec(
        action_id="window_tool_options",
        text="Tool Options",
        menu_path=("Window",),
        status_tip="Displays the tool options window.",
    ),
    "window_tile_properties": ActionSpec(
        action_id="window_tile_properties",
        text="Tile Properties",
        menu_path=("Window",),
        status_tip="Displays the tile properties panel.",
    ),
    "window_ingame_preview": ActionSpec(
        action_id="window_ingame_preview",
        text="In-game Preview",
        menu_path=("Window",),
        status_tip="Displays the in-game preview window.",
    ),
    "new_palette": ActionSpec(
        action_id="new_palette",
        text="New Palette",
        menu_path=("Window",),
        status_tip="Creates a new palette.",
    ),
    "select_palette_terrain": ActionSpec(
        action_id="select_palette_terrain",
        text="Terrain",
        menu_path=("Window", "Palette"),
        shortcut="T",
        status_tip="Select the Terrain palette.",
    ),
    "select_palette_doodad": ActionSpec(
        action_id="select_palette_doodad",
        text="Doodad",
        menu_path=("Window", "Palette"),
        shortcut="D",
        status_tip="Select the Doodad palette.",
    ),
    "select_palette_item": ActionSpec(
        action_id="select_palette_item",
        text="Item",
        menu_path=("Window", "Palette"),
        shortcut="I",
        status_tip="Select the Item palette.",
    ),
    "select_palette_collection": ActionSpec(
        action_id="select_palette_collection",
        text="Collection",
        menu_path=("Window", "Palette"),
        shortcut="N",
        status_tip="Select the Collection palette.",
    ),
    "select_palette_house": ActionSpec(
        action_id="select_palette_house",
        text="House",
        menu_path=("Window", "Palette"),
        shortcut="H",
        status_tip="Select the House palette.",
    ),
    "select_palette_creature": ActionSpec(
        action_id="select_palette_creature",
        text="Creature",
        menu_path=("Window", "Palette"),
        shortcut="C",
        status_tip="Select the Creature palette.",
    ),
    "select_palette_waypoint": ActionSpec(
        action_id="select_palette_waypoint",
        text="Waypoint",
        menu_path=("Window", "Palette"),
        shortcut="W",
        status_tip="Select the Waypoint palette.",
    ),
    "select_palette_raw": ActionSpec(
        action_id="select_palette_raw",
        text="RAW",
        menu_path=("Window", "Palette"),
        shortcut="R",
        status_tip="Select the RAW palette.",
    ),
    "view_toolbars_brushes": ActionSpec(
        action_id="view_toolbars_brushes",
        text="Brushes",
        menu_path=("Window", "Toolbars"),
        status_tip="Show or hide the Brushes toolbar.",
    ),
    "view_toolbars_position": ActionSpec(
        action_id="view_toolbars_position",
        text="Position",
        menu_path=("Window", "Toolbars"),
        status_tip="Show or hide the Position toolbar.",
    ),
    "view_toolbars_sizes": ActionSpec(
        action_id="view_toolbars_sizes",
        text="Sizes",
        menu_path=("Window", "Toolbars"),
        status_tip="Show or hide the Sizes toolbar.",
    ),
    "view_toolbars_standard": ActionSpec(
        action_id="view_toolbars_standard",
        text="Standard",
        menu_path=("Window", "Toolbars"),
        status_tip="Show or hide the Standard toolbar.",
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
    "editor_new_view": ActionSpec(
        action_id="editor_new_view",
        text="New View",
        menu_path=("Editor",),
        shortcut="Ctrl+Shift+N",
        status_tip="Creates a new view of the current map.",
    ),
    "editor_fullscreen": ActionSpec(
        action_id="editor_fullscreen",
        text="Enter Fullscreen",
        menu_path=("Editor",),
        shortcut="F11",
        status_tip="Changes between fullscreen mode and windowed mode.",
    ),
    "editor_screenshot": ActionSpec(
        action_id="editor_screenshot",
        text="Take Screenshot",
        menu_path=("Editor",),
        shortcut="F10",
        status_tip="Saves the current view to the disk.",
    ),
    "editor_zoom_in": ActionSpec(
        action_id="editor_zoom_in",
        text="Zoom In",
        menu_path=("Editor", "Zoom"),
        shortcut="Ctrl++",
        status_tip="Increase the zoom.",
    ),
    "editor_zoom_out": ActionSpec(
        action_id="editor_zoom_out",
        text="Zoom Out",
        menu_path=("Editor", "Zoom"),
        shortcut="Ctrl+-",
        status_tip="Decrease the zoom.",
    ),
    "editor_zoom_normal": ActionSpec(
        action_id="editor_zoom_normal",
        text="Zoom Normal",
        menu_path=("Editor", "Zoom"),
        shortcut="Ctrl+0",
        status_tip="Normal zoom(100%).",
    ),
}
