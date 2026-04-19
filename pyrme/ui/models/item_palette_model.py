"""Item palette model – catalog, cache, Qt models.

Owns the full item dataset and exposes filtered views through
QAbstractListModel subclasses.  Search is the primary interaction;
category narrowing is secondary.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt

from pyrme.ui.models.item_palette_types import CategoryNode, ItemEntry, QueryKey


# ── Catalog / Index ───────────────────────────────────────────
class ItemCatalog:
    """In-memory index over all items.  Precomputes search keys
    and category membership for O(n) scan on first query, then
    caches repeated queries.
    """

    def __init__(self) -> None:
        self._entries: list[ItemEntry] = []
        self._by_category: dict[str, list[int]] = defaultdict(list)
        self._cache: dict[QueryKey, list[int]] = {}

    # ── load ──────────────────────────────────────────────────
    def load(self, entries: list[ItemEntry]) -> None:
        """Replace the full dataset and rebuild indices."""
        self._entries = entries
        self._by_category.clear()
        self._cache.clear()
        for idx, entry in enumerate(entries):
            self._by_category[entry.category].append(idx)

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> list[ItemEntry]:
        return self._entries

    # ── categories ────────────────────────────────────────────
    def categories(self) -> list[CategoryNode]:
        """Sorted list of categories with counts."""
        nodes = [
            CategoryNode(name=cat, count=len(ids))
            for cat, ids in self._by_category.items()
        ]
        nodes.sort(key=lambda n: n.name)
        return nodes

    # ── query / filter ────────────────────────────────────────
    def query(self, key: QueryKey) -> list[int]:
        """Return row indices matching the query.  Cached."""
        if key in self._cache:
            return self._cache[key]

        indices = self._filter(key)
        self._cache[key] = indices
        return indices

    def _filter(self, key: QueryKey) -> list[int]:
        """Linear scan with pre-computed search keys."""
        pool: list[int]
        if key.category:
            pool = self._by_category.get(key.category, [])
        else:
            pool = list(range(len(self._entries)))

        if not key.search_text:
            return pool

        needle = key.search_text
        return [i for i in pool if needle in self._entries[i]._search_key]

    def invalidate_cache(self) -> None:
        self._cache.clear()


# ── Result List Model ─────────────────────────────────────────
class ItemResultModel(QAbstractListModel):
    """Virtual Qt model backed by filtered index refs."""

    def __init__(self, catalog: ItemCatalog, parent: Any = None) -> None:
        super().__init__(parent)
        self._catalog = catalog
        self._visible: list[int] = []

    def apply_query(self, key: QueryKey) -> None:
        """Re-filter and reset the view."""
        self.beginResetModel()
        self._visible = self._catalog.query(key)
        self.endResetModel()

    def show_all(self) -> None:
        self.beginResetModel()
        self._visible = list(range(self._catalog.size))
        self.endResetModel()

    @property
    def visible_count(self) -> int:
        return len(self._visible)

    def entry_at(self, row: int) -> ItemEntry | None:
        if 0 <= row < len(self._visible):
            return self._catalog.entries[self._visible[row]]
        return None

    # ── QAbstractListModel contract ───────────────────────────
    def rowCount(  # noqa: N802
        self, parent: QModelIndex | None = None,
    ) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._visible)

    def data(
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return None
        entry = self.entry_at(index.row())
        if entry is None:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{entry.name}  (ID: {entry.item_id})"
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"ID: {entry.item_id}  SID: {entry.server_id}  Cat: {entry.category}"
        return None


# ── Category List Model ───────────────────────────────────────
class ItemCategoryModel(QAbstractListModel):
    """Flat Qt model for the category rail."""

    ALL_LABEL = "All"

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._nodes: list[CategoryNode] = []

    def load_from_catalog(self, catalog: ItemCatalog) -> None:
        self.beginResetModel()
        self._nodes = catalog.categories()
        self.endResetModel()

    def category_at(self, row: int) -> str:
        """Return category name.  Row 0 is always 'All'."""
        if row == 0:
            return ""
        adjusted = row - 1
        if 0 <= adjusted < len(self._nodes):
            return self._nodes[adjusted].name
        return ""

    # ── QAbstractListModel contract ───────────────────────────
    def rowCount(  # noqa: N802
        self, parent: QModelIndex | None = None,
    ) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._nodes) + 1  # +1 for "All"

    def data(
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return None
        row = index.row()
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if row == 0:
            return self.ALL_LABEL
        adjusted = row - 1
        if 0 <= adjusted < len(self._nodes):
            node = self._nodes[adjusted]
            return f"{node.name} ({node.count})"
        return None
