"""Item palette data types – lightweight, immutable contracts."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ItemEntry:
    """Single item in the catalog."""

    item_id: int
    name: str
    server_id: int = 0
    category: str = "Uncategorized"
    # Pre-computed lowercase name for O(1) search matching
    _search_key: str = field(default="", repr=False, compare=False)

    def __post_init__(self) -> None:
        # frozen=True requires object.__setattr__ for post-init mutation
        if not self._search_key:
            object.__setattr__(self, "_search_key", self.name.lower())


@dataclass(frozen=True, slots=True)
class CategoryNode:
    """Category entry for the left rail."""

    name: str
    count: int = 0


@dataclass(frozen=True, slots=True)
class QueryKey:
    """Normalized cache key for filtered results."""

    search_text: str = ""
    category: str = ""

    @staticmethod
    def from_raw(text: str, category: str = "") -> QueryKey:
        return QueryKey(
            search_text=text.strip().lower(),
            category=category,
        )
