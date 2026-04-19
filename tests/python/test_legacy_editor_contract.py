"""XML-backed contract tests for the legacy Editor menu parity.

Verifies that the Editor action metadata in legacy_menu_contract.py
matches the structure defined in remeres-map-editor-redux/data/menubar.xml.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from pyrme.ui.legacy_menu_contract import (
    LEGACY_EDITOR_ITEMS,
    LEGACY_EDITOR_ZOOM_ITEMS,
    PHASE1_ACTIONS,
)

MENUBAR_XML = (
    Path(__file__).resolve().parents[2]
    / "remeres-map-editor-redux"
    / "data"
    / "menubar.xml"
)


@pytest.fixture(scope="module")
def editor_xml_element() -> ET.Element:
    """Parse the Editor menu from menubar.xml."""
    tree = ET.parse(MENUBAR_XML)
    root = tree.getroot()
    for menu in root.findall("menu"):
        if menu.get("name") == "Editor":
            return menu
    pytest.fail("Editor menu not found in menubar.xml")


# ── Structure tests ─────────────────────────────────────────────────


def test_editor_top_level_items_match_xml(editor_xml_element: ET.Element) -> None:
    """LEGACY_EDITOR_ITEMS must list the top-level Editor items in XML order."""
    xml_items = [
        item.get("name")
        for item in editor_xml_element.findall("item")
    ]
    assert list(LEGACY_EDITOR_ITEMS) == xml_items


def test_editor_zoom_submenu_matches_xml(editor_xml_element: ET.Element) -> None:
    """LEGACY_EDITOR_ZOOM_ITEMS must list the Zoom submenu items in XML order."""
    zoom_menu = None
    for sub in editor_xml_element.findall("menu"):
        if sub.get("name") == "Zoom":
            zoom_menu = sub
            break
    assert zoom_menu is not None, "Zoom submenu not found in Editor XML"
    xml_zoom_items = [item.get("name") for item in zoom_menu.findall("item")]
    assert list(LEGACY_EDITOR_ZOOM_ITEMS) == xml_zoom_items


# ── Action metadata tests ───────────────────────────────────────────


def test_editor_action_labels_match_xml(editor_xml_element: ET.Element) -> None:
    """Each Editor ActionSpec text must match the XML name attribute."""
    xml_map: dict[str, str] = {}
    for item in editor_xml_element.findall("item"):
        action = item.get("action", "")
        xml_map[action] = item.get("name", "")

    zoom_menu = editor_xml_element.find("menu[@name='Zoom']")
    assert zoom_menu is not None
    for item in zoom_menu.findall("item"):
        action = item.get("action", "")
        xml_map[action] = item.get("name", "")

    # Map XML action IDs to our ActionSpec keys
    action_id_map = {
        "NEW_VIEW": "editor_new_view",
        "TOGGLE_FULLSCREEN": "editor_fullscreen",
        "TAKE_SCREENSHOT": "editor_screenshot",
        "ZOOM_IN": "editor_zoom_in",
        "ZOOM_OUT": "editor_zoom_out",
        "ZOOM_NORMAL": "editor_zoom_normal",
    }

    for xml_action, spec_key in action_id_map.items():
        assert spec_key in PHASE1_ACTIONS, f"Missing ActionSpec for {spec_key}"
        assert PHASE1_ACTIONS[spec_key].text == xml_map[xml_action], (
            f"{spec_key}: expected '{xml_map[xml_action]}', "
            f"got '{PHASE1_ACTIONS[spec_key].text}'"
        )


def test_editor_action_shortcuts_match_xml(editor_xml_element: ET.Element) -> None:
    """Each Editor ActionSpec shortcut must match the XML hotkey attribute."""
    xml_hotkeys: dict[str, str | None] = {}
    for item in editor_xml_element.findall("item"):
        action = item.get("action", "")
        hotkey = item.get("hotkey")
        xml_hotkeys[action] = hotkey if hotkey else None

    zoom_menu = editor_xml_element.find("menu[@name='Zoom']")
    assert zoom_menu is not None
    for item in zoom_menu.findall("item"):
        action = item.get("action", "")
        hotkey = item.get("hotkey")
        xml_hotkeys[action] = hotkey if hotkey else None

    action_id_map = {
        "NEW_VIEW": "editor_new_view",
        "TOGGLE_FULLSCREEN": "editor_fullscreen",
        "TAKE_SCREENSHOT": "editor_screenshot",
        "ZOOM_IN": "editor_zoom_in",
        "ZOOM_OUT": "editor_zoom_out",
        "ZOOM_NORMAL": "editor_zoom_normal",
    }

    for xml_action, spec_key in action_id_map.items():
        expected = xml_hotkeys.get(xml_action)
        actual = PHASE1_ACTIONS[spec_key].shortcut
        assert actual == expected, (
            f"{spec_key}: expected shortcut '{expected}', got '{actual}'"
        )


def test_editor_action_status_tips_match_xml(editor_xml_element: ET.Element) -> None:
    """Each Editor ActionSpec status_tip must match the XML help attribute."""
    xml_help: dict[str, str] = {}
    for item in editor_xml_element.findall("item"):
        action = item.get("action", "")
        xml_help[action] = item.get("help", "")

    zoom_menu = editor_xml_element.find("menu[@name='Zoom']")
    assert zoom_menu is not None
    for item in zoom_menu.findall("item"):
        action = item.get("action", "")
        xml_help[action] = item.get("help", "")

    action_id_map = {
        "NEW_VIEW": "editor_new_view",
        "TOGGLE_FULLSCREEN": "editor_fullscreen",
        "TAKE_SCREENSHOT": "editor_screenshot",
        "ZOOM_IN": "editor_zoom_in",
        "ZOOM_OUT": "editor_zoom_out",
        "ZOOM_NORMAL": "editor_zoom_normal",
    }

    for xml_action, spec_key in action_id_map.items():
        expected = xml_help.get(xml_action, "")
        actual = PHASE1_ACTIONS[spec_key].status_tip
        assert actual == expected, (
            f"{spec_key}: expected help '{expected}', got '{actual}'"
        )
