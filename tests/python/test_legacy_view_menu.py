from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.ui.legacy_menu_contract import (
    LEGACY_VIEW_FLAG_DEFAULTS,
    LEGACY_VIEW_MENU_SEQUENCE,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _view_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "View")
    assert menu is not None
    return menu


def _menu_sequence(menu: QMenu) -> tuple[str | None, ...]:
    return tuple(None if action.isSeparator() else action.text() for action in menu.actions())


class _RecordingCanvas(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.view_flags: dict[str, bool] = {}
        self.show_flags: dict[str, bool] = {}

    def bind_editor_context(self, context) -> None:
        self.context = context

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)

    def set_floor(self, z: int) -> None:
        self.floor = z

    def set_zoom(self, percent: int) -> None:
        self.zoom = percent

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled

    def set_view_flag(self, name: str, enabled: bool) -> None:
        self.view_flags[name] = enabled

    def set_show_flag(self, name: str, enabled: bool) -> None:
        self.show_flags[name] = enabled


def test_legacy_view_contract_matches_xml_and_defaults() -> None:
    assert LEGACY_VIEW_MENU_SEQUENCE == (
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
    assert LEGACY_VIEW_FLAG_DEFAULTS == {
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
    assert PHASE1_ACTIONS["view_show_all_floors"].shortcut == "Ctrl+W"
    assert PHASE1_ACTIONS["view_show_as_minimap"].shortcut == "Shift+E"
    assert PHASE1_ACTIONS["view_only_show_colors"].shortcut == "Ctrl+E"
    assert PHASE1_ACTIONS["view_only_show_modified"].shortcut == "Ctrl+M"
    assert PHASE1_ACTIONS["view_show_tooltips"].shortcut == "Y"
    assert PHASE1_ACTIONS["show_grid"].shortcut == "Shift+G"
    assert PHASE1_ACTIONS["view_show_client_box"].shortcut == "Shift+I"
    assert PHASE1_ACTIONS["view_ghost_loose_items"].shortcut == "G"
    assert PHASE1_ACTIONS["ghost_higher_floors"].shortcut == "Ctrl+L"
    assert PHASE1_ACTIONS["view_show_shade"].shortcut == "Q"


def test_main_window_view_menu_matches_legacy_order_and_defaults(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "view-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert _menu_sequence(_view_menu(window)) == LEGACY_VIEW_MENU_SEQUENCE
    for action_key, expected_checked in LEGACY_VIEW_FLAG_DEFAULTS.items():
        action = window.view_menu_actions[action_key]
        assert action.isCheckable()
        assert action.isChecked() is expected_checked
        assert action.objectName() == f"action_{action_key}"


def test_view_actions_update_canvas_seams(qtbot, settings_workspace: Path) -> None:
    canvases: list[_RecordingCanvas] = []

    def _canvas_factory(parent=None) -> _RecordingCanvas:
        canvas = _RecordingCanvas(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "view-canvas.ini"),
        enable_docks=False,
        canvas_factory=_canvas_factory,
    )
    qtbot.addWidget(window)
    canvas = canvases[0]

    window.show_grid_action.trigger()
    assert canvas.show_grid is True

    window.ghost_higher_action.trigger()
    assert canvas.ghost_higher is True

    window.view_menu_actions["view_show_as_minimap"].trigger()
    assert canvas.view_flags["show_as_minimap"] is True

    window.view_menu_actions["view_show_all_floors"].trigger()
    assert canvas.view_flags["show_all_floors"] is False
    assert window._views[0].shell_state.view_flags["view_show_all_floors"] is False
