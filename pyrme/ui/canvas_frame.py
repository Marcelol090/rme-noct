"""Canvas frame assembly for the pre-sprite renderer host."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import TYPE_CHECKING

from pyrme.ui.viewport import TILE_SIZE, EditorViewport

if TYPE_CHECKING:
    from pyrme.editor import MapPosition
    from pyrme.ui.editor_context import EditorContext
    from pyrme.ui.viewport import ViewportSnapshot


@dataclass(frozen=True, slots=True)
class CanvasTile:
    position: MapPosition
    ground_item_id: int | None
    item_ids: tuple[int, ...]
    screen_rect: tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class CanvasFrame:
    viewport_snapshot: ViewportSnapshot
    visible_rect: tuple[float, float, float, float]
    map_generation: int
    tiles: tuple[CanvasTile, ...]

    @property
    def tile_count(self) -> int:
        return len(self.tiles)

    def summary(self) -> str:
        noun = "tile" if self.tile_count == 1 else "tiles"
        return (
            f"frame plan: {self.tile_count} visible {noun} "
            f"@ floor {self.viewport_snapshot.floor:02d}"
        )


def build_canvas_frame(
    editor_context: EditorContext | None,
    viewport: EditorViewport | ViewportSnapshot,
) -> CanvasFrame:
    working_viewport = _working_viewport(viewport)
    snapshot = working_viewport.snapshot()
    visible_rect = working_viewport.visible_rect()
    map_model = getattr(
        getattr(getattr(editor_context, "session", None), "document", None),
        "map_model",
        None,
    )
    if map_model is None:
        return CanvasFrame(snapshot, visible_rect, 0, ())

    tile_size = _tile_screen_size(working_viewport)
    tiles = tuple(
        CanvasTile(
            position=tile.position,
            ground_item_id=tile.ground_item_id,
            item_ids=tile.item_ids,
            screen_rect=(
                *working_viewport.map_to_screen(
                    tile.position.x,
                    tile.position.y,
                    tile.position.z,
                ),
                tile_size,
                tile_size,
            ),
        )
        for tile in map_model.tiles()
        if tile.position.z == snapshot.floor and _contains_tile(visible_rect, tile.position)
    )
    return CanvasFrame(snapshot, visible_rect, int(map_model.generation), tiles)


def _working_viewport(viewport: EditorViewport | ViewportSnapshot) -> EditorViewport:
    if isinstance(viewport, EditorViewport):
        return EditorViewport(viewport.snapshot())
    return EditorViewport(viewport)


def _contains_tile(
    visible_rect: tuple[float, float, float, float],
    position: MapPosition,
) -> bool:
    min_x, min_y, width, height = visible_rect
    return bool(min_x <= position.x < min_x + width and min_y <= position.y < min_y + height)


def _tile_screen_size(viewport: EditorViewport) -> int:
    return max(1, int(ceil(TILE_SIZE / (viewport.legacy_zoom_scale * viewport.scale_factor))))
