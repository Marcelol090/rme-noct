from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings

from pyrme.editor.model import EditorModel, MapPosition, TileState
from pyrme.ui.legacy_menu_contract import (
    LEGACY_SELECTION_FIND_ITEMS,
    LEGACY_SELECTION_MENU_SEQUENCE,
    LEGACY_SELECTION_MODE_DEFAULTS,
    LEGACY_SELECTION_MODE_ITEMS,
    PHASE1_ACTIONS,
)
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _selection_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(
        action.menu() for action in menu_bar.actions() if action.text() == "Selection"
    )
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


class _SelectionTransformService:
    def __init__(self, *, item_id: int = 200) -> None:
        self.item_id = item_id
        self.confirmed: list[str] = []

    def choose_replace_items(self, _parent, _context) -> tuple[int, int]:
        return (200, 500)

    def choose_remove_items_by_id(self, _parent, _context) -> int:
        return self.item_id

    def confirm_map_transform(self, _parent, label: str) -> bool:
        self.confirmed.append(label)
        return True


def _seed_selected_map(editor: EditorModel) -> tuple[MapPosition, MapPosition, MapPosition]:
    first = MapPosition(32000, 32000, 7)
    second = MapPosition(32001, 32000, 7)
    unselected = MapPosition(32002, 32000, 7)
    editor.map_model.set_tile(
        TileState(position=first, ground_item_id=200, item_ids=(300, 200))
    )
    editor.map_model.set_tile(
        TileState(position=second, ground_item_id=400, item_ids=(500,))
    )
    editor.map_model.set_tile(
        TileState(position=unselected, ground_item_id=200, item_ids=(200,))
    )
    editor.map_model.clear_changed()
    editor.select_position(first)
    editor.select_position(second)
    return first, second, unselected


def test_legacy_selection_contract_matches_xml_and_defaults() -> None:
    assert LEGACY_SELECTION_MENU_SEQUENCE == (
        "Replace Items on Selection",
        "Find Item on Selection",
        "Remove Item on Selection",
        None,
        "Find on Selection",
        None,
        "Selection Mode",
        None,
        "Borderize Selection",
        "Randomize Selection",
    )
    assert LEGACY_SELECTION_FIND_ITEMS == (
        "Find Everything",
        None,
        "Find Unique",
        "Find Action",
        "Find Container",
        "Find Writeable",
    )
    assert LEGACY_SELECTION_MODE_ITEMS == (
        "Compensate Selection",
        None,
        "Current Floor",
        "Lower Floors",
        "Visible Floors",
    )
    assert LEGACY_SELECTION_MODE_DEFAULTS == {
        "select_mode_compensate": True,
        "select_mode_current": True,
        "select_mode_lower": False,
        "select_mode_visible": False,
    }
    assert PHASE1_ACTIONS["replace_on_selection_items"].status_tip == (
        "Replace items on selected area."
    )
    assert PHASE1_ACTIONS["search_on_selection_item"].status_tip == (
        "Find items on selected area."
    )
    assert PHASE1_ACTIONS["remove_on_selection_item"].status_tip == (
        "Remove item on selected area."
    )


