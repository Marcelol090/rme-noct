"""Brush palette performance tests – 50k items, instant search.

Verifies:
1. VirtualBrushModel handles 50k rows without blocking.
2. QSortFilterProxyModel filters 50k items in <50ms.
3. 8px spacing on list items.
4. Hover/press/selected states exist in stylesheet.
"""

from __future__ import annotations

import time

import pytest
from PyQt6.QtCore import QSortFilterProxyModel, Qt

from pyrme.ui.docks.brush_palette import BrushPaletteDock, VirtualBrushModel

ITEM_COUNT = 50_000


@pytest.fixture
def model() -> VirtualBrushModel:
    m = VirtualBrushModel()
    m.load_names([f"Brush_{i}" for i in range(ITEM_COUNT)])
    return m


@pytest.fixture
def dock(qapp) -> BrushPaletteDock:  # noqa: ANN001, ARG001
    return BrushPaletteDock()


# ── rowCount ──────────────────────────────────────────────────
class TestVirtualBrushModel:
    def test_row_count(self, model: VirtualBrushModel) -> None:
        assert model.rowCount() == ITEM_COUNT

    def test_data_returns_string(self, model: VirtualBrushModel) -> None:
        idx = model.index(0)
        assert model.data(idx, Qt.ItemDataRole.DisplayRole) == "Brush_0"

    def test_load_does_not_block(self) -> None:
        """Inserting 50k strings into the model must take <200ms."""
        m = VirtualBrushModel()
        names = [f"item_{i}" for i in range(ITEM_COUNT)]
        t0 = time.perf_counter()
        m.load_names(names)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 200, f"load_names took {elapsed_ms:.1f}ms (limit 200ms)"


# ── filter proxy ──────────────────────────────────────────────
class TestProxyFilter:
    def test_filter_speed(self, model: VirtualBrushModel) -> None:
        """Filtering 50k items with a fixed string must take <50ms."""
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive,
        )

        t0 = time.perf_counter()
        proxy.setFilterFixedString("Brush_999")
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 50, f"filter took {elapsed_ms:.1f}ms (limit 50ms)"
        # "Brush_999", "Brush_9990"..."Brush_9999" etc
        assert proxy.rowCount() > 0


# ── dock integration ──────────────────────────────────────────
class TestBrushDockIntegration:
    def test_search_bar_exists(self, dock: BrushPaletteDock) -> None:
        assert dock._search_bar is not None

    def test_palette_tabs_exist(self, dock: BrushPaletteDock) -> None:
        assert dock.tabs.count() == len(dock.palette_names())

    def test_8px_spacing_in_stylesheet(self, dock: BrushPaletteDock) -> None:
        """Item padding must use 8px grid."""
        first_view = list(dock._views.values())[0]
        ss = first_view.styleSheet()
        assert "padding: 8px" in ss

    def test_hover_state_in_stylesheet(self, dock: BrushPaletteDock) -> None:
        first_view = list(dock._views.values())[0]
        ss = first_view.styleSheet()
        assert "hover" in ss

    def test_selected_state_in_stylesheet(self, dock: BrushPaletteDock) -> None:
        first_view = list(dock._views.values())[0]
        ss = first_view.styleSheet()
        assert "selected" in ss
