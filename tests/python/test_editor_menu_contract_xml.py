from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from pyrme.ui.legacy_menu_contract import (
    EDITOR_ACTION_ORDER,
    EDITOR_ACTIONS,
    EDITOR_ZOOM_ACTION_ORDER,
    EDITOR_ZOOM_MENU_TITLE,
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


def _editor_menu(root: ET.Element) -> ET.Element:
    menu = root.find("./menu[@name='Editor']")
    assert menu is not None
    return menu


def _menu_children(menu: ET.Element) -> list[ET.Element]:
    return list(menu)


def _action_child_names(menu: ET.Element) -> tuple[str, ...]:
    return tuple(child.attrib["action"] for child in menu if child.tag == "item")


def _child_menu(menu: ET.Element, name: str) -> ET.Element:
    child = menu.find(f"./menu[@name='{name}']")
    assert child is not None
    return child


def _child_item(menu: ET.Element, action_name: str) -> ET.Element:
    child = menu.find(f"./item[@action='{action_name}']")
    assert child is not None
    return child


def _find_action(
    menu: ET.Element, action_name: str, path: tuple[str, ...]
) -> tuple[ET.Element, tuple[str, ...]] | None:
    for child in menu:
        if child.tag == "item" and child.attrib.get("action") == action_name:
            return child, path
        if child.tag == "menu":
            found = _find_action(child, action_name, (*path, child.attrib["name"]))
            if found is not None:
                return found
    return None


def _xml_menu_path(root: ET.Element, action_name: str) -> tuple[str, ...]:
    editor_menu = _editor_menu(root)
    found = _find_action(editor_menu, action_name, ("Editor",))
    assert found is not None
    _, menu_path = found
    return menu_path


def test_editor_menu_exists_and_keeps_legacy_order() -> None:
    root = _legacy_menu_root()
    editor_menu = _editor_menu(root)

    assert editor_menu.attrib["name"] == "Editor"
    assert _action_child_names(editor_menu) == tuple(
        EDITOR_ACTIONS[action_key].action_id.upper() for action_key in EDITOR_ACTION_ORDER
    )
    assert [child.tag for child in _menu_children(editor_menu)] == [
        "item",
        "item",
        "item",
        "separator",
        "menu",
    ]


def test_editor_zoom_submenu_matches_legacy_xml() -> None:
    root = _legacy_menu_root()
    editor_menu = _editor_menu(root)
    zoom_menu = _child_menu(editor_menu, EDITOR_ZOOM_MENU_TITLE)

    assert zoom_menu.attrib["name"] == EDITOR_ZOOM_MENU_TITLE
    assert tuple(child.attrib["action"] for child in zoom_menu if child.tag == "item") == tuple(
        EDITOR_ACTIONS[action_key].action_id.upper()
        for action_key in EDITOR_ZOOM_ACTION_ORDER
    )


def test_editor_action_metadata_matches_legacy_xml() -> None:
    root = _legacy_menu_root()
    editor_menu = _editor_menu(root)
    zoom_menu = _child_menu(editor_menu, EDITOR_ZOOM_MENU_TITLE)

    new_view = _child_item(editor_menu, "NEW_VIEW")
    toggle_fullscreen = _child_item(editor_menu, "TOGGLE_FULLSCREEN")
    take_screenshot = _child_item(editor_menu, "TAKE_SCREENSHOT")
    zoom_in = _child_item(zoom_menu, "ZOOM_IN")
    zoom_out = _child_item(zoom_menu, "ZOOM_OUT")
    zoom_normal = _child_item(zoom_menu, "ZOOM_NORMAL")

    assert new_view.attrib["name"] == EDITOR_ACTIONS["new_view"].text
    assert new_view.attrib["help"] == EDITOR_ACTIONS["new_view"].status_tip
    assert new_view.attrib["hotkey"] == EDITOR_ACTIONS["new_view"].shortcut
    assert EDITOR_ACTIONS["new_view"].menu_path == _xml_menu_path(root, "NEW_VIEW")

    assert toggle_fullscreen.attrib["name"] == EDITOR_ACTIONS["toggle_fullscreen"].text
    assert toggle_fullscreen.attrib["help"] == EDITOR_ACTIONS["toggle_fullscreen"].status_tip
    assert toggle_fullscreen.attrib["hotkey"] == EDITOR_ACTIONS["toggle_fullscreen"].shortcut
    assert EDITOR_ACTIONS["toggle_fullscreen"].menu_path == _xml_menu_path(
        root, "TOGGLE_FULLSCREEN"
    )

    assert take_screenshot.attrib["name"] == EDITOR_ACTIONS["take_screenshot"].text
    assert take_screenshot.attrib["help"] == EDITOR_ACTIONS["take_screenshot"].status_tip
    assert take_screenshot.attrib["hotkey"] == EDITOR_ACTIONS["take_screenshot"].shortcut
    assert EDITOR_ACTIONS["take_screenshot"].menu_path == _xml_menu_path(
        root, "TAKE_SCREENSHOT"
    )

    assert zoom_in.attrib["name"] == EDITOR_ACTIONS["zoom_in"].text
    assert zoom_in.attrib["help"] == EDITOR_ACTIONS["zoom_in"].status_tip
    assert zoom_in.attrib["hotkey"] == EDITOR_ACTIONS["zoom_in"].shortcut
    assert EDITOR_ACTIONS["zoom_in"].menu_path == _xml_menu_path(root, "ZOOM_IN")

    assert zoom_out.attrib["name"] == EDITOR_ACTIONS["zoom_out"].text
    assert zoom_out.attrib["help"] == EDITOR_ACTIONS["zoom_out"].status_tip
    assert zoom_out.attrib["hotkey"] == EDITOR_ACTIONS["zoom_out"].shortcut
    assert EDITOR_ACTIONS["zoom_out"].menu_path == _xml_menu_path(root, "ZOOM_OUT")

    assert zoom_normal.attrib["name"] == EDITOR_ACTIONS["zoom_normal"].text
    assert zoom_normal.attrib["help"] == EDITOR_ACTIONS["zoom_normal"].status_tip
    assert zoom_normal.attrib["hotkey"] == EDITOR_ACTIONS["zoom_normal"].shortcut
    assert EDITOR_ACTIONS["zoom_normal"].menu_path == _xml_menu_path(root, "ZOOM_NORMAL")
