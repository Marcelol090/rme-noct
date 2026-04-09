"""Milestone 5 widget tests for menu commands, shortcuts, and status feedback."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

from pyrme.ui.legacy_menu_contract import PHASE1_ACTIONS
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtGui import QAction


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _shortcut(action: QAction) -> str:
    return action.shortcut().toString()


def _status_message(window: MainWindow) -> str:
    status_bar = window.statusBar()
    assert status_bar is not None
    return status_bar.currentMessage()


def test_main_window_exposes_legacy_navigation_shortcuts_and_status_tips(
    qtbot,
    tmp_path: Path,
) -> None:
    window = MainWindow(settings=_build_settings(tmp_path, "commands.ini"))
    qtbot.addWidget(window)

    assert _shortcut(window.find_item_action) == PHASE1_ACTIONS["find_item"].shortcut
    assert _shortcut(window.replace_items_action) == PHASE1_ACTIONS["replace_items"].shortcut
    assert _shortcut(window.map_properties_action) == PHASE1_ACTIONS["map_properties"].shortcut
    assert _shortcut(window.map_statistics_action) == PHASE1_ACTIONS["map_statistics"].shortcut
    assert _shortcut(window.goto_position_action) == PHASE1_ACTIONS["goto_position"].shortcut
    assert (
        _shortcut(window.goto_previous_position_action)
        == PHASE1_ACTIONS["goto_previous_position"].shortcut
    )
    assert _shortcut(window.jump_to_brush_action) == PHASE1_ACTIONS["jump_to_brush"].shortcut
    assert _shortcut(window.jump_to_item_action) == PHASE1_ACTIONS["jump_to_item"].shortcut
    assert _shortcut(window.ghost_higher_action) == PHASE1_ACTIONS["ghost_higher_floors"].shortcut
    assert _shortcut(window.show_grid_action) == PHASE1_ACTIONS["show_grid"].shortcut

    assert window.find_item_action.statusTip() == PHASE1_ACTIONS["find_item"].status_tip
    assert window.replace_items_action.statusTip() == PHASE1_ACTIONS["replace_items"].status_tip
    assert window.map_properties_action.statusTip() == PHASE1_ACTIONS["map_properties"].status_tip
    assert window.map_statistics_action.statusTip() == PHASE1_ACTIONS["map_statistics"].status_tip
    assert window.goto_position_action.statusTip() == PHASE1_ACTIONS["goto_position"].status_tip
    assert (
        window.goto_previous_position_action.statusTip()
        == PHASE1_ACTIONS["goto_previous_position"].status_tip
    )
    assert window.jump_to_brush_action.statusTip() == PHASE1_ACTIONS["jump_to_brush"].status_tip
    assert window.jump_to_item_action.statusTip() == PHASE1_ACTIONS["jump_to_item"].status_tip
    assert window.show_grid_action.statusTip() == PHASE1_ACTIONS["show_grid"].status_tip
    assert (
        window.ghost_higher_action.statusTip()
        == PHASE1_ACTIONS["ghost_higher_floors"].status_tip
    )


def test_main_window_previous_position_swaps_single_history_slot(
    qtbot,
    tmp_path: Path,
) -> None:
    class _GotoDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def get_position(self) -> tuple[int, int, int]:
            return (32123, 32234, 6)

    window = MainWindow(
        settings=_build_settings(tmp_path, "previous.ini"),
        goto_dialog_factory=_GotoDialog,
    )
    qtbot.addWidget(window)

    window._show_goto_position()
    assert window._coord_label.text() == "Pos: (X: 32123, Y: 32234, Z: 06)"
    assert _status_message(window) == "Navigation focus moved to 32123, 32234, 06"

    window.goto_previous_position_action.trigger()
    assert window._coord_label.text() == "Pos: (X: 32000, Y: 32000, Z: 07)"
    assert _status_message(window) == "Returned to previous position 32000, 32000, 07"

    window.goto_previous_position_action.trigger()
    assert window._coord_label.text() == "Pos: (X: 32123, Y: 32234, Z: 06)"
    assert _status_message(window) == "Returned to previous position 32123, 32234, 06"


def test_main_window_stub_navigation_commands_report_status(
    qtbot,
    tmp_path: Path,
) -> None:
    window = MainWindow(settings=_build_settings(tmp_path, "status.ini"))
    qtbot.addWidget(window)

    window.goto_previous_position_action.trigger()
    assert _status_message(window) == "No previous position stored."

    window.jump_to_brush_action.trigger()
    assert _status_message(window) == "Jump to Brush is not available yet."

    window.jump_to_item_action.trigger()
    assert _status_message(window) == "Jump to Item is not available yet."
