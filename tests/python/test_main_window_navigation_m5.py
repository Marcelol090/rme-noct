"""Milestone 5 widget tests for MainWindow shell navigation behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

import pyrme.ui.main_window as main_window_module
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _status_message(window: MainWindow) -> str:
    status_bar = window.statusBar()
    assert status_bar is not None
    return status_bar.currentMessage()


def _setting_bool(settings: QSettings, key: str, default: bool = False) -> bool:
    raw = settings.value(key, default)
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def test_main_window_goto_position_updates_shell_state(
    qtbot,
    monkeypatch,
    tmp_path: Path,
) -> None:
    class _PositionInput:
        def set_position(self, *_args) -> None:
            pass

    class _FakeGotoDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent
            self.position_input = _PositionInput()

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def get_position(self) -> tuple[int, int, int]:
            return (32123, 32234, 6)

    monkeypatch.setattr(main_window_module, "GotoPositionDialog", _FakeGotoDialog)

    window = MainWindow(settings=_build_settings(tmp_path, "goto.ini"), enable_docks=True)
    qtbot.addWidget(window)

    window._show_goto_position()

    assert window._coord_label.text() == "Pos: (X: 32123, Y: 32234, Z: 06)"
    assert window._floor_label.text() == "Floor 6 (Above Ground)"
    assert window._position == (32123, 32234, 6)
    assert window.goto_previous_position_action.isEnabled() is True
    assert window.floor_actions[6].isChecked()
    assert not window.floor_actions[7].isChecked()
    assert window.minimap_dock.pos_label.text() == "Z: 06"
    assert _status_message(window) == "Navigation focus moved to 32123, 32234, 06"


def test_main_window_floor_navigation_and_visibility_actions_drive_shell_state(
    qtbot,
    tmp_path: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(tmp_path, "navigation.ini"),
        enable_docks=True,
    )
    qtbot.addWidget(window)

    assert window.toggle_minimap_action is not None
    assert window.toggle_brush_palette_action is not None
    assert window.toggle_properties_action is not None
    assert window.toggle_waypoints_action is not None
    assert window.toggle_brushes_toolbar_action is not None
    assert window.toggle_position_toolbar_action is not None
    assert window.toggle_floor_toolbar_action is not None
    assert window.toggle_sizes_toolbar_action is not None
    assert window.toggle_standard_toolbar_action is not None

    assert window.show_lower_action.isCheckable()
    assert window.show_lower_action.isChecked() is True
    assert window.show_grid_action.isCheckable()
    assert window.ghost_higher_action.isCheckable()

    assert window.floor_actions[7].isChecked()

    window.floor_up_action.trigger()
    assert window.floor_actions[6].isChecked()
    assert window._coord_label.text() == "Pos: (X: 32000, Y: 32000, Z: 06)"
    assert window._floor_label.text() == "Floor 6 (Above Ground)"
    assert window.minimap_dock.pos_label.text() == "Z: 06"

    window.minimap_dock.z_down_btn.click()
    assert window.floor_actions[7].isChecked()
    assert window.minimap_dock.pos_label.text() == "Z: 07"

    minimap_checked = window.toggle_minimap_action.isChecked()
    window.toggle_minimap_action.trigger()
    assert window.toggle_minimap_action.isChecked() is not minimap_checked

    floor_toolbar_checked = window.toggle_floor_toolbar_action.isChecked()
    window.toggle_floor_toolbar_action.trigger()
    assert window.toggle_floor_toolbar_action.isChecked() is not floor_toolbar_checked

    show_lower_checked = window.show_lower_action.isChecked()
    window.show_lower_action.trigger()
    assert window.show_lower_action.isChecked() is not show_lower_checked


def test_main_window_persists_shell_state_with_qsettings(
    qtbot,
    tmp_path: Path,
) -> None:
    settings_path = tmp_path / "main_window.ini"

    settings = QSettings(str(settings_path), QSettings.Format.IniFormat)
    window = MainWindow(settings=settings, enable_docks=True)
    qtbot.addWidget(window)

    assert window.toggle_waypoints_action is not None
    assert window.toggle_floor_toolbar_action is not None

    window.floor_down_action.trigger()
    window.show_grid_action.trigger()
    window.ghost_higher_action.trigger()
    window.show_lower_action.trigger()
    window.toggle_waypoints_action.trigger()
    window.toggle_floor_toolbar_action.trigger()
    window.close()

    saved = QSettings(str(settings_path), QSettings.Format.IniFormat)
    assert saved.value("main_window/geometry") is not None
    assert saved.value("main_window/state") is not None
    assert int(str(saved.value("main_window/current_x"))) == 32000
    assert int(str(saved.value("main_window/current_y"))) == 32000
    assert int(str(saved.value("main_window/current_z"))) == 8
    assert _setting_bool(saved, "main_window/show_grid") is True
    assert _setting_bool(saved, "main_window/ghost_higher") is True
    assert _setting_bool(saved, "main_window/show_lower", True) is False

    restored_settings = QSettings(str(settings_path), QSettings.Format.IniFormat)
    restored = MainWindow(settings=restored_settings, enable_docks=True)
    qtbot.addWidget(restored)

    assert restored.floor_actions[8].isChecked()
    assert restored.ghost_higher_action.isChecked() is True
    assert restored.show_grid_action.isChecked() is True
    assert restored.show_lower_action.isChecked() is False
    assert restored.toggle_waypoints_action is not None
    assert restored.toggle_waypoints_action.isChecked() is False
    assert restored.toggle_floor_toolbar_action is not None
    assert restored.toggle_floor_toolbar_action.isChecked() is False
