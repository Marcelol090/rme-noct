from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.editor.model import EditorModel, MapPosition, TileState
from pyrme.ui.legacy_menu_contract import (
    LEGACY_EDIT_BORDER_ITEMS,
    LEGACY_EDIT_MENU_SEQUENCE,
    LEGACY_EDIT_OTHER_ITEMS,
    LEGACY_EDIT_STATE_DEFAULTS,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _edit_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "Edit")
    assert menu is not None
    return menu


def _submenu(menu: QMenu, name: str) -> QMenu:
    submenu = next(action.menu() for action in menu.actions() if action.text() == name)
    assert submenu is not None
    return submenu


def _menu_sequence(menu: QMenu) -> tuple[str | None, ...]:
    return tuple(None if action.isSeparator() else action.text() for action in menu.actions())


def _status_message(window: MainWindow) -> str:
    status_bar = window.statusBar()
    assert status_bar is not None
    return status_bar.currentMessage()


def test_legacy_edit_contract_matches_xml_and_defaults() -> None:
    assert LEGACY_EDIT_MENU_SEQUENCE == (
        "Undo",
        "Redo",
        None,
        "Replace Items...",
        None,
        "Border Options",
        "Other Options",
        None,
        "Cut",
        "Copy",
        "Paste",
    )
    assert LEGACY_EDIT_BORDER_ITEMS == (
        "Border Automagic",
        None,
        "Borderize Selection",
        "Borderize Map",
        "Randomize Selection",
        "Randomize Map",
    )
    assert LEGACY_EDIT_OTHER_ITEMS == (
        "Remove Items by ID...",
        "Remove all Corpses...",
        "Remove all Unreachable Tiles...",
        "Clear Invalid Houses",
        "Clear Modified State",
    )
    assert LEGACY_EDIT_STATE_DEFAULTS == {"border_automagic": True}
    assert PHASE1_ACTIONS["edit_undo"].shortcut == "Ctrl+Z"
    assert PHASE1_ACTIONS["edit_redo"].shortcut == "Ctrl+Shift+Z"
    assert PHASE1_ACTIONS["border_automagic"].shortcut == "A"
    assert PHASE1_ACTIONS["borderize_selection"].shortcut == "Ctrl+B"
    assert PHASE1_ACTIONS["remove_items_by_id"].shortcut == "Ctrl+Shift+R"
    assert PHASE1_ACTIONS["edit_cut"].shortcut == "Ctrl+X"
    assert PHASE1_ACTIONS["edit_copy"].shortcut == "Ctrl+C"
    assert PHASE1_ACTIONS["edit_paste"].shortcut == "Ctrl+V"


def test_main_window_edit_menu_matches_legacy_order_and_defaults(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "edit-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    edit_menu = _edit_menu(window)
    assert _menu_sequence(edit_menu) == LEGACY_EDIT_MENU_SEQUENCE
    assert _menu_sequence(_submenu(edit_menu, "Border Options")) == LEGACY_EDIT_BORDER_ITEMS
    assert _menu_sequence(_submenu(edit_menu, "Other Options")) == LEGACY_EDIT_OTHER_ITEMS

    assert window.edit_menu_actions["border_automagic"].isCheckable()
    assert (
        window.edit_menu_actions["border_automagic"].isChecked()
        is LEGACY_EDIT_STATE_DEFAULTS["border_automagic"]
    )


def test_editor_model_tracks_undo_redo_for_tile_edits() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.activate_item_brush(1)

    assert editor.apply_active_tool_at(position) is True
    assert editor.can_undo() is True
    assert editor.can_redo() is False
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=1,
    )

    assert editor.undo() is True
    assert editor.map_model.get_tile(position) is None
    assert editor.can_undo() is False
    assert editor.can_redo() is True

    assert editor.redo() is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=1,
    )


def test_editor_model_copies_cuts_and_pastes_selected_tiles() -> None:
    editor = EditorModel()
    source = MapPosition(32000, 32000, 7)
    target = MapPosition(32010, 32020, 7)
    editor.map_model.set_tile(TileState(position=source, ground_item_id=42))
    editor.map_model.clear_changed()
    editor.select_position(source)

    assert editor.copy_selection() is True
    assert editor.has_clipboard() is True
    assert editor.cut_selection() is True
    assert editor.map_model.get_tile(source) is None
    assert editor.can_undo() is True

    assert editor.paste_clipboard_at(target) is True
    assert editor.map_model.get_tile(target) == TileState(
        position=target,
        ground_item_id=42,
    )


def test_edit_history_and_clipboard_actions_update_shell_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "edit-actions.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert window.edit_undo_action.isEnabled() is False
    assert window.edit_redo_action.isEnabled() is False
    assert window.edit_cut_action.isEnabled() is False
    assert window.edit_copy_action.isEnabled() is False
    assert window.edit_paste_action.isEnabled() is False

    position = MapPosition(32000, 32000, 7)
    window._set_active_item_selection("Stone", 1)
    assert window._apply_active_tool_at_cursor() is True

    assert window.edit_undo_action.isEnabled() is True
    window.edit_undo_action.trigger()
    assert window._editor_context.session.editor.map_model.get_tile(position) is None
    assert _status_message(window) == "Undid last edit."
    assert window.edit_redo_action.isEnabled() is True

    window.edit_redo_action.trigger()
    assert window._editor_context.session.editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=1,
    )
    assert _status_message(window) == "Redid last edit."

    window._editor_context.session.editor.select_position(position)
    window._refresh_selection_action_state()
    assert window.edit_cut_action.isEnabled() is True
    assert window.edit_copy_action.isEnabled() is True

    window.edit_copy_action.trigger()
    assert _status_message(window) == "Copied 1 tile."
    assert window.edit_paste_action.isEnabled() is True

    window.edit_cut_action.trigger()
    assert window._editor_context.session.editor.map_model.get_tile(position) is None
    assert _status_message(window) == "Cut 1 tile."

    window._set_current_position(32005, 32006, 7)
    window.edit_paste_action.trigger()
    assert window._editor_context.session.editor.map_model.get_tile(
        MapPosition(32005, 32006, 7)
    ) == TileState(position=MapPosition(32005, 32006, 7), ground_item_id=1)
    assert _status_message(window) == "Pasted 1 tile."


def test_edit_actions_keep_unsupported_gaps_safe(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "edit-gap-actions.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._editor_context.session.editor.select_position(MapPosition(32000, 32000, 7))
    window._refresh_selection_action_state()
    window.edit_menu_actions["borderize_selection"].trigger()
    assert _status_message(window) == "Borderize Selection is not available yet."

    window.edit_menu_actions["remove_all_corpses"].trigger()
    assert _status_message(window) == "Remove all Corpses is not available yet."

    window.edit_menu_actions["border_automagic"].setChecked(False)
    assert _status_message(window) == "Automagic disabled."


def test_border_automagic_persists_as_global_setting(
    qtbot,
    settings_workspace: Path,
) -> None:
    settings = _build_settings(settings_workspace, "edit-automagic.ini")

    window = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.edit_menu_actions["border_automagic"].setChecked(False)
    assert _status_message(window) == "Automagic disabled."

    replacement = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(replacement)

    assert replacement.edit_menu_actions["border_automagic"].isChecked() is False
