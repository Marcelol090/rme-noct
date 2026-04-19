"""Pure render frame planning before real GL draw passes exist."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyrme.ui.viewport import EditorViewport

if TYPE_CHECKING:
    from pyrme.editor import MapModel, MapPosition
    from pyrme.ui.viewport import ViewportSnapshot


@dataclass(frozen=True, slots=True)
class RenderTileCommand:
    position: MapPosition
    ground_item_id: int | None
    item_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class RenderFramePlan:
    viewport: ViewportSnapshot
    visible_rect: tuple[float, float, float, float]
    tile_commands: tuple[RenderTileCommand, ...]

    @property
    def tile_count(self) -> int:
        return len(self.tile_commands)

    def summary(self) -> str:
        noun = "tile" if self.tile_count == 1 else "tiles"
        return f"frame plan: {self.tile_count} visible {noun} @ floor {self.viewport.floor:02d}"


def build_render_frame_plan(
    map_model: MapModel,
    viewport: EditorViewport | ViewportSnapshot,
) -> RenderFramePlan:
    working_viewport = _working_viewport(viewport)
    snapshot = working_viewport.snapshot()
    visible_rect = working_viewport.visible_rect()
    commands = tuple(
        RenderTileCommand(
            position=tile.position,
            ground_item_id=tile.ground_item_id,
            item_ids=tile.item_ids,
        )
        for tile in map_model.tiles()
        if tile.position.z == snapshot.floor and _contains_tile(visible_rect, tile.position)
    )
    return RenderFramePlan(
        viewport=snapshot,
        visible_rect=visible_rect,
        tile_commands=commands,
    )


def _working_viewport(viewport: EditorViewport | ViewportSnapshot) -> EditorViewport:
    if isinstance(viewport, EditorViewport):
        return EditorViewport(viewport.snapshot())
    return EditorViewport(viewport)


def _contains_tile(
    visible_rect: tuple[float, float, float, float],
    position: MapPosition,
) -> bool:
    min_x, min_y, width, height = visible_rect
    return min_x <= position.x < min_x + width and min_y <= position.y < min_y + height
