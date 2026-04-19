"""Diagnostic tile primitives for the renderer host pre-sprite phase."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import TYPE_CHECKING

from pyrme.ui.viewport import TILE_SIZE, EditorViewport

if TYPE_CHECKING:
    from pyrme.editor import MapPosition
    from pyrme.rendering.frame_plan import RenderFramePlan
    from pyrme.ui.viewport import ViewportSnapshot


@dataclass(frozen=True, slots=True)
class DiagnosticTilePrimitive:
    position: MapPosition
    screen_rect: tuple[int, int, int, int]
    label: str


def build_diagnostic_tile_primitives(
    frame_plan: RenderFramePlan,
    viewport: EditorViewport | ViewportSnapshot,
) -> tuple[DiagnosticTilePrimitive, ...]:
    working_viewport = _working_viewport(viewport)
    tile_size = _tile_screen_size(working_viewport)
    return tuple(
        DiagnosticTilePrimitive(
            position=command.position,
            screen_rect=(
                *working_viewport.map_to_screen(
                    command.position.x,
                    command.position.y,
                    command.position.z,
                ),
                tile_size,
                tile_size,
            ),
            label=_tile_label(command.ground_item_id, command.item_ids),
        )
        for command in frame_plan.tile_commands
    )


def _working_viewport(viewport: EditorViewport | ViewportSnapshot) -> EditorViewport:
    if isinstance(viewport, EditorViewport):
        return EditorViewport(viewport.snapshot())
    return EditorViewport(viewport)


def _tile_screen_size(viewport: EditorViewport) -> int:
    return max(1, int(ceil(TILE_SIZE / (viewport.legacy_zoom_scale * viewport.scale_factor))))


def _tile_label(ground_item_id: int | None, item_ids: tuple[int, ...]) -> str:
    base = str(ground_item_id) if ground_item_id is not None else "empty"
    return f"{base} +{len(item_ids)}" if item_ids else base
