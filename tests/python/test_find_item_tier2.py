"""Tier 2 widget tests for the Find Item dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QLabel, QListView

from pyrme.ui.dialogs.find_item import (
    FindItemDialog,
    FindItemQuery,
    FindItemResult,
    FindItemResultMode,
)


def _catalog() -> list[FindItemResult]:
    return [
        FindItemResult(2555, 2555, "Grass", "sprite-2555", "item", {"pickupable"}),
        FindItemResult(
            1049,
            1049,
            "Stone Wall",
            "sprite-1049",
            "raw-item",
            {"impassable", "immovable"},
        ),
        FindItemResult(2148, 2148, "Gold Coin", "sprite-2148", "item", {"pickupable", "stackable"}),
        FindItemResult(3100, 3100, "Dragon", "sprite-3100", "creature", set()),
    ]


def _result_count(dialog: FindItemDialog) -> int:
    return dialog.item_list.model().rowCount()


def _current_result_text(dialog: FindItemDialog) -> str | None:
    index = dialog.item_list.currentIndex()
    if not index.isValid():
        return None
    value = dialog.item_list.model().data(index)
    return str(value) if value is not None else None


def test_find_item_dialog_renders_required_controls(qtbot) -> None:
    dialog = FindItemDialog(catalog=_catalog())
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Find Item"
    assert dialog.search_field is not None
    assert dialog.chk_items is not None
    assert dialog.chk_raw is not None
    assert dialog.chk_creatures is not None
    assert dialog.chk_impassable is not None
    assert dialog.chk_immovable is not None
    assert dialog.chk_container is not None
    assert dialog.chk_pickupable is not None
    assert dialog.chk_stackable is not None
    assert dialog.chk_writable is not None
    assert dialog.item_list is not None
    assert dialog.btn_search_map.text() == "Search on Map"
    assert dialog.btn_cancel.text() == "Cancel"
    assert dialog.btn_ok.text() == "OK"
    assert dialog.btn_list_mode.text() == "List"
    assert dialog.btn_grid_mode.text() == "Grid"


def test_find_item_dialog_updates_results_and_switches_modes(qtbot) -> None:
    dialog = FindItemDialog(
        catalog=_catalog(),
        query=FindItemQuery(
            search_text="",
            type_filters={"item", "raw-item", "creature"},
            property_filters=set(),
            result_mode=FindItemResultMode.LIST,
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog.item_list.viewMode() == QListView.ViewMode.ListMode
    assert _result_count(dialog) == 4

    dialog.set_query(
        FindItemQuery(
            search_text="wall",
            type_filters={"raw-item"},
            property_filters={"impassable", "immovable"},
            result_mode=FindItemResultMode.GRID,
        )
    )

    assert dialog.current_query().result_mode == FindItemResultMode.GRID
    assert dialog.item_list.viewMode() == QListView.ViewMode.IconMode
    assert _result_count(dialog) == 1
    assert dialog.result_count.text() == "1 result"
    assert _current_result_text(dialog) == "Stone Wall\n#1049"

    dialog.btn_search_map.click()
    assert dialog._last_search_map_query is not None
    assert dialog._last_search_map_query.search_text == "wall"


def test_find_item_dialog_returns_selected_result_on_accept(qtbot) -> None:
    dialog = FindItemDialog(
        catalog=_catalog(),
        query=FindItemQuery(
            search_text="coin",
            type_filters={"item"},
            property_filters={"pickupable", "stackable"},
            result_mode=FindItemResultMode.LIST,
        ),
    )
    qtbot.addWidget(dialog)

    assert _result_count(dialog) == 1
    dialog.item_list.setCurrentIndex(dialog.item_list.model().index(0, 0))
    dialog.accept()

    assert dialog.selected_result() == FindItemResult(
        2148,
        2148,
        "Gold Coin",
        "sprite-2148",
        "item",
        {"pickupable", "stackable"},
        search_haystack="gold coin 2148 2148 sprite-2148",
    )


def test_find_item_dialog_allows_custom_window_title_and_search_map_snapshot(qtbot) -> None:
    dialog = FindItemDialog(catalog=_catalog(), window_title="Jump to Item")
    qtbot.addWidget(dialog)
    dialog.show()

    dialog.search_field.setText("dragon")
    dialog.btn_search_map.click()

    assert dialog.windowTitle() == "Jump to Item"
    assert "Jump to Item" in [label.text() for label in dialog.findChildren(QLabel)]
    assert dialog.result() == int(QDialog.DialogCode.Rejected)
    assert dialog.isVisible() is False
    assert dialog.last_search_map_query() is not None
    assert dialog.last_search_map_query().search_text == "dragon"
