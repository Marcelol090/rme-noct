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

LEGACY_FILE_MENU_SEQUENCE = (
    "New...",
    "Open...",
    "Save",
    "Save As...",
    "Generate Map",
    "Close",
    None,
    "Import",
    "Export",
    "Reload",
    "Missing Items Report...",
    None,
    "Recent Files",
    "Preferences",
    "Exit",
)

LEGACY_FILE_IMPORT_ITEMS = (
    "Import Map...",
    "Import Monsters/NPC...",
)

LEGACY_FILE_EXPORT_ITEMS = (
    "Export Minimap...",
    "Export Tilesets...",
)

LEGACY_FILE_RELOAD_ITEMS = ("Reload Data Files",)

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

LEGACY_SEARCH_MENU_SEQUENCE = (
    "Find Item...",
    None,
    "Find Unique",
    "Find Action",
    "Find Container",
    "Find Writeable",
    None,
    "Find Everything",
)

LEGACY_EDIT_MENU_SEQUENCE = (
    "Undo",
    "Redo",
    None,
    "Replace Items...",
    None,
    "Border Options",
    "Other Options",
    None,
    "Cut",
    "Copy",
    "Paste",
)

LEGACY_EDIT_BORDER_ITEMS = (
    "Border Automagic",
    None,
    "Borderize Selection",
    "Borderize Map",
    "Randomize Selection",
    "Randomize Map",
)

LEGACY_EDIT_OTHER_ITEMS = (
    "Remove Items by ID...",
    "Remove all Corpses...",
    "Remove all Unreachable Tiles...",
    "Clear Invalid Houses",
    "Clear Modified State",
)

LEGACY_EDIT_STATE_DEFAULTS = {"border_automagic": True}

LEGACY_SELECTION_MENU_SEQUENCE = (
    "Replace Items on Selection",
    "Find Item on Selection",
    "Remove Item on Selection",
    None,
    "Find on Selection",
    None,
    "Selection Mode",
    None,
    "Borderize Selection",
    "Randomize Selection",
)

LEGACY_SELECTION_FIND_ITEMS = (
    "Find Everything",
    None,
    "Find Unique",
    "Find Action",
    "Find Container",
    "Find Writeable",
)

LEGACY_SELECTION_MODE_ITEMS = (
    "Compensate Selection",
    None,
    "Current Floor",
    "Lower Floors",
    "Visible Floors",
)

LEGACY_SELECTION_MODE_DEFAULTS = {
    "select_mode_compensate": True,
    "select_mode_current": True,
    "select_mode_lower": False,
    "select_mode_visible": False,
}

LEGACY_MAP_MENU_SEQUENCE = (
    "Edit Towns",
    None,
    "Cleanup invalid tiles...",
    "Cleanup invalid zones...",
    "Properties...",
    "Statistics",
)

LEGACY_VIEW_MENU_SEQUENCE = (
    "Show all Floors",
    "Show as Minimap",
    "Only show Colors",
    "Only show Modified",
    "Always show zones",
    "Extended house shader",
    None,
    "Show tooltips",
    "Show grid",
    "Show client box",
    None,
    "Ghost loose items",
    "Ghost higher floors",
    "Show shade",
)

LEGACY_VIEW_FLAG_DEFAULTS = {
    "view_show_all_floors": True,
    "view_show_as_minimap": False,
    "view_only_show_colors": False,
    "view_only_show_modified": False,
    "view_always_show_zones": True,
    "view_extended_house_shader": True,
    "view_show_tooltips": True,
    "show_grid": False,
    "view_show_client_box": False,
    "view_ghost_loose_items": False,
    "ghost_higher_floors": False,
    "view_show_shade": True,
}

LEGACY_SHOW_MENU_SEQUENCE = (
    "Show Animation",
    "Show Light",
    "Show Light Strength",
    "Show Technical Items",
    "Show Invalid Tiles",
    "Show Invalid Zones",
    None,
    "Show creatures",
    "Show spawns",
    "Show special",
    "Show houses",
    "Show pathing",
    "Show towns",
    "Show waypoints",
    None,
    "Highlight Items",
    "Highlight Locked Doors",
    "Show Wall Hooks",
)

