from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.ui.legacy_menu_contract import LEGACY_MENUBAR_XML
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _legacy_menu(*path: str) -> ET.Element:
    current = ET.parse(LEGACY_MENUBAR_XML).getroot()
    for name in path:
        current = next(
            child
            for child in current.findall("./menu")
            if child.attrib.get("name") == name
        )
    return current


def _window_menu(window: MainWindow, *path: str) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    current = next(action.menu() for action in menu_bar.actions() if action.text() == path[0])
    assert current is not None
    for name in path[1:]:
        current = next(action.menu() for action in current.actions() if action.text() == name)
        assert current is not None
    return current


def _action_texts(menu: QMenu) -> list[str]:
    return [action.text() for action in menu.actions() if action.text()]


def _legacy_texts(menu: ET.Element) -> list[str]:
    return [
        child.attrib["name"]
        for child in menu
        if child.tag in {"item", "menu"} and child.attrib.get("name")
    ]


def _action_by_text(menu: QMenu, text: str):
    return next(action for action in menu.actions() if action.text() == text)


def test_main_window_navigate_and_window_menus_match_legacy_xml(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, "legacy-menu.ini"))
    qtbot.addWidget(window)

    assert _action_texts(_window_menu(window, "Navigate")) == _legacy_texts(
        _legacy_menu("Navigate")
    )
    assert _action_texts(_window_menu(window, "Navigate", "Floor")) == _legacy_texts(
        _legacy_menu("Navigate", "Floor")
    )

    assert _action_texts(_window_menu(window, "Window")) == _legacy_texts(_legacy_menu("Window"))
    assert _action_texts(_window_menu(window, "Window", "Palette")) == _legacy_texts(
        _legacy_menu("Window", "Palette")
    )
    assert _action_texts(_window_menu(window, "Window", "Toolbars")) == _legacy_texts(
        _legacy_menu("Window", "Toolbars")
    )


def test_main_window_navigate_and_window_shortcuts_match_legacy_xml(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, "legacy-shortcuts.ini"))
    qtbot.addWidget(window)

    navigate_menu = _window_menu(window, "Navigate")
    window_menu = _window_menu(window, "Window")
    palette_menu = _window_menu(window, "Window", "Palette")

    assert _action_by_text(navigate_menu, "Go to Previous Position").shortcut().toString() == "P"
    assert _action_by_text(navigate_menu, "Go to Position...").shortcut().toString() == "Ctrl+G"
    assert _action_by_text(navigate_menu, "Jump to Brush...").shortcut().toString() == "J"
    assert _action_by_text(navigate_menu, "Jump to Item...").shortcut().toString() == "Ctrl+J"
    assert _action_by_text(window_menu, "Minimap").shortcut().toString() == "M"
    assert _action_by_text(palette_menu, "Terrain").shortcut().toString() == "T"
    assert _action_by_text(palette_menu, "RAW").shortcut().toString() == "R"

    assert (
        _action_by_text(navigate_menu, "Go to Previous Position").statusTip()
        == "Go to the previous screen center position."
    )
    assert (
        _action_by_text(window_menu, "Tile Properties").statusTip()
        == "Displays the tile properties panel."
    )
