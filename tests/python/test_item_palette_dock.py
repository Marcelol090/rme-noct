"""Item palette widget tests – search, category selection, selection signals."""

from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt

from pyrme.ui.docks.item_palette import ItemPaletteWidget
from pyrme.ui.models.item_palette_types import ItemEntry


@pytest.fixture
def entries() -> list[ItemEntry]:
    return [
        ItemEntry(1, "Stone", category="Ground"),
        ItemEntry(2, "Sword", category="Weapons"),
        ItemEntry(3, "Shield", category="Armor"),
        ItemEntry(4, "Grass", category="Ground"),
        ItemEntry(5, "Axe", category="Weapons"),
    ]


@pytest.fixture
def palette_widget(qapp, entries, qtbot) -> ItemPaletteWidget:  # noqa: ANN001, ARG001
    w = ItemPaletteWidget()
    w.load_items(entries)
    qtbot.addWidget(w)
    w.show()
    return w


def test_initial_load(palette_widget: ItemPaletteWidget) -> None:
    assert palette_widget._result_model.rowCount() == 5
    assert palette_widget._category_model.rowCount() == 4  # All + 3 distinct categories


def test_search_filtering(palette_widget: ItemPaletteWidget) -> None:
    # Use public API — search is driven by parent dock
    palette_widget.set_search_text("S")
    # Stone, Sword, Shield, Grass (all contain 's' case-insensitive)
    assert palette_widget._result_model.rowCount() == 4

    palette_widget.set_search_text("Sword")
    assert palette_widget._result_model.rowCount() == 1


def test_category_selection(palette_widget: ItemPaletteWidget) -> None:
    # Categories are sorted: Armor, Ground, Weapons
    # Row 0: All
    # Row 1: Armor
    # Row 2: Ground
    # Row 3: Weapons

    # Let's verify sorting
    assert (
        palette_widget._category_model.data(palette_widget._category_model.index(1))
        == "Armor (1)"
    )

    # Click Weapons (Row 3)
    palette_widget._on_category_clicked(palette_widget._category_model.index(3))
    assert palette_widget._result_model.rowCount() == 2  # Sword, Axe


def test_selection_signal(palette_widget: ItemPaletteWidget) -> None:
    selected_item = None

    def on_selected(item: ItemEntry) -> None:
        nonlocal selected_item
        selected_item = item

    palette_widget.item_selected.connect(on_selected)

    # Click first item
    palette_widget._on_result_clicked(palette_widget._result_model.index(0))
    assert selected_item is not None
    assert selected_item.name == "Stone"


def test_empty_state_visibility(palette_widget: ItemPaletteWidget) -> None:
    # Ensure it's hidden initially
    assert not palette_widget._empty_label.isVisible()

    palette_widget.set_search_text("NONEXISTENT_STUFF")
    assert palette_widget._empty_label.isVisible()
    assert not palette_widget._result_view.isVisible()


def test_empty_state_label_is_centered(palette_widget: ItemPaletteWidget) -> None:
    assert palette_widget._empty_label.alignment() == Qt.AlignmentFlag.AlignCenter


def test_initial_all_category_selected(palette_widget: ItemPaletteWidget) -> None:
    """The 'All' row (index 0) should be visually selected on load."""
    sel_model = palette_widget._category_view.selectionModel()
    assert sel_model is not None
    indexes = sel_model.selectedIndexes()
    assert len(indexes) == 1
    assert indexes[0].row() == 0


def test_clear_category_resets_to_all(palette_widget: ItemPaletteWidget) -> None:
    """clear_category() should reset to 'All' and show everything."""
    # First narrow to a category
    palette_widget._on_category_clicked(palette_widget._category_model.index(3))
    assert palette_widget._result_model.rowCount() == 2  # Weapons only

    # Reset
    palette_widget.clear_category()
    assert palette_widget._result_model.rowCount() == 5  # All items
    assert palette_widget._current_category == ""

    # Verify "All" is selected in the view
    sel_model = palette_widget._category_view.selectionModel()
    assert sel_model is not None
    indexes = sel_model.selectedIndexes()
    assert len(indexes) == 1
    assert indexes[0].row() == 0
