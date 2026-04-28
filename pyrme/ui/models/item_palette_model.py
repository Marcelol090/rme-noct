"""Cached item palette catalog and Qt list models."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt

from pyrme.ui.models.item_palette_types import CategoryEntry, ItemEntry, QueryKey

if TYPE_CHECKING:
    from collections.abc import Iterable

_ROOT_INDEX = QModelIndex()


class ItemCatalog:
    """Qt-free searchable item catalog with cached query results."""

    def __init__(self) -> None:
        self.entries: list[ItemEntry] = []
        self._search_text: list[str] = []
        self._category_rows: dict[str, list[int]] = {}
        self._cache: dict[QueryKey, tuple[int, ...]] = {}

    @property
    def size(self) -> int:
        return len(self.entries)

    def load(self, entries: Iterable[ItemEntry]) -> None:
        self.entries = list(entries)
        self._search_text = [
            " ".join(
                part
                for part in (
                    entry.name,
                    str(entry.item_id),
                    str(entry.server_id) if entry.server_id is not None else "",
                    str(entry.client_id) if entry.client_id is not None else "",
                )
                if part
            ).casefold()
            for entry in self.entries
        ]

        category_rows: dict[str, list[int]] = defaultdict(list)
        for row, entry in enumerate(self.entries):
            category_rows[entry.category].append(row)
        self._category_rows = dict(category_rows)
        self.invalidate_cache()

    def invalidate_cache(self) -> None:
        self._cache.clear()

    def categories(self) -> list[CategoryEntry]:
        return [
            CategoryEntry(name, len(rows))
            for name, rows in sorted(self._category_rows.items())
            if name
        ]

    def query(self, key: QueryKey) -> tuple[int, ...]:
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        rows: Iterable[int]
        if key.category:
            rows = self._category_rows.get(key.category, [])
        else:
            rows = range(len(self.entries))

        if key.search_text:
            result = tuple(
                row
                for row in rows
                if key.search_text in self._search_text[row]
            )
        else:
            result = tuple(rows)

        self._cache[key] = result
        return result


class ItemResultModel(QAbstractListModel):
    """Virtualized item result model for ``QListView``."""

    def __init__(self, catalog: ItemCatalog, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self._catalog = catalog
        self._visible_rows: tuple[int, ...] = ()

    @property
    def visible_count(self) -> int:
        return len(self._visible_rows)

    def index(  # noqa: D102
        self,
        row: int,
        column: int = 0,
        parent: QModelIndex = _ROOT_INDEX,
    ) -> QModelIndex:
        return super().index(row, column, parent)

    def rowCount(self, parent: QModelIndex = _ROOT_INDEX) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._visible_rows)

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):  # noqa: ANN201
        if not index.isValid() or not 0 <= index.row() < len(self._visible_rows):
            return None

        entry = self._catalog.entries[self._visible_rows[index.row()]]
        if role == int(Qt.ItemDataRole.DisplayRole):
            return entry.name
        if role == int(Qt.ItemDataRole.UserRole):
            return entry
        if role == int(Qt.ItemDataRole.ToolTipRole):
            return f"{entry.name} #{entry.item_id}"
        return None

    def flags(self, index: QModelIndex):  # noqa: ANN201
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def show_all(self) -> None:
        self.apply_query(QueryKey())

    def apply_query(self, key: QueryKey) -> None:
        rows = self._catalog.query(key)
        self.beginResetModel()
        self._visible_rows = rows
        self.endResetModel()

    def entry_at(self, row: int) -> ItemEntry | None:
        if not 0 <= row < len(self._visible_rows):
            return None
        return self._catalog.entries[self._visible_rows[row]]


class ItemCategoryModel(QAbstractListModel):
    """Flat category rail model, with row 0 representing all categories."""

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self._categories: list[CategoryEntry] = []

    def index(  # noqa: D102
        self,
        row: int,
        column: int = 0,
        parent: QModelIndex = _ROOT_INDEX,
    ) -> QModelIndex:
        return super().index(row, column, parent)

    def rowCount(self, parent: QModelIndex = _ROOT_INDEX) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return 1 + len(self._categories)

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):  # noqa: ANN201
        if not index.isValid() or role != int(Qt.ItemDataRole.DisplayRole):
            return None
        row = index.row()
        if row == 0:
            return "All"
        if 1 <= row <= len(self._categories):
            category = self._categories[row - 1]
            return f"{category.name} ({category.count})"
        return None

    def flags(self, index: QModelIndex):  # noqa: ANN201
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def load_from_catalog(self, catalog: ItemCatalog) -> None:
        self.beginResetModel()
        self._categories = catalog.categories()
        self.endResetModel()

    def category_at(self, row: int) -> str:
        if row <= 0:
            return ""
        index = row - 1
        if not 0 <= index < len(self._categories):
            return ""
        return self._categories[index].name
