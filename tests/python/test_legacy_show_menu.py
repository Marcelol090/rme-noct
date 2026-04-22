from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.ui.legacy_menu_contract import (
    LEGACY_SHOW_FLAG_DEFAULTS,
    LEGACY_SHOW_MENU_SEQUENCE,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _show_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "Show")
    assert menu is not None
    return menu


def _menu_sequence(menu: QMenu) -> tuple[str | None, ...]:
    return tuple(None if action.isSeparator() else action.text() for action in menu.actions())


class _RecordingCanvas(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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
        self.view_flags = getattr(self, "view_flags", {})
        self.view_flags[name] = enabled

    def set_show_flag(self, name: str, enabled: bool) -> None:
        self.show_flags[name] = enabled


def test_legacy_show_contract_matches_xml_and_defaults() -> None:
    assert LEGACY_SHOW_MENU_SEQUENCE == (
        "Show Animation",
        "Show Light",
        "Show Light Strength",
        "Show Technical Items",
        "Show Invalid Tiles",
        "Show Invalid Zones",
        None,
        "Show creatures",
        "Show spawns",
        "Show special",
        "Show houses",
        "Show pathing",
        "Show towns",
        "Show waypoints",
        None,
        "Highlight Items",
        "Highlight Locked Doors",
        "Show Wall Hooks",
    )
    assert LEGACY_SHOW_FLAG_DEFAULTS == {
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
    assert PHASE1_ACTIONS["show_animation"].shortcut == "L"
    assert PHASE1_ACTIONS["show_light"].shortcut == "Shift+L"
    assert PHASE1_ACTIONS["show_light_strength"].shortcut == "Shift+K"
    assert PHASE1_ACTIONS["show_technical_items"].shortcut == "Shift+T"
    assert PHASE1_ACTIONS["show_creatures"].shortcut == "F"
    assert PHASE1_ACTIONS["show_spawns"].shortcut == "S"
    assert PHASE1_ACTIONS["show_special"].shortcut == "E"
    assert PHASE1_ACTIONS["show_houses"].shortcut == "Ctrl+H"
    assert PHASE1_ACTIONS["show_pathing"].shortcut == "O"
    assert PHASE1_ACTIONS["show_waypoints"].shortcut == "Shift+W"
    assert PHASE1_ACTIONS["highlight_items"].shortcut == "V"
    assert PHASE1_ACTIONS["highlight_locked_doors"].shortcut == "U"
    assert PHASE1_ACTIONS["show_wall_hooks"].shortcut == "K"


def test_main_window_show_menu_matches_legacy_order_and_defaults(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "show-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert _menu_sequence(_show_menu(window)) == LEGACY_SHOW_MENU_SEQUENCE
    for action_key, expected_checked in LEGACY_SHOW_FLAG_DEFAULTS.items():
        action = window.show_menu_actions[action_key]
        assert action.isCheckable()
        assert action.isChecked() is expected_checked
        assert action.objectName() == f"action_{action_key}"


def test_show_actions_update_canvas_seams_and_snapshot(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_RecordingCanvas] = []

    def _canvas_factory(parent=None) -> _RecordingCanvas:
        canvas = _RecordingCanvas(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "show-canvas.ini"),
        enable_docks=False,
        canvas_factory=_canvas_factory,
    )
    qtbot.addWidget(window)
    canvas = canvases[0]

    window.show_menu_actions["show_light"].trigger()
    assert canvas.show_flags["show_lights"] is True
    assert window._views[0].shell_state.show_flags["show_light"] is True

    window.show_menu_actions["show_animation"].trigger()
    assert canvas.show_flags["show_preview"] is False
    assert window._views[0].shell_state.show_flags["show_animation"] is False
