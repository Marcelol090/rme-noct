"""Small Python brush catalog view model for palette widgets."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class BrushPaletteEntry:
    """Visible brush entry shared by palette widgets and search dialogs."""

    brush_id: int
    name: str
    kind: str
    palette_name: str
    look_id: int
    related_item_ids: tuple[int, ...]
    visible_in_palette: bool = True

    @property
    def active_brush_id(self) -> str:
        return f"brush:{self.kind}:{self.brush_id}"

    @property
    def search_text(self) -> str:
        parts = [
            self.name,
            self.kind,
            self.palette_name,
            str(self.brush_id),
            str(self.look_id),
            *(str(item_id) for item_id in self.related_item_ids),
        ]
        deduped_parts = tuple(dict.fromkeys(part.casefold() for part in parts))
        return " ".join(deduped_parts)


def default_brush_palette_entries() -> tuple[BrushPaletteEntry, ...]:
    """Return visible starter brush entries mirrored from the Rust brush contract."""
    return (
        BrushPaletteEntry(10, "grass", "ground", "Terrain", 4526, (4526, 4527)),
        BrushPaletteEntry(11, "dirt", "ground", "Terrain", 103, (103,)),
        BrushPaletteEntry(20, "stone wall", "wall", "Terrain", 3361, (3361, 3362)),
        BrushPaletteEntry(21, "wooden wall", "wall", "Terrain", 3390, (3390,)),
    )


def entries_by_palette(
    entries: Iterable[BrushPaletteEntry],
) -> dict[str, tuple[BrushPaletteEntry, ...]]:
    grouped: dict[str, list[BrushPaletteEntry]] = defaultdict(list)
    for entry in entries:
        if entry.visible_in_palette:
            grouped[entry.palette_name].append(entry)
    return {name: tuple(values) for name, values in grouped.items()}
