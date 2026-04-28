"""Item palette shell-level integration tests (T14).

Verifies the Item palette works correctly when mounted inside
BrushPaletteDock, including tab switching, search delegation,
and the public item_palette property.
"""

from __future__ import annotations

import pytest

from pyrme.ui.docks.brush_palette import BrushPaletteDock
from pyrme.ui.docks.item_palette import ItemPaletteWidget


@pytest.fixture
def dock(qapp, qtbot) -> BrushPaletteDock:  # noqa: ANN001, ARG001
    d = BrushPaletteDock()
    qtbot.addWidget(d)
    d.show()
    return d


class TestItemTabMounting:
    """Verify the Item tab is an ItemPaletteWidget inside the dock."""

    def test_item_tab_exists(self, dock: BrushPaletteDock) -> None:
        found = False
        for i in range(dock.tabs.count()):
            if dock.tabs.tabText(i) == "Item":
                found = True
                break
        assert found, "Item tab not found in BrushPaletteDock"

    def test_item_tab_is_palette_widget(self, dock: BrushPaletteDock) -> None:
        for i in range(dock.tabs.count()):
            if dock.tabs.tabText(i) == "Item":
                widget = dock.tabs.widget(i)
                assert isinstance(widget, ItemPaletteWidget)
                return
        pytest.fail("Item tab not found")

    def test_item_tab_has_object_name(self, dock: BrushPaletteDock) -> None:
        for i in range(dock.tabs.count()):
            if dock.tabs.tabText(i) == "Item":
                widget = dock.tabs.widget(i)
                assert widget.objectName() == "Item"
                return
        pytest.fail("Item tab not found")


class TestSelectPalette:
    """Verify select_palette() works for the Item tab."""

    def test_select_palette_item(self, dock: BrushPaletteDock) -> None:
        # Start on a different tab
        dock.select_palette("Terrain")
        assert dock.current_palette() == "Terrain"

        # Switch to Item
        result = dock.select_palette("Item")
        assert result is True
        assert dock.current_palette() == "Item"

    def test_select_palette_back_and_forth(self, dock: BrushPaletteDock) -> None:
        dock.select_palette("Item")
        assert dock.current_palette() == "Item"

        dock.select_palette("RAW")
        assert dock.current_palette() == "RAW"

        dock.select_palette("Item")
        assert dock.current_palette() == "Item"


class TestDockSearchDrivesItemPalette:
    """Verify the dock's search bar drives the Item palette filter."""

    def test_search_filters_item_results(self, dock: BrushPaletteDock) -> None:
        dock.select_palette("Item")
        palette = dock.item_palette
        assert palette is not None

        initial_count = palette._result_model.rowCount()
        assert initial_count > 0

        # Type a search that should narrow results
        dock._search_bar.setText("Stone")
        assert palette._result_model.rowCount() < initial_count
        assert palette._result_model.rowCount() >= 1

    def test_clear_search_restores_all(self, dock: BrushPaletteDock) -> None:
        dock.select_palette("Item")
        palette = dock.item_palette
        assert palette is not None

        initial_count = palette._result_model.rowCount()

        dock._search_bar.setText("Stone")
        assert palette._result_model.rowCount() < initial_count

        dock._search_bar.clear()
        assert palette._result_model.rowCount() == initial_count


class TestItemPaletteProperty:
    """Verify the public item_palette property."""

    def test_property_returns_widget(self, dock: BrushPaletteDock) -> None:
        palette = dock.item_palette
        assert palette is not None
        assert isinstance(palette, ItemPaletteWidget)

    def test_property_can_reload_data(self, dock: BrushPaletteDock) -> None:
        from pyrme.ui.models.item_palette_types import ItemEntry

        palette = dock.item_palette
        assert palette is not None

        new_items = [ItemEntry(i, f"New_{i}", category="Test") for i in range(10)]
        palette.load_items(new_items)
        assert palette._result_model.rowCount() == 10


class TestSelectionSeam:
    """Verify item selection escapes the widget boundary through the dock seam."""

    def test_dock_re_emits_item_selection(self, dock: BrushPaletteDock) -> None:
        selected: list[object] = []
        dock.item_selected.connect(selected.append)

        palette = dock.item_palette
        assert palette is not None

        palette._on_result_clicked(palette._result_model.index(0))

        assert len(selected) == 1
        assert selected[0].name == "Stone"


class TestTabSwitchPreservesBehavior:
    """Verify other tabs keep working after Item tab usage."""

    def test_terrain_tab_still_works(self, dock: BrushPaletteDock) -> None:
        dock.select_palette("Item")
        dock.select_palette("Terrain")
        assert dock.current_palette() == "Terrain"
        # Terrain should still have its proxy model
        assert "Terrain" in dock._proxies

    def test_all_palette_names_reachable(self, dock: BrushPaletteDock) -> None:
        for name in dock.palette_names():
            result = dock.select_palette(name)
            assert result is True, f"Cannot switch to palette '{name}'"
            assert dock.current_palette() == name
