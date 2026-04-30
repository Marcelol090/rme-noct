"""Legacy menu contract for the Python editor shell.

The tracked ``pyrme/assets/contracts/legacy/menubar.xml`` snapshot is the
publishable source of truth for labels, shortcuts, help text, and menu
ordering. This module exposes the subset of that contract currently mounted by
the Python shell.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from functools import cache
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ActionSpec:
    """Declarative metadata for one legacy-facing action."""

    action_id: str
    text: str
    menu_path: tuple[str, ...]
    shortcut: str | None = None
    status_tip: str | None = None


_PYRME_ROOT = Path(__file__).resolve().parents[1]
LEGACY_MENUBAR_XML = _PYRME_ROOT / "assets" / "contracts" / "legacy" / "menubar.xml"
_MENUBAR_ROOT = ET.parse(LEGACY_MENUBAR_XML).getroot()


@cache
def _menu(name: str, parent: ET.Element | None = None) -> ET.Element:
    source = _MENUBAR_ROOT if parent is None else parent
    for node in source.findall("menu"):
        if node.get("name") == name:
            return node
    raise KeyError(f"Legacy menu not found: {name}")


def _menu_path(*names: str) -> ET.Element:
    current: ET.Element | None = None
    for name in names:
        current = _menu(name, current)
    assert current is not None
    return current


def _sequence(*names: str) -> tuple[str | None, ...]:
    menu = _menu_path(*names)
    items: list[str | None] = []
    for child in menu:
        if child.tag == "separator":
            items.append(None)
        elif child.tag in {"item", "menu"}:
            items.append(child.get("name", ""))
    return tuple(items)


def _action_nodes() -> dict[str, ET.Element]:
    nodes: dict[str, ET.Element] = {}
    for node in _MENUBAR_ROOT.iter("item"):
        action = node.get("action")
        if action and action not in nodes:
            nodes[action] = node
    return nodes


_XML_ACTIONS = _action_nodes()

LEGACY_TOP_LEVEL_MENUS = tuple(
    node.get("name", "") for node in _MENUBAR_ROOT.findall("menu")
)

LEGACY_FILE_MENU_SEQUENCE = _sequence("File")
LEGACY_FILE_IMPORT_ITEMS = _sequence("File", "Import")
LEGACY_FILE_EXPORT_ITEMS = _sequence("File", "Export")
LEGACY_FILE_RELOAD_ITEMS = _sequence("File", "Reload")

LEGACY_EDIT_MENU_SEQUENCE = _sequence("Edit")
LEGACY_EDIT_BORDER_ITEMS = _sequence("Edit", "Border Options")
LEGACY_EDIT_OTHER_ITEMS = _sequence("Edit", "Other Options")
LEGACY_EDIT_STATE_DEFAULTS = {"border_automagic": True}

LEGACY_EDITOR_ITEMS = tuple(
    child.get("name", "")
    for child in _menu_path("Editor").findall("item")
)
LEGACY_EDITOR_ZOOM_ITEMS = _sequence("Editor", "Zoom")

LEGACY_SEARCH_MENU_SEQUENCE = _sequence("Search")
LEGACY_MAP_MENU_SEQUENCE = _sequence("Map")

LEGACY_SELECTION_MENU_SEQUENCE = _sequence("Selection")
LEGACY_SELECTION_FIND_ITEMS = _sequence("Selection", "Find on Selection")
LEGACY_SELECTION_MODE_ITEMS = _sequence("Selection", "Selection Mode")
LEGACY_SELECTION_MODE_DEFAULTS = {
    "select_mode_compensate": True,
    "select_mode_current": True,
    "select_mode_lower": False,
    "select_mode_visible": False,
}

LEGACY_VIEW_MENU_SEQUENCE = _sequence("View")
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

LEGACY_SHOW_MENU_SEQUENCE = _sequence("Show")
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

LEGACY_NAVIGATE_FLOOR_LABELS = _sequence("Navigate", "Floor")
LEGACY_WINDOW_PRIMARY_ITEMS = tuple(
    child.get("name", "")
    for child in _menu_path("Window")
    if child.tag == "item"
)
LEGACY_WINDOW_PALETTE_ITEMS = _sequence("Window", "Palette")
LEGACY_WINDOW_TOOLBAR_ITEMS = _sequence("Window", "Toolbars")


_ACTION_KEY_BY_XML_ID = {
    "NEW": "file_new",
    "OPEN": "file_open",
    "SAVE": "file_save",
    "SAVE_AS": "file_save_as",
    "GENERATE_MAP": "file_generate_map",
    "CLOSE": "file_close",
    "IMPORT_MAP": "file_import_map",
    "IMPORT_MONSTERS": "file_import_monsters",
    "EXPORT_MINIMAP": "file_export_minimap",
    "EXPORT_TILESETS": "file_export_tilesets",
    "RELOAD_DATA": "file_reload_data",
    "MISSING_ITEMS_REPORT": "file_missing_items_report",
    "PREFERENCES": "file_preferences",
    "EXIT": "file_exit",
    "UNDO": "edit_undo",
    "REDO": "edit_redo",
    "REPLACE_ITEMS": "replace_items",
    "AUTOMAGIC": "border_automagic",
    "BORDERIZE_SELECTION": "borderize_selection",
    "BORDERIZE_MAP": "borderize_map",
    "RANDOMIZE_SELECTION": "randomize_selection",
    "RANDOMIZE_MAP": "randomize_map",
    "MAP_REMOVE_ITEMS": "remove_items_by_id",
    "MAP_REMOVE_CORPSES": "remove_all_corpses",
    "MAP_REMOVE_UNREACHABLE_TILES": "remove_all_unreachable_tiles",
    "CLEAR_INVALID_HOUSES": "clear_invalid_houses",
    "CLEAR_MODIFIED_STATE": "clear_modified_state",
    "CUT": "edit_cut",
    "COPY": "edit_copy",
    "PASTE": "edit_paste",
    "FIND_ITEM": "find_item",
    "SEARCH_ON_MAP_UNIQUE": "search_on_map_unique",
    "SEARCH_ON_MAP_ACTION": "search_on_map_action",
    "SEARCH_ON_MAP_CONTAINER": "search_on_map_container",
    "SEARCH_ON_MAP_WRITEABLE": "search_on_map_writeable",
    "SEARCH_ON_MAP_EVERYTHING": "search_on_map_everything",
    "EDIT_TOWNS": "map_edit_towns",
    "EDIT_HOUSES": "map_edit_houses",
    "MAP_CLEANUP": "map_cleanup_invalid_tiles",
    "MAP_CLEAN_INVALID_ZONES": "map_cleanup_invalid_zones",
    "MAP_PROPERTIES": "map_properties",
    "MAP_STATISTICS": "map_statistics",
    "REPLACE_ON_SELECTION_ITEMS": "replace_on_selection_items",
    "SEARCH_ON_SELECTION_ITEM": "search_on_selection_item",
    "REMOVE_ON_SELECTION_ITEM": "remove_on_selection_item",
    "SEARCH_ON_SELECTION_EVERYTHING": "search_on_selection_everything",
    "SEARCH_ON_SELECTION_UNIQUE": "search_on_selection_unique",
    "SEARCH_ON_SELECTION_ACTION": "search_on_selection_action",
    "SEARCH_ON_SELECTION_CONTAINER": "search_on_selection_container",
    "SEARCH_ON_SELECTION_WRITEABLE": "search_on_selection_writeable",
    "SELECT_MODE_COMPENSATE": "select_mode_compensate",
    "SELECT_MODE_CURRENT": "select_mode_current",
    "SELECT_MODE_LOWER": "select_mode_lower",
    "SELECT_MODE_VISIBLE": "select_mode_visible",
    "SHOW_ALL_FLOORS": "view_show_all_floors",
    "SHOW_AS_MINIMAP": "view_show_as_minimap",
    "SHOW_ONLY_COLORS": "view_only_show_colors",
    "SHOW_ONLY_MODIFIED": "view_only_show_modified",
    "ALWAYS_SHOW_ZONES": "view_always_show_zones",
    "EXT_HOUSE_SHADER": "view_extended_house_shader",
    "SHOW_TOOLTIPS": "view_show_tooltips",
    "SHOW_GRID": "show_grid",
    "SHOW_INGAME_BOX": "view_show_client_box",
    "GHOST_ITEMS": "view_ghost_loose_items",
    "GHOST_HIGHER_FLOORS": "ghost_higher_floors",
    "SHOW_SHADE": "view_show_shade",
    "SHOW_PREVIEW": "show_animation",
    "SHOW_LIGHTS": "show_light",
    "SHOW_LIGHT_STR": "show_light_strength",
    "SHOW_TECHNICAL_ITEMS": "show_technical_items",
    "SHOW_INVALID_TILES": "show_invalid_tiles",
    "SHOW_INVALID_ZONES": "show_invalid_zones",
    "SHOW_CREATURES": "show_creatures",
    "SHOW_SPAWNS": "show_spawns",
    "SHOW_SPECIAL": "show_special",
    "SHOW_HOUSES": "show_houses",
    "SHOW_PATHING": "show_pathing",
    "SHOW_TOWNS": "show_towns",
    "SHOW_WAYPOINTS": "show_waypoints",
    "HIGHLIGHT_ITEMS": "highlight_items",
    "HIGHLIGHT_LOCKED_DOORS": "highlight_locked_doors",
    "SHOW_WALL_HOOKS": "show_wall_hooks",
    "GOTO_POSITION": "goto_position",
    "GOTO_PREVIOUS_POSITION": "goto_previous_position",
    "JUMP_TO_BRUSH": "jump_to_brush",
    "JUMP_TO_ITEM_BRUSH": "jump_to_item",
    "WIN_MINIMAP": "window_minimap",
    "WIN_TOOL_OPTIONS": "window_tool_options",
    "WIN_TILE_PROPERTIES": "window_tile_properties",
    "WIN_INGAME_PREVIEW": "window_ingame_preview",
    "NEW_PALETTE": "new_palette",
    "SELECT_TERRAIN": "select_palette_terrain",
    "SELECT_DOODAD": "select_palette_doodad",
    "SELECT_ITEM": "select_palette_item",
    "SELECT_COLLECTION": "select_palette_collection",
    "SELECT_HOUSE": "select_palette_house",
    "SELECT_CREATURE": "select_palette_creature",
    "SELECT_WAYPOINT": "select_palette_waypoint",
    "SELECT_RAW": "select_palette_raw",
    "VIEW_TOOLBARS_BRUSHES": "view_toolbars_brushes",
    "VIEW_TOOLBARS_POSITION": "view_toolbars_position",
    "VIEW_TOOLBARS_SIZES": "view_toolbars_sizes",
    "VIEW_TOOLBARS_STANDARD": "view_toolbars_standard",
    "NEW_VIEW": "editor_new_view",
    "TOGGLE_FULLSCREEN": "editor_fullscreen",
    "TAKE_SCREENSHOT": "editor_screenshot",
    "ZOOM_IN": "editor_zoom_in",
    "ZOOM_OUT": "editor_zoom_out",
    "ZOOM_NORMAL": "editor_zoom_normal",
    "EXPERIMENTAL_FOG": "experimental_fog",
    "SCRIPTS_MANAGER": "scripts_manager",
    "SCRIPTS_OPEN_FOLDER": "scripts_open_folder",
    "SCRIPTS_RELOAD": "scripts_reload",
    "EXTENSIONS": "about_extensions",
    "GOTO_WEBSITE": "about_goto_website",
    "ABOUT": "about",
}

_MENU_PATH_BY_ACTION_KEY = {
    "file_new": ("File",),
    "file_open": ("File",),
    "file_save": ("File",),
    "file_save_as": ("File",),
    "file_generate_map": ("File",),
    "file_close": ("File",),
    "file_import_map": ("File", "Import"),
    "file_import_monsters": ("File", "Import"),
    "file_export_minimap": ("File", "Export"),
    "file_export_tilesets": ("File", "Export"),
    "file_reload_data": ("File", "Reload"),
    "file_missing_items_report": ("File",),
    "file_preferences": ("File",),
    "file_exit": ("File",),
    "edit_undo": ("Edit",),
    "edit_redo": ("Edit",),
    "replace_items": ("Edit",),
    "border_automagic": ("Edit", "Border Options"),
    "borderize_selection": ("Edit", "Border Options"),
    "borderize_map": ("Edit", "Border Options"),
    "randomize_selection": ("Edit", "Border Options"),
    "randomize_map": ("Edit", "Border Options"),
    "remove_items_by_id": ("Edit", "Other Options"),
    "remove_all_corpses": ("Edit", "Other Options"),
    "remove_all_unreachable_tiles": ("Edit", "Other Options"),
    "clear_invalid_houses": ("Edit", "Other Options"),
    "clear_modified_state": ("Edit", "Other Options"),
    "edit_cut": ("Edit",),
    "edit_copy": ("Edit",),
    "edit_paste": ("Edit",),
    "find_item": ("Search",),
    "search_on_map_unique": ("Search",),
    "search_on_map_action": ("Search",),
    "search_on_map_container": ("Search",),
    "search_on_map_writeable": ("Search",),
    "search_on_map_everything": ("Search",),
    "map_edit_towns": ("Map",),
    "map_edit_houses": ("Map",),
    "map_cleanup_invalid_tiles": ("Map",),
    "map_cleanup_invalid_zones": ("Map",),
    "map_properties": ("Map",),
    "map_statistics": ("Map",),
    "replace_on_selection_items": ("Selection",),
    "search_on_selection_item": ("Selection",),
    "remove_on_selection_item": ("Selection",),
    "search_on_selection_everything": ("Selection", "Find on Selection"),
    "search_on_selection_unique": ("Selection", "Find on Selection"),
    "search_on_selection_action": ("Selection", "Find on Selection"),
    "search_on_selection_container": ("Selection", "Find on Selection"),
    "search_on_selection_writeable": ("Selection", "Find on Selection"),
    "select_mode_compensate": ("Selection", "Selection Mode"),
    "select_mode_current": ("Selection", "Selection Mode"),
    "select_mode_lower": ("Selection", "Selection Mode"),
    "select_mode_visible": ("Selection", "Selection Mode"),
    "view_show_all_floors": ("View",),
    "view_show_as_minimap": ("View",),
    "view_only_show_colors": ("View",),
    "view_only_show_modified": ("View",),
    "view_always_show_zones": ("View",),
    "view_extended_house_shader": ("View",),
    "view_show_tooltips": ("View",),
    "show_grid": ("View",),
    "view_show_client_box": ("View",),
    "view_ghost_loose_items": ("View",),
    "ghost_higher_floors": ("View",),
    "view_show_shade": ("View",),
    "show_animation": ("Show",),
    "show_light": ("Show",),
    "show_light_strength": ("Show",),
    "show_technical_items": ("Show",),
    "show_invalid_tiles": ("Show",),
    "show_invalid_zones": ("Show",),
    "show_creatures": ("Show",),
    "show_spawns": ("Show",),
    "show_special": ("Show",),
    "show_houses": ("Show",),
    "show_pathing": ("Show",),
    "show_towns": ("Show",),
    "show_waypoints": ("Show",),
    "highlight_items": ("Show",),
    "highlight_locked_doors": ("Show",),
    "show_wall_hooks": ("Show",),
    "goto_position": ("Navigate",),
    "goto_previous_position": ("Navigate",),
    "jump_to_brush": ("Navigate",),
    "jump_to_item": ("Navigate",),
    "window_minimap": ("Window",),
    "window_tool_options": ("Window",),
    "window_tile_properties": ("Window",),
    "window_ingame_preview": ("Window",),
    "new_palette": ("Window",),
    "select_palette_terrain": ("Window", "Palette"),
    "select_palette_doodad": ("Window", "Palette"),
    "select_palette_item": ("Window", "Palette"),
    "select_palette_collection": ("Window", "Palette"),
    "select_palette_house": ("Window", "Palette"),
    "select_palette_creature": ("Window", "Palette"),
    "select_palette_waypoint": ("Window", "Palette"),
    "select_palette_raw": ("Window", "Palette"),
    "view_toolbars_brushes": ("Window", "Toolbars"),
    "view_toolbars_position": ("Window", "Toolbars"),
    "view_toolbars_sizes": ("Window", "Toolbars"),
    "view_toolbars_standard": ("Window", "Toolbars"),
    "editor_new_view": ("Editor",),
    "editor_fullscreen": ("Editor",),
    "editor_screenshot": ("Editor",),
    "editor_zoom_in": ("Editor", "Zoom"),
    "editor_zoom_out": ("Editor", "Zoom"),
    "editor_zoom_normal": ("Editor", "Zoom"),
    "experimental_fog": ("Experimental",),
    "scripts_manager": ("Scripts",),
    "scripts_open_folder": ("Scripts",),
    "scripts_reload": ("Scripts",),
    "about_extensions": ("About",),
    "about_goto_website": ("About",),
    "about": ("About",),
}


def _build_action_specs() -> dict[str, ActionSpec]:
    specs: dict[str, ActionSpec] = {}
    for xml_id, action_key in _ACTION_KEY_BY_XML_ID.items():
        node = _XML_ACTIONS.get(xml_id)
        if node is None:
            continue
        specs[action_key] = ActionSpec(
            action_id=action_key,
            text=node.get("name", ""),
            menu_path=_MENU_PATH_BY_ACTION_KEY[action_key],
            shortcut=node.get("hotkey") or None,
            status_tip=node.get("help") or None,
        )
    return specs


PHASE1_ACTIONS: dict[str, ActionSpec] = _build_action_specs()