def test_main_window_selection_menu_matches_legacy_order_and_defaults(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    selection_menu = _selection_menu(window)
    assert _menu_sequence(selection_menu) == LEGACY_SELECTION_MENU_SEQUENCE
    assert _menu_sequence(_submenu(selection_menu, "Find on Selection")) == (
        LEGACY_SELECTION_FIND_ITEMS
    )
    assert _menu_sequence(_submenu(selection_menu, "Selection Mode")) == (
        LEGACY_SELECTION_MODE_ITEMS
    )

    for key, expected in LEGACY_SELECTION_MODE_DEFAULTS.items():
        action = window.selection_menu_actions[key]
        assert action.isCheckable()
        assert action.isChecked() is expected

    assert window.selection_menu_actions["select_mode_lower"].isEnabled() is True
    assert window.selection_menu_actions["select_mode_visible"].isEnabled() is True


def test_selection_actions_follow_selection_presence_and_safe_gaps(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-actions.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    disabled_keys = (
        "replace_on_selection_items",
        "search_on_selection_item",
        "remove_on_selection_item",
        "search_on_selection_everything",
        "search_on_selection_unique",
        "search_on_selection_action",
        "search_on_selection_container",
        "search_on_selection_writeable",
    )
    for key in disabled_keys:
        assert window.selection_menu_actions[key].isEnabled() is False

    assert window.edit_menu_actions["borderize_selection"].isEnabled() is False
    assert window.edit_menu_actions["randomize_selection"].isEnabled() is False

    window._editor_context.session.editor.select_position(MapPosition(32000, 32000, 7))
    window._refresh_selection_action_state()

    for key in disabled_keys:
        assert window.selection_menu_actions[key].isEnabled() is True

    assert window.edit_menu_actions["borderize_selection"].isEnabled() is True
    assert window.edit_menu_actions["randomize_selection"].isEnabled() is True

    window.selection_menu_actions["replace_on_selection_items"].trigger()
    assert (
        _status_message(window)
        == "Replace Items on Selection deferred: no item selection dialog is mounted."
    )


def test_editor_model_counts_selected_item_occurrences() -> None:
    editor = EditorModel()
    _first, _second, _unselected = _seed_selected_map(editor)

    assert editor.selection_item_counts() == {200: 2, 300: 1, 400: 1, 500: 1}


def test_selection_replace_and_remove_items_mutate_only_selected_tiles(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _SelectionTransformService(item_id=500)
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-mutate.ini"),
        enable_docks=False,
        edit_transform_service=service,
    )
    qtbot.addWidget(window)

    editor = window._editor_context.session.editor
    first, second, unselected = _seed_selected_map(editor)
    window._refresh_selection_action_state()

    window.selection_menu_actions["replace_on_selection_items"].trigger()
    assert editor.map_model.get_tile(first) == TileState(
        position=first,
        ground_item_id=500,
        item_ids=(300, 500),
    )
    assert editor.map_model.get_tile(second) == TileState(
        position=second,
        ground_item_id=400,
        item_ids=(500,),
    )
    assert editor.map_model.get_tile(unselected) == TileState(
        position=unselected,
        ground_item_id=200,
        item_ids=(200,),
    )
    assert service.confirmed == ["Replace Items on Selection"]
    assert _status_message(window) == "Replaced 2 selected item occurrences."

    window.selection_menu_actions["remove_on_selection_item"].trigger()
    assert editor.map_model.get_tile(first) == TileState(
        position=first,
        ground_item_id=None,
        item_ids=(300,),
    )
    assert editor.map_model.get_tile(second) == TileState(
        position=second,
        ground_item_id=400,
        item_ids=(),
    )
    assert editor.map_model.get_tile(unselected) == TileState(
        position=unselected,
        ground_item_id=200,
        item_ids=(200,),
    )
    assert service.confirmed == [
        "Replace Items on Selection",
        "Remove Item on Selection",
    ]
    assert _status_message(window) == "Removed 3 selected item occurrences."


def test_selection_search_actions_report_selected_item_counts(
    qtbot,
    settings_workspace: Path,
) -> None:
    service = _SelectionTransformService(item_id=200)
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-search.ini"),
        enable_docks=False,
        edit_transform_service=service,
    )
    qtbot.addWidget(window)

    editor = window._editor_context.session.editor
    _seed_selected_map(editor)
    window._refresh_selection_action_state()

    window.selection_menu_actions["search_on_selection_item"].trigger()
    assert _status_message(window) == "Found 2 selected item occurrences for item #200."

    window.selection_menu_actions["search_on_selection_everything"].trigger()
    assert _status_message(window) == "Selection contains 2 tiles and 5 item occurrences."

    window.selection_menu_actions["search_on_selection_unique"].trigger()
    assert _status_message(window) == "Selection unique item IDs: 200, 300, 400, 500."


def test_selection_type_filter_gaps_report_missing_item_flags(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-filter-gaps.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    editor = window._editor_context.session.editor
    _seed_selected_map(editor)
    window._refresh_selection_action_state()

    window.selection_menu_actions["search_on_selection_action"].trigger()
    assert (
        _status_message(window)
        == "Find Action on Selection deferred: TileState has no item type flags."
    )

    window.selection_menu_actions["search_on_selection_container"].trigger()
    assert (
        _status_message(window)
        == "Find Container on Selection deferred: TileState has no item type flags."
    )

    window.selection_menu_actions["search_on_selection_writeable"].trigger()
    assert (
        _status_message(window)
        == "Find Writeable on Selection deferred: TileState has no item type flags."
    )


def test_selection_mode_enablement_tracks_show_all_floors(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "selection-mode.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.selection_menu_actions["select_mode_lower"].setChecked(True)
    assert window.selection_menu_actions["select_mode_lower"].isChecked() is True

    window.view_menu_actions["view_show_all_floors"].setChecked(False)

    assert window.selection_menu_actions["select_mode_current"].isChecked() is True
    assert window.selection_menu_actions["select_mode_lower"].isEnabled() is False
    assert window.selection_menu_actions["select_mode_visible"].isEnabled() is False

    window.view_menu_actions["view_show_all_floors"].setChecked(True)

    assert window.selection_menu_actions["select_mode_lower"].isEnabled() is True
    assert window.selection_menu_actions["select_mode_visible"].isEnabled() is True


def test_selection_mode_persists_in_settings(qtbot, settings_workspace: Path) -> None:
    settings = _build_settings(settings_workspace, "selection-persist.ini")

    window = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.selection_menu_actions["select_mode_compensate"].setChecked(False)
    window.selection_menu_actions["select_mode_visible"].setChecked(True)

    replacement = MainWindow(
        settings=settings,
        enable_docks=False,
    )
    qtbot.addWidget(replacement)

    assert replacement.selection_menu_actions["select_mode_compensate"].isChecked() is False
    assert replacement.selection_menu_actions["select_mode_visible"].isChecked() is True
