"""Milestone 5 widget tests for menu commands, shortcuts, and status feedback."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

from pyrme.ui.dialogs import FindItemQuery
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
    class _CancelDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Rejected)

        def selected_result(self):
            return None

        def last_search_map_query(self):
            return None

    window = MainWindow(
        settings=_build_settings(tmp_path, "status.ini"),
        jump_to_brush_dialog_factory=_CancelDialog,
        jump_to_item_dialog_factory=_CancelDialog,
    )
    qtbot.addWidget(window)

    window.goto_previous_position_action.trigger()
    assert _status_message(window) == "No previous position stored."

    window.jump_to_brush_action.trigger()
    assert window._active_brush_id is None
    assert window._active_item_id is None

    window.jump_to_item_action.trigger()
    assert window._active_brush_id is None
    assert window._active_item_id is None


def test_main_window_find_item_selection_updates_session_state(
    qtbot,
    tmp_path: Path,
) -> None:
    class _FindItemDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def selected_result(self):
            class _Result:
                name = "Gold Coin"
                server_id = 2148

            return _Result()

    window = MainWindow(
        settings=_build_settings(tmp_path, "find-item-selection.ini"),
        find_item_dialog_factory=_FindItemDialog,
    )
    qtbot.addWidget(window)

    window._show_find_item()

    assert window._active_brush_name == "Gold Coin"
    assert window._editor_context.session.active_item_id == 2148
    assert window._editor_context.session.active_brush_id == "item:2148"
    assert _status_message(window) == "Selected item Gold Coin (#2148)."


def test_main_window_jump_to_item_action_updates_session_state(
    qtbot,
    tmp_path: Path,
) -> None:
    class _JumpToItemDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def selected_result(self):
            class _Result:
                name = "Gold Coin"
                server_id = 2148

            return _Result()

    window = MainWindow(
        settings=_build_settings(tmp_path, "jump-to-item-selection.ini"),
        jump_to_item_dialog_factory=_JumpToItemDialog,
    )
    qtbot.addWidget(window)

    window.jump_to_item_action.trigger()

    assert window._active_brush_name == "Gold Coin"
    assert window._editor_context.session.active_item_id == 2148
    assert window._editor_context.session.active_brush_id == "item:2148"
    assert _status_message(window) == "Selected item Gold Coin (#2148)."


def test_main_window_jump_to_item_reports_search_map_gap(
    qtbot,
    tmp_path: Path,
) -> None:
    class _JumpToItemDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Rejected)

        def selected_result(self):
            return None

        def last_search_map_query(self):
            return FindItemQuery(search_text="coin")

    window = MainWindow(
        settings=_build_settings(tmp_path, "jump-to-item-search-map.ini"),
        jump_to_item_dialog_factory=_JumpToItemDialog,
    )
    qtbot.addWidget(window)

    window.jump_to_item_action.trigger()

    assert _status_message(window) == "Search on map for 'coin' is not available yet."


def test_main_window_jump_to_brush_action_selects_palette_result(
    qtbot,
    tmp_path: Path,
) -> None:
    class _JumpToBrushDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def selected_result(self):
            class _Result:
                kind = "palette"
                name = "RAW"
                palette_name = "RAW"

            return _Result()

    window = MainWindow(
        settings=_build_settings(tmp_path, "jump-to-brush-palette.ini"),
        jump_to_brush_dialog_factory=_JumpToBrushDialog,
    )
    qtbot.addWidget(window)

    window.jump_to_brush_action.trigger()

    assert window.brush_palette_dock is not None
    assert window.brush_palette_dock.current_palette() == "RAW"
    assert window._editor_context.session.active_brush_id == "palette:raw"
    assert window._editor_context.session.active_item_id is None
    assert _status_message(window) == "Palette switched to RAW."


def test_main_window_jump_to_brush_action_selects_item_result(
    qtbot,
    tmp_path: Path,
) -> None:
    class _JumpToBrushDialog:
        def __init__(self, parent=None) -> None:
            self.parent = parent

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def selected_result(self):
            class _Result:
                kind = "item"
                name = "Stone"
                item_id = 1

            return _Result()

    window = MainWindow(
        settings=_build_settings(tmp_path, "jump-to-brush-item.ini"),
        jump_to_brush_dialog_factory=_JumpToBrushDialog,
    )
    qtbot.addWidget(window)

    window.jump_to_brush_action.trigger()

    assert window._active_brush_name == "Stone"
    assert window._editor_context.session.active_item_id == 1
    assert window._editor_context.session.active_brush_id == "item:1"
    assert _status_message(window) == "Selected item Stone (#1)."


def test_main_window_brush_mode_toolbar_updates_session_and_tool_options(
    qtbot,
    tmp_path: Path,
) -> None:
    window = MainWindow(settings=_build_settings(tmp_path, "brush-mode.ini"))
    qtbot.addWidget(window)

    assert window.tool_options_dock is not None
    assert window._editor_context.session.mode == "drawing"
    assert window.brush_mode_actions["drawing"].isChecked()
    assert window.tool_options_dock._mode_label.text() == "Draw"

    window.brush_mode_actions["selection"].trigger()

    assert window._editor_context.session.mode == "selection"
    assert window.brush_mode_actions["selection"].isChecked()
    assert not window.brush_mode_actions["drawing"].isChecked()
    assert window.tool_options_dock._mode_label.text() == "Select"
    assert _status_message(window) == "Editor mode: Select."


def test_main_window_unknown_brush_mode_falls_back_to_drawing(
    qtbot,
    tmp_path: Path,
) -> None:
    window = MainWindow(settings=_build_settings(tmp_path, "brush-mode-fallback.ini"))
    qtbot.addWidget(window)

    window._editor_context.session.mode = "unknown"
    window._sync_canvas_shell_state()

    assert window._editor_context.session.mode == "drawing"
    assert window.tool_options_dock is not None
    assert window.brush_mode_actions["drawing"].isChecked()
    assert window.tool_options_dock._mode_label.text() == "Draw"
