"""Item palette model tests – query, cache, category, empty state."""

from __future__ import annotations

import time

from pyrme.ui.models.item_palette_model import (
    ItemCatalog,
    ItemCategoryModel,
    ItemResultModel,
)
from pyrme.ui.models.item_palette_types import ItemEntry, QueryKey


def _make_entries(n: int = 100) -> list[ItemEntry]:
    categories = ["Ground", "Weapons", "Armor", "Decoration", "Food"]
    return [
        ItemEntry(
            item_id=i,
            name=f"Item_{i}",
            server_id=i + 1000,
            category=categories[i % len(categories)],
        )
        for i in range(n)
    ]


# ── Catalog tests ─────────────────────────────────────────────
class TestItemCatalog:
    def test_load_and_size(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(200))
        assert cat.size == 200

    def test_query_key_normalizes_whitespace_and_case(self) -> None:
        key = QueryKey.from_raw("  GOLD   Coin  ", "  Weapons  ")
        assert key.search_text == "gold coin"
        assert key.category == "Weapons"

    def test_categories(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(50))
        cats = cat.categories()
        names = [c.name for c in cats]
        assert "Ground" in names
        assert "Weapons" in names

    def test_query_empty_text_returns_all(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        key = QueryKey.from_raw("")
        result = cat.query(key)
        assert len(result) == 100

    def test_query_filter_by_name(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        key = QueryKey.from_raw("Item_42")
        result = cat.query(key)
        assert len(result) >= 1
        assert cat.entries[result[0]].name == "Item_42"

    def test_query_filter_by_category(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        key = QueryKey.from_raw("", "Ground")
        result = cat.query(key)
        assert all(cat.entries[i].category == "Ground" for i in result)

    def test_query_cache_hit(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        key = QueryKey.from_raw("item_5")
        r1 = cat.query(key)
        r2 = cat.query(key)
        assert r1 is r2  # same object = cached

    def test_cache_invalidation(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        key = QueryKey.from_raw("item_5")
        r1 = cat.query(key)
        cat.invalidate_cache()
        r2 = cat.query(key)
        assert r1 is not r2
        assert r1 == r2

    def test_empty_result(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        key = QueryKey.from_raw("NONEXISTENT_ITEM_XYZ")
        result = cat.query(key)
        assert len(result) == 0

    def test_50k_query_speed(self) -> None:
        cat = ItemCatalog()
        cat.load(_make_entries(50_000))
        key = QueryKey.from_raw("item_999")
        t0 = time.perf_counter()
        cat.query(key)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 100, f"Query took {elapsed_ms:.1f}ms (limit 100ms)"


# ── Result model tests ────────────────────────────────────────
class TestItemResultModel:
    def test_show_all(self, qapp) -> None:  # noqa: ANN001, ARG002
        cat = ItemCatalog()
        cat.load(_make_entries(50))
        model = ItemResultModel(cat)
        model.show_all()
        assert model.rowCount() == 50

    def test_apply_query_narrows(self, qapp) -> None:  # noqa: ANN001, ARG002
        cat = ItemCatalog()
        cat.load(_make_entries(100))
        model = ItemResultModel(cat)
        model.apply_query(QueryKey.from_raw("Item_42"))
        assert model.visible_count >= 1

    def test_entry_at(self, qapp) -> None:  # noqa: ANN001, ARG002
        cat = ItemCatalog()
        cat.load(_make_entries(10))
        model = ItemResultModel(cat)
        model.show_all()
        entry = model.entry_at(0)
        assert entry is not None
        assert entry.item_id == 0


# ── Category model tests ──────────────────────────────────────
class TestItemCategoryModel:
    def test_all_label_first(self, qapp) -> None:  # noqa: ANN001, ARG002
        cat = ItemCatalog()
        cat.load(_make_entries(50))
        cm = ItemCategoryModel()
        cm.load_from_catalog(cat)
        idx = cm.index(0)
        assert cm.data(idx) == "All"

    def test_category_at_zero_returns_empty(self, qapp) -> None:  # noqa: ANN001, ARG002
        cm = ItemCategoryModel()
        assert cm.category_at(0) == ""

    def test_category_at_valid_row(self, qapp) -> None:  # noqa: ANN001, ARG002
        cat = ItemCatalog()
        cat.load(_make_entries(50))
        cm = ItemCategoryModel()
        cm.load_from_catalog(cat)
        # Row 1 should be some category
        name = cm.category_at(1)
        assert name != ""
