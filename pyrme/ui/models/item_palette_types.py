"""Lightweight data contracts for the item palette."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ItemEntry:
    """Single selectable item row in the palette catalog."""

    item_id: int
    name: str
    server_id: int | None = None
    client_id: int | None = None
    category: str = ""
    flags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class CategoryEntry:
    """Category rail row derived from the catalog."""

    name: str
    count: int


@dataclass(frozen=True, slots=True)
class QueryKey:
    """Normalized cache key for item palette filtering."""

    search_text: str = ""
    category: str = ""

    def __post_init__(self) -> None:
        normalized_search_text = " ".join(self.search_text.split()).casefold()
        normalized_category = " ".join(self.category.split())
        object.__setattr__(self, "search_text", normalized_search_text)
        object.__setattr__(self, "category", normalized_category)

    @classmethod
    def from_raw(cls, search_text: str = "", category: str = "") -> QueryKey:
        return cls(search_text, category)