LEGACY_SHOW_FLAG_DEFAULTS = {
    "show_animation": True,
    "show_light": False,
    "show_light_strength": True,
    "show_technical_items": True,
    "show_invalid_tiles": True,
    "show_invalid_zones": True,
    "show_creatures": True,
    "show_spawns": True,
    "show_special": True,
    "show_houses": True,
    "show_pathing": False,
    "show_towns": False,
    "show_waypoints": True,
    "highlight_items": False,
    "highlight_locked_doors": True,
    "show_wall_hooks": False,
}

LEGACY_EXPERIMENTAL_MENU_SEQUENCE = ("Fog in light view",)

LEGACY_SCRIPTS_MENU_SEQUENCE = (
    "Script Manager...",
    "Open Scripts Folder",
    "Reload Scripts",
)

LEGACY_ABOUT_MENU_SEQUENCE = (
    "Extensions...",
    "Goto Website",
    "About...",
)


PHASE1_ACTIONS: dict[str, ActionSpec] = {
    "file_new": ActionSpec(
        action_id="file_new",
        text="New...",
        menu_path=("File",),
        shortcut="Ctrl+N",
        status_tip="Create a new map.",
    ),
    "file_open": ActionSpec(
        action_id="file_open",
        text="Open...",
        menu_path=("File",),
        shortcut="Ctrl+O",
        status_tip="Open another map.",
    ),
    "file_save": ActionSpec(
        action_id="file_save",
        text="Save",
        menu_path=("File",),
        shortcut="Ctrl+S",
        status_tip="Save the current map.",
    ),
    "file_save_as": ActionSpec(
        action_id="file_save_as",
        text="Save As...",
        menu_path=("File",),
        shortcut="Ctrl+Alt+S",
        status_tip="Save the current map as a new file.",
    ),
    "file_generate_map": ActionSpec(
        action_id="file_generate_map",
        text="Generate Map",
        menu_path=("File",),
        status_tip="Generate a new map.",
    ),
    "file_close": ActionSpec(
        action_id="file_close",
        text="Close",
        menu_path=("File",),
        shortcut="Ctrl+Q",
        status_tip="Closes the currently open map.",
    ),
    "file_import_map": ActionSpec(
        action_id="file_import_map",
        text="Import Map...",
        menu_path=("File", "Import"),
        status_tip="Import map data from another map file.",
    ),
    "file_import_monsters": ActionSpec(
        action_id="file_import_monsters",
        text="Import Monsters/NPC...",
        menu_path=("File", "Import"),
        status_tip="Import either a monsters.xml file or a specific monster/NPC.",
    ),
    "file_export_minimap": ActionSpec(
        action_id="file_export_minimap",
        text="Export Minimap...",
        menu_path=("File", "Export"),
        status_tip="Export minimap to an image file.",
    ),
    "file_export_tilesets": ActionSpec(
        action_id="file_export_tilesets",
        text="Export Tilesets...",
        menu_path=("File", "Export"),
        status_tip="Export tilesets to an xml file.",
    ),
    "file_reload_data": ActionSpec(
        action_id="file_reload_data",
        text="Reload Data Files",
        menu_path=("File", "Reload"),
        shortcut="F5",
        status_tip="Reloads all data files.",
    ),
    "file_missing_items_report": ActionSpec(
        action_id="file_missing_items_report",
        text="Missing Items Report...",
        menu_path=("File",),
        status_tip="View missing item definitions between data files.",
    ),
    "file_preferences": ActionSpec(
        action_id="file_preferences",
        text="Preferences",
        menu_path=("File",),
        status_tip="Configure the map editor.",
    ),
    "file_exit": ActionSpec(
        action_id="file_exit",
        text="Exit",
        menu_path=("File",),
        status_tip="Close the editor.",
    ),
    "edit_undo": ActionSpec(
        action_id="edit_undo",
        text="Undo",
        menu_path=("Edit",),
        shortcut="Ctrl+Z",
        status_tip="Undo last action.",
    ),
    "edit_redo": ActionSpec(
        action_id="edit_redo",
        text="Redo",
        menu_path=("Edit",),
        shortcut="Ctrl+Shift+Z",
        status_tip="Redo last undid action.",
    ),
    "find_item": ActionSpec(
        action_id="find_item",
        text="Find Item...",
        menu_path=("Search",),
        shortcut="Ctrl+F",
        status_tip="Find all instances of an item type the map.",
    ),
    "search_on_map_unique": ActionSpec(
        action_id="search_on_map_unique",
        text="Find Unique",
        menu_path=("Search",),
        status_tip="Find all items with an unique ID on map.",
    ),
    "search_on_map_action": ActionSpec(
        action_id="search_on_map_action",
        text="Find Action",
        menu_path=("Search",),
        status_tip="Find all items with an action ID on map.",
    ),
    "search_on_map_container": ActionSpec(
        action_id="search_on_map_container",
        text="Find Container",
        menu_path=("Search",),
        status_tip="Find all containers on map.",
    ),
    "search_on_map_writeable": ActionSpec(
        action_id="search_on_map_writeable",
        text="Find Writeable",
        menu_path=("Search",),
        status_tip="Find all writeable items on map.",
    ),
    "search_on_map_everything": ActionSpec(
        action_id="search_on_map_everything",
        text="Find Everything",
        menu_path=("Search",),
        status_tip="Find all unique/action/text/container items.",
    ),
    "replace_items": ActionSpec(
        action_id="replace_items",
        text="Replace Items...",
        menu_path=("Edit",),
        shortcut="Ctrl+Shift+F",
        status_tip="Replaces all occurrences of one item with another.",
    ),
    "border_automagic": ActionSpec(
        action_id="border_automagic",
        text="Border Automagic",
        menu_path=("Edit", "Border Options"),
        shortcut="A",
        status_tip="Turns on all automatic border functions.",
    ),
    "borderize_selection": ActionSpec(
        action_id="borderize_selection",
        text="Borderize Selection",
        menu_path=("Edit", "Border Options"),
        shortcut="Ctrl+B",
        status_tip="Creates automatic borders in the entire selected area.",
    ),
    "borderize_map": ActionSpec(
        action_id="borderize_map",
        text="Borderize Map",
        menu_path=("Edit", "Border Options"),
        status_tip="Reborders the entire map.",
    ),
    "randomize_selection": ActionSpec(
        action_id="randomize_selection",
        text="Randomize Selection",
        menu_path=("Edit", "Border Options"),
        status_tip="Randomizes the ground tiles of the selected area.",
    ),
    "randomize_map": ActionSpec(
        action_id="randomize_map",
        text="Randomize Map",
        menu_path=("Edit", "Border Options"),
        status_tip="Randomizes all tiles of the entire map.",
    ),
    "remove_items_by_id": ActionSpec(
        action_id="remove_items_by_id",
        text="Remove Items by ID...",
        menu_path=("Edit", "Other Options"),
        shortcut="Ctrl+Shift+R",
        status_tip="Removes all items with the selected ID from the map.",
    ),
    "remove_all_corpses": ActionSpec(
        action_id="remove_all_corpses",
        text="Remove all Corpses...",
        menu_path=("Edit", "Other Options"),
        status_tip="Removes all corpses from the map.",
    ),
    "remove_all_unreachable_tiles": ActionSpec(
        action_id="remove_all_unreachable_tiles",
        text="Remove all Unreachable Tiles...",
        menu_path=("Edit", "Other Options"),
        status_tip="Removes all tiles that cannot be reached (or seen) by the player from the map.",
    ),
    "clear_invalid_houses": ActionSpec(
        action_id="clear_invalid_houses",
        text="Clear Invalid Houses",
        menu_path=("Edit", "Other Options"),
        status_tip="Clears house tiles not belonging to any house.",
    ),
    "clear_modified_state": ActionSpec(
        action_id="clear_modified_state",
        text="Clear Modified State",
        menu_path=("Edit", "Other Options"),
        status_tip="Clears the modified state from all tiles.",
    ),
    "edit_cut": ActionSpec(
        action_id="edit_cut",
        text="Cut",
        menu_path=("Edit",),
        shortcut="Ctrl+X",
        status_tip="Cut a part of the map.",
    ),
    "edit_copy": ActionSpec(
        action_id="edit_copy",
        text="Copy",
        menu_path=("Edit",),
        shortcut="Ctrl+C",
        status_tip="Copy a part of the map.",
    ),
    "edit_paste": ActionSpec(
        action_id="edit_paste",
        text="Paste",
        menu_path=("Edit",),
        shortcut="Ctrl+V",
        status_tip="Paste a part of the map.",
    ),
    "replace_on_selection_items": ActionSpec(
        action_id="replace_on_selection_items",
        text="Replace Items on Selection",
        menu_path=("Selection",),
        status_tip="Replace items on selected area.",
    ),
    "search_on_selection_item": ActionSpec(
        action_id="search_on_selection_item",
        text="Find Item on Selection",
        menu_path=("Selection",),
        status_tip="Find items on selected area.",
    ),
    "remove_on_selection_item": ActionSpec(
        action_id="remove_on_selection_item",
        text="Remove Item on Selection",
        menu_path=("Selection",),
        status_tip="Remove item on selected area.",
    ),
    "search_on_selection_everything": ActionSpec(
        action_id="search_on_selection_everything",
        text="Find Everything",
        menu_path=("Selection", "Find on Selection"),
        status_tip="Find all unique/action/text/container items.",
    ),
    "search_on_selection_unique": ActionSpec(
        action_id="search_on_selection_unique",
        text="Find Unique",
        menu_path=("Selection", "Find on Selection"),
        status_tip="Find all items with an unique ID on selected area.",
    ),
    "search_on_selection_action": ActionSpec(
        action_id="search_on_selection_action",
        text="Find Action",
        menu_path=("Selection", "Find on Selection"),
        status_tip="Find all items with an action ID on selected area.",
    ),
    "search_on_selection_container": ActionSpec(
        action_id="search_on_selection_container",
        text="Find Container",
        menu_path=("Selection", "Find on Selection"),
        status_tip="Find all containers on selected area.",
    ),
    "search_on_selection_writeable": ActionSpec(
        action_id="search_on_selection_writeable",
        text="Find Writeable",
        menu_path=("Selection", "Find on Selection"),
        status_tip="Find all writeable items on selected area.",
    ),
    "select_mode_compensate": ActionSpec(
        action_id="select_mode_compensate",
        text="Compensate Selection",
        menu_path=("Selection", "Selection Mode"),
        status_tip="Compensate for floor difference when selecting.",
    ),
    "select_mode_current": ActionSpec(
        action_id="select_mode_current",
        text="Current Floor",
        menu_path=("Selection", "Selection Mode"),
        status_tip="Select only current floor.",
    ),
    "select_mode_lower": ActionSpec(
        action_id="select_mode_lower",
        text="Lower Floors",
        menu_path=("Selection", "Selection Mode"),
        status_tip="Select all lower floors.",
    ),
    "select_mode_visible": ActionSpec(
        action_id="select_mode_visible",
        text="Visible Floors",
        menu_path=("Selection", "Selection Mode"),
        status_tip="Select only visible floors.",
    ),
    "map_edit_towns": ActionSpec(
        action_id="map_edit_towns",
        text="Edit Towns",
        menu_path=("Map",),
        shortcut="Ctrl+T",
        status_tip="Edit towns.",
    ),
    "map_cleanup_invalid_tiles": ActionSpec(
        action_id="map_cleanup_invalid_tiles",
        text="Cleanup invalid tiles...",
        menu_path=("Map",),
        status_tip="Removes all invalid or unresolved items from the map.",
    ),
    "map_cleanup_invalid_zones": ActionSpec(
        action_id="map_cleanup_invalid_zones",
        text="Cleanup invalid zones...",
        menu_path=("Map",),
        status_tip=(
            "Removes preserved invalid tile flags and opaque OTBM tile fragments from the map."
        ),
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
    "view_show_all_floors": ActionSpec(
        action_id="view_show_all_floors",
        text="Show all Floors",
        menu_path=("View",),
        shortcut="Ctrl+W",
        status_tip="If not checked other floors are hidden.",
    ),
    "view_show_as_minimap": ActionSpec(
        action_id="view_show_as_minimap",
        text="Show as Minimap",
        menu_path=("View",),
        shortcut="Shift+E",
        status_tip="Show only the tile minimap colors.",
    ),
    "view_only_show_colors": ActionSpec(
        action_id="view_only_show_colors",
        text="Only show Colors",
        menu_path=("View",),
        shortcut="Ctrl+E",
        status_tip="Show only the special tiles on the map.",
    ),
    "view_only_show_modified": ActionSpec(
        action_id="view_only_show_modified",
        text="Only show Modified",
        menu_path=("View",),
        shortcut="Ctrl+M",
        status_tip="Show only the tiles that have been modified since the map was opened.",
    ),
    "view_always_show_zones": ActionSpec(
        action_id="view_always_show_zones",
        text="Always show zones",
        menu_path=("View",),
        status_tip="Zones will be visible even on empty tiles.",
    ),
    "view_extended_house_shader": ActionSpec(
        action_id="view_extended_house_shader",
        text="Extended house shader",
        menu_path=("View",),
        status_tip="Draw house brush on walls and items.",
    ),
    "view_show_tooltips": ActionSpec(
        action_id="view_show_tooltips",
        text="Show tooltips",
        menu_path=("View",),
        shortcut="Y",
        status_tip="Show tooltips.",
    ),
    "show_grid": ActionSpec(
        action_id="show_grid",
        text="Show grid",
        menu_path=("View",),
        shortcut="Shift+G",
        status_tip="Shows a grid over all items.",
    ),
    "view_show_client_box": ActionSpec(
        action_id="view_show_client_box",
        text="Show client box",
        menu_path=("View",),
        shortcut="Shift+I",
        status_tip="Shadows out areas not visible ingame (from the center of the screen).",
    ),
    "view_ghost_loose_items": ActionSpec(
        action_id="view_ghost_loose_items",
        text="Ghost loose items",
        menu_path=("View",),
        shortcut="G",
        status_tip="Ghost items (except ground).",
    ),
    "ghost_higher_floors": ActionSpec(
        action_id="ghost_higher_floors",
        text="Ghost higher floors",
        menu_path=("View",),
        shortcut="Ctrl+L",
        status_tip="Ghost floors.",
    ),
    "view_show_shade": ActionSpec(
        action_id="view_show_shade",
        text="Show shade",
        menu_path=("View",),
        shortcut="Q",
        status_tip="Shade lower floors.",
    ),
    "show_animation": ActionSpec(
        action_id="show_animation",
        text="Show Animation",
        menu_path=("Show",),
        shortcut="L",
        status_tip="Show item animations.",
    ),
    "show_light": ActionSpec(
        action_id="show_light",
        text="Show Light",
        menu_path=("Show",),
        shortcut="Shift+L",
        status_tip="Show lights.",
    ),
    "show_light_strength": ActionSpec(
        action_id="show_light_strength",
        text="Show Light Strength",
        menu_path=("Show",),
        shortcut="Shift+K",
        status_tip="Show indicators of light strength.",
    ),
    "show_technical_items": ActionSpec(
        action_id="show_technical_items",
        text="Show Technical Items",
        menu_path=("Show",),
        shortcut="Shift+T",
        status_tip="Shows some of special items that are not visible in game.",
    ),
    "show_invalid_tiles": ActionSpec(
        action_id="show_invalid_tiles",
        text="Show Invalid Tiles",
        menu_path=("Show",),
        status_tip="Show preserved invalid OTBM content as tile overlays.",
    ),
    "show_invalid_zones": ActionSpec(
        action_id="show_invalid_zones",
        text="Show Invalid Zones",
        menu_path=("Show",),
        status_tip="Show invalid tile flags and opaque OTBM tile fragments as magenta overlays.",
    ),
    "show_creatures": ActionSpec(
        action_id="show_creatures",
        text="Show creatures",
        menu_path=("Show",),
        shortcut="F",
        status_tip="Show creatures on the map.",
    ),
    "show_spawns": ActionSpec(
        action_id="show_spawns",
        text="Show spawns",
        menu_path=("Show",),
        shortcut="S",
        status_tip="Show spawns on the map.",
    ),
    "show_special": ActionSpec(
        action_id="show_special",
        text="Show special",
        menu_path=("Show",),
        shortcut="E",
        status_tip="Show special tiles on the map, like PZ.",
    ),
    "show_houses": ActionSpec(
        action_id="show_houses",
        text="Show houses",
        menu_path=("Show",),
        shortcut="Ctrl+H",
        status_tip="Show houses on the map.",
    ),
    "show_pathing": ActionSpec(
        action_id="show_pathing",
        text="Show pathing",
        menu_path=("Show",),
        shortcut="O",
        status_tip="Show blocking tiles.",
    ),
    "show_towns": ActionSpec(
        action_id="show_towns",
        text="Show towns",
        menu_path=("Show",),
        status_tip="Show temple positions.",
    ),
    "show_waypoints": ActionSpec(
        action_id="show_waypoints",
        text="Show waypoints",
        menu_path=("Show",),
        shortcut="Shift+W",
        status_tip="Show waypoints.",
    ),
    "highlight_items": ActionSpec(
        action_id="highlight_items",
        text="Highlight Items",
        menu_path=("Show",),
        shortcut="V",
        status_tip="Highlight tiles with items on them.",
    ),
    "highlight_locked_doors": ActionSpec(
        action_id="highlight_locked_doors",
        text="Highlight Locked Doors",
        menu_path=("Show",),
        shortcut="U",
        status_tip="Highlight doors that require key to open.",
    ),
    "show_wall_hooks": ActionSpec(
        action_id="show_wall_hooks",
        text="Show Wall Hooks",
        menu_path=("Show",),
        shortcut="K",
        status_tip="Show indicators for wall hooks.",
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
    "experimental_fog": ActionSpec(
        action_id="experimental_fog",
        text="Fog in light view",
        menu_path=("Experimental",),
        status_tip="Apply fog filter to light effect.",
    ),
    "scripts_manager": ActionSpec(
        action_id="scripts_manager",
        text="Script Manager...",
        menu_path=("Scripts",),
        status_tip="Show/hide the Script Manager window.",
    ),
    "scripts_open_folder": ActionSpec(
        action_id="scripts_open_folder",
        text="Open Scripts Folder",
        menu_path=("Scripts",),
        status_tip="Open the scripts folder in file explorer.",
    ),
    "scripts_reload": ActionSpec(
        action_id="scripts_reload",
        text="Reload Scripts",
        menu_path=("Scripts",),
        shortcut="Ctrl+Shift+F5",
        status_tip="Reload all scripts from disk.",
    ),
    "extensions": ActionSpec(
        action_id="extensions",
        text="Extensions...",
        menu_path=("About",),
        shortcut="F2",
        status_tip="Manage extensions.",
    ),
    "goto_website": ActionSpec(
        action_id="goto_website",
        text="Goto Website",
        menu_path=("About",),
        shortcut="F3",
        status_tip="Visit the official website.",
    ),
    "about": ActionSpec(
        action_id="about",
        text="About...",
        menu_path=("About",),
        shortcut="F1",
        status_tip="Show information about the application.",
    ),
}
