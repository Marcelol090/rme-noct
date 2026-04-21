"""Item palette performance tests - 50k item load and scroll."""

from __future__ import annotations

import time

import pytest

from pyrme.ui.docks.item_palette import ItemPaletteWidget
from pyrme.ui.models.item_palette_types import ItemEntry, QueryKey

LOAD_50K_LIMIT_MS = 200.0
SEARCH_50K_LIMIT_MS = 50.0
CATEGORY_SWITCH_LIMIT_MS = 16.0
CACHE_HIT_LIMIT_MS = 5.0


@pytest.fixture
def big_entries() -> list[ItemEntry]:
    return [
        ItemEntry(i, f"Item_{i}", category=f"Cat_{i % 10}")
        for i in range(50_000)
    ]


def test_50k_load_speed(qapp, big_entries, qtbot) -> None:  # noqa: ANN001, ARG001
    w = ItemPaletteWidget()
    qtbot.addWidget(w)

    t0 = time.perf_counter()
    w.load_items(big_entries)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert elapsed_ms < LOAD_50K_LIMIT_MS, (
        f"Load took {elapsed_ms:.1f}ms (limit {LOAD_50K_LIMIT_MS:.0f}ms)"
    )
    assert w._result_model.rowCount() == 50_000


def test_50k_search_latency(qapp, big_entries, qtbot) -> None:  # noqa: ANN001, ARG001
    w = ItemPaletteWidget()
    qtbot.addWidget(w)
    w.load_items(big_entries)

    t0 = time.perf_counter()
    w.set_search_text("Item_49999")
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert elapsed_ms < SEARCH_50K_LIMIT_MS, (
        f"Search took {elapsed_ms:.1f}ms (limit {SEARCH_50K_LIMIT_MS:.0f}ms)"
    )
    assert w._result_model.rowCount() >= 1


def test_50k_category_switch_latency(qapp, big_entries, qtbot) -> None:  # noqa: ANN001, ARG001
    w = ItemPaletteWidget()
    qtbot.addWidget(w)
    w.load_items(big_entries)

    index = w._category_model.index(6)
    assert "Cat_5" in w._category_model.data(index)

    t0 = time.perf_counter()
    w._on_category_clicked(index)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert elapsed_ms < CATEGORY_SWITCH_LIMIT_MS, (
        f"Category switch took {elapsed_ms:.1f}ms "
        f"(limit {CATEGORY_SWITCH_LIMIT_MS:.0f}ms)"
    )
    assert w._result_model.rowCount() == 5000


def test_50k_cache_hit_latency(qapp, big_entries, qtbot) -> None:  # noqa: ANN001, ARG001
    w = ItemPaletteWidget()
    qtbot.addWidget(w)
    w.load_items(big_entries)

    key = QueryKey.from_raw("Item_49999", "Cat_9")
    first_result = w._catalog.query(key)

    second_t0 = time.perf_counter()
    second_result = w._catalog.query(key)
    second_elapsed_ms = (time.perf_counter() - second_t0) * 1000

    assert first_result == second_result
    assert second_elapsed_ms < CACHE_HIT_LIMIT_MS, (
        f"Cache hit took {second_elapsed_ms:.3f}ms "
        f"(limit {CACHE_HIT_LIMIT_MS:.0f}ms)"
    )
