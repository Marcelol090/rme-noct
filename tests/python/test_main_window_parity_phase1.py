"""Phase 1 XML-backed parity audit for the legacy menu shell."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from pyrme.ui.legacy_menu_contract import LEGACY_TOP_LEVEL_MENUS, PHASE1_ACTIONS

PHASE1_SHORTCUT_ACTIONS = (
    ("FIND_ITEM", "find_item"),
    ("REPLACE_ITEMS", "replace_items"),
    ("MAP_PROPERTIES", "map_properties"),
    ("MAP_STATISTICS", "map_statistics"),
    ("GOTO_PREVIOUS_POSITION", "goto_previous_position"),
    ("GOTO_POSITION", "goto_position"),
    ("JUMP_TO_BRUSH", "jump_to_brush"),
    ("JUMP_TO_ITEM_BRUSH", "jump_to_item"),
    ("SHOW_GRID", "show_grid"),
    ("GHOST_HIGHER_FLOORS", "ghost_higher_floors"),
)


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "remeres-map-editor-redux" / "data" / "menubar.xml"
        if candidate.exists():
            return parent
    raise AssertionError("Could not locate remeres-map-editor-redux/data/menubar.xml")


def _legacy_menu_root() -> ET.Element:
    menubar_xml = _repo_root() / "remeres-map-editor-redux" / "data" / "menubar.xml"
    return ET.parse(menubar_xml).getroot()


def _top_level_menu_names(root: ET.Element) -> tuple[str, ...]:
    return tuple(menu.attrib["name"] for menu in root.findall("./menu"))


def _shortcut_for_action(root: ET.Element, action_name: str) -> str:
    for menu in root.findall(".//menu"):
        for item in menu:
            if item.tag == "item" and item.attrib.get("action") == action_name:
                return item.attrib.get("hotkey", "")
    raise AssertionError(f"Could not find XML action {action_name!r}")


def test_legacy_top_level_menu_order_matches_xml() -> None:
    root = _legacy_menu_root()

    assert _top_level_menu_names(root) == LEGACY_TOP_LEVEL_MENUS


@pytest.mark.parametrize("xml_action_name,spec_key", PHASE1_SHORTCUT_ACTIONS)
def test_phase1_shortcuts_match_xml(xml_action_name: str, spec_key: str) -> None:
    root = _legacy_menu_root()

    assert PHASE1_ACTIONS[spec_key].shortcut == _shortcut_for_action(root, xml_action_name)
