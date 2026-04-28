"""Expanded XML-backed parity tests for the legacy menu shell."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

import pytest
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


def _legacy_texts(menu: ET.Element) -> list[str]:
    return [
        child.attrib["name"]
        for child in menu
        if child.tag in {"item", "menu"} and child.attrib.get("name")
    ]


def _window_menu(window: MainWindow, *path: str) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    current = next(
        action.menu() for action in menu_bar.actions() if action.text() == path[0]
    )
    assert current is not None
    for name in path[1:]:
        current = next(action.menu() for action in current.actions() if action.text() == name)
        assert current is not None
    return current


def _window_texts(menu: QMenu) -> list[str]:
    return [action.text() for action in menu.actions() if action.text()]


@pytest.mark.parametrize(
    "menu_path",
    [
        ("File",),
        ("File", "Import"),
        ("File", "Export"),
        ("File", "Reload"),
        ("Edit",),
        ("Edit", "Border Options"),
        ("Edit", "Other Options"),
        ("Editor",),
        ("Editor", "Zoom"),
        ("Search",),
        ("Map",),
        ("Selection",),
        ("Selection", "Find on Selection"),
        ("Selection", "Selection Mode"),
        ("View",),
        ("Show",),
        ("Experimental",),
        ("Scripts",),
        ("About",),
    ],
)
def test_main_window_expanded_menu_matches_legacy_xml(
    menu_path: tuple[str, ...],
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, f"{'-'.join(menu_path)}.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert _window_texts(_window_menu(window, *menu_path)) == _legacy_texts(
        _legacy_menu(*menu_path)
    )
