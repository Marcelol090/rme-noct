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


def _find_action(
    menu: ET.Element, action_name: str, path: tuple[str, ...]
) -> tuple[ET.Element, tuple[str, ...]] | None:
    for child in menu:
        if child.tag == "item" and child.attrib.get("action") == action_name:
            return child, path
        if child.tag == "menu":
            found = _find_action(
                child,
                action_name,
                (*path, child.attrib["name"]),
            )
            if found is not None:
                return found
    return None


def _action_metadata(root: ET.Element, action_name: str) -> tuple[str, str, str, tuple[str, ...]]:
    for menu in root.findall("./menu"):
        found = _find_action(menu, action_name, (menu.attrib["name"],))
        if found is None:
            continue

        action, menu_path = found
        return (
            action.attrib["name"],
            action.attrib.get("help", ""),
            action.attrib.get("hotkey", ""),
            menu_path,
        )

    raise AssertionError(f"Could not find XML action {action_name!r}")


def _normalize_label(text: str) -> str:
    return text.replace("&", "")


def test_legacy_top_level_menu_order_matches_xml() -> None:
    root = _legacy_menu_root()

    assert _top_level_menu_names(root) == LEGACY_TOP_LEVEL_MENUS


@pytest.mark.parametrize("xml_action_name,spec_key", PHASE1_SHORTCUT_ACTIONS)
def test_phase1_shortcuts_match_xml(xml_action_name: str, spec_key: str) -> None:
    root = _legacy_menu_root()

    _, _, shortcut, _ = _action_metadata(root, xml_action_name)

    assert PHASE1_ACTIONS[spec_key].shortcut == shortcut


@pytest.mark.parametrize("xml_action_name,spec_key", PHASE1_SHORTCUT_ACTIONS)
def test_phase1_contract_metadata_matches_xml(xml_action_name: str, spec_key: str) -> None:
    root = _legacy_menu_root()
    xml_name, xml_help, _, xml_menu_path = _action_metadata(root, xml_action_name)
    action = PHASE1_ACTIONS[spec_key]

    assert _normalize_label(action.text) == xml_name
    assert action.status_tip == xml_help
    assert action.menu_path == xml_menu_path
