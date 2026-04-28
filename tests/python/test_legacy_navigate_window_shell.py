from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

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


def test_legacy_navigate_menu_actions_drive_shell_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    class _GotoDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def get_position(self) -> tuple[int, int, int]:
            return (32123, 32234, 6)

    window = MainWindow(
        settings=_build_settings(settings_workspace, "navigate-shell.ini"),
        goto_dialog_factory=_GotoDialog,
    )
    qtbot.addWidget(window)

    navigate_menu = _menu(window, "Navigate")
    floor_menu = _submenu(navigate_menu, "Floor")

    _action(navigate_menu, "Go to Position...").trigger()
    assert window._coord_label.text() == "Pos: (X: 32123, Y: 32234, Z: 06)"
    assert window._previous_position == (32000, 32000, 7)

    _action(navigate_menu, "Go to Previous Position").trigger()
    assert window._coord_label.text() == "Pos: (X: 32000, Y: 32000, Z: 07)"

    _action(floor_menu, "Floor 3").trigger()
    assert window._coord_label.text() == "Pos: (X: 32000, Y: 32000, Z: 03)"
    assert window.floor_actions[3].isChecked()
    assert window.minimap_dock is not None
    assert window.minimap_dock.pos_label.text() == "Z: 03"


def test_legacy_window_menu_actions_toggle_surfaces_and_palettes(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, "window-shell.ini"))
    qtbot.addWidget(window)

    assert window.brush_palette_dock is not None
    assert window.tool_options_dock is not None
    assert window.minimap_dock is not None
    assert window.properties_dock is not None
    assert window.ingame_preview_dock is not None
    assert window.sizes_toolbar is not None

    window_menu = _menu(window, "Window")
    palette_menu = _submenu(window_menu, "Palette")
    toolbars_menu = _submenu(window_menu, "Toolbars")

    _action(window_menu, "Minimap").trigger()
    assert window.minimap_dock.isHidden() is True
    _action(window_menu, "Minimap").trigger()
    assert window.minimap_dock.isHidden() is False

    _action(window_menu, "Tool Options").trigger()
    assert window.tool_options_dock.isHidden() is True

    _action(window_menu, "Tile Properties").trigger()
    assert window.properties_dock.isHidden() is True

    _action(window_menu, "In-game Preview").trigger()
    assert window.ingame_preview_dock.isHidden() is True

    _action(window_menu, "New Palette").trigger()
    assert window.brush_palette_dock.isHidden() is False
    assert (
        window.statusBar().currentMessage()
        == "New Palette reuses the shared palette dock in this slice."
    )

    _action(palette_menu, "RAW").trigger()
    assert window.brush_palette_dock.current_palette() == "RAW"
    assert window.statusBar().currentMessage() == "Palette switched to RAW."

    _action(toolbars_menu, "Sizes").trigger()
    assert window.sizes_toolbar.isHidden() is True
