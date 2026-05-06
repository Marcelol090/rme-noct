"""Pure editor brush placement data shared by UI and backend seams."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BrushPlacementKind(str, Enum):
    GROUND = "ground"
    WALL = "wall"


@dataclass(frozen=True, slots=True)
class EditorBrushPlacement:
    brush_id: int
    name: str
    kind: BrushPlacementKind
    palette_name: str
    item_id: int
    related_item_ids: tuple[int, ...]
    visible_in_palette: bool = True

    @property
    def active_brush_id(self) -> str:
        return f"brush:{self.kind.value}:{self.brush_id}"


def default_editor_brush_placements() -> tuple[EditorBrushPlacement, ...]:
    """Return starter brush placements mirrored from the Rust brush contract."""
    return (
        EditorBrushPlacement(
            10,
            "grass",
            BrushPlacementKind.GROUND,
            "Terrain",
            4526,
            (4526, 4527),
        ),
        EditorBrushPlacement(
            11,
            "dirt",
            BrushPlacementKind.GROUND,
            "Terrain",
            103,
            (103,),
        ),
        EditorBrushPlacement(
            20,
            "stone wall",
            BrushPlacementKind.WALL,
            "Terrain",
            3361,
            (3361, 3362),
        ),
        EditorBrushPlacement(
            21,
            "wooden wall",
            BrushPlacementKind.WALL,
            "Terrain",
            3390,
            (3390,),
        ),
    )


def brush_placement_for_active_id(
    active_brush_id: str | None,
) -> EditorBrushPlacement | None:
    if active_brush_id is None:
        return None
    return next(
        (
            placement
            for placement in default_editor_brush_placements()
            if placement.active_brush_id == active_brush_id
        ),
        None,
    )
