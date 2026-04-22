"""Shell-wiring tests for the legacy Editor menu parity.

Verifies that the Editor menu in MainWindow is properly wired
with actions for New View, Enter Fullscreen, Take Screenshot,
and the Zoom submenu (Zoom In, Zoom Out, Zoom Normal).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _menu(window: MainWindow, title: str) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == title)
    assert menu is not None
    return menu


def _submenu(menu: QMenu, title: str) -> QMenu:
    submenu = next(action.menu() for action in menu.actions() if action.text() == title)
    assert submenu is not None
    return submenu


def _action(menu: QMenu, text: str):
    return next(action for action in menu.actions() if action.text() == text)


def test_editor_menu_exists_with_correct_actions(
    qtbot,
    settings_workspace: Path,
) -> None:
    """Editor menu must contain New View, Enter Fullscreen, Take Screenshot,
    and a Zoom submenu with Zoom In, Zoom Out, Zoom Normal."""
    window = MainWindow(
        settings=_build_settings(settings_workspace, "editor-shell.ini"),
    )
    qtbot.addWidget(window)

    editor_menu = _menu(window, "Editor")
    action_texts = [a.text() for a in editor_menu.actions() if not a.isSeparator()]

    assert "New View" in action_texts
    assert "Enter Fullscreen" in action_texts
    assert "Take Screenshot" in action_texts

    # Zoom submenu must exist
    zoom_menu = _submenu(editor_menu, "Zoom")
    zoom_texts = [a.text() for a in zoom_menu.actions() if not a.isSeparator()]
    assert zoom_texts == ["Zoom In", "Zoom Out", "Zoom Normal"]


def test_editor_fullscreen_toggle_changes_window_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    """Enter Fullscreen action must toggle the window state."""
    window = MainWindow(
        settings=_build_settings(settings_workspace, "editor-fullscreen.ini"),
    )
    qtbot.addWidget(window)

    editor_menu = _menu(window, "Editor")
    fullscreen_action = _action(editor_menu, "Enter Fullscreen")

    assert window.isFullScreen() is False
    fullscreen_action.trigger()
    assert window.isFullScreen() is True
    fullscreen_action.trigger()
    assert window.isFullScreen() is False


def test_editor_zoom_actions_modify_zoom_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    """Zoom In/Out/Normal actions must modify the shell zoom state."""
    window = MainWindow(
        settings=_build_settings(settings_workspace, "editor-zoom.ini"),
    )
    qtbot.addWidget(window)

    editor_menu = _menu(window, "Editor")
    zoom_menu = _submenu(editor_menu, "Zoom")

    assert window._zoom_percent == 100

    _action(zoom_menu, "Zoom In").trigger()
    assert window._zoom_percent > 100

    _action(zoom_menu, "Zoom Out").trigger()
    _action(zoom_menu, "Zoom Out").trigger()
    assert window._zoom_percent < 100

    _action(zoom_menu, "Zoom Normal").trigger()
    assert window._zoom_percent == 100


def test_editor_new_view_opens_view_and_screenshot_shows_gap_message(
    qtbot,
    settings_workspace: Path,
) -> None:
    """New View must open a shared view; Take Screenshot remains a backend gap."""
    window = MainWindow(
        settings=_build_settings(settings_workspace, "editor-gaps.ini"),
    )
    qtbot.addWidget(window)

    editor_menu = _menu(window, "Editor")

    _action(editor_menu, "New View").trigger()
    assert window.statusBar() is not None
    assert window._view_tabs.count() == 2
    assert "opened a new view" in window.statusBar().currentMessage().lower()

    _action(editor_menu, "Take Screenshot").trigger()
    assert "not available" in window.statusBar().currentMessage().lower()


def test_editor_action_object_names_follow_convention(
    qtbot,
    settings_workspace: Path,
) -> None:
    """All Editor actions must follow the action_{id} object name convention."""
    window = MainWindow(
        settings=_build_settings(settings_workspace, "editor-names.ini"),
    )
    qtbot.addWidget(window)

    expected_names = {
        "action_editor_new_view",
        "action_editor_fullscreen",
        "action_editor_screenshot",
        "action_editor_zoom_in",
        "action_editor_zoom_out",
        "action_editor_zoom_normal",
    }

    editor_menu = _menu(window, "Editor")
    zoom_menu = _submenu(editor_menu, "Zoom")

    found_names = set()
    for action in editor_menu.actions():
        if not action.isSeparator() and action.menu() is None:
            found_names.add(action.objectName())
    for action in zoom_menu.actions():
        if not action.isSeparator():
            found_names.add(action.objectName())

    assert expected_names.issubset(found_names), (
        f"Missing: {expected_names - found_names}"
    )
