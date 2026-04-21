"""Pure frame sprite resource records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyrme.editor import MapPosition
    from pyrme.rendering.frame_plan import RenderFramePlan
    from pyrme.rendering.sprite_resolver import SpriteResourceResolver, SpriteResourceResult


@dataclass(frozen=True, slots=True)
class FrameSpriteResource:
    """Resolved sprite resource attached to a frame tile command."""

    position: MapPosition
    item_id: int
    stack_layer: int
    result: SpriteResourceResult


def build_frame_sprite_resources(
    frame_plan: RenderFramePlan,
    resolver: SpriteResourceResolver,
) -> tuple[FrameSpriteResource, ...]:
    """Resolve ordered sprite resources from a render frame plan."""

    resources: list[FrameSpriteResource] = []
    for command in frame_plan.tile_commands:
        if command.ground_item_id is not None:
            resources.append(
                FrameSpriteResource(
                    position=command.position,
                    item_id=command.ground_item_id,
                    stack_layer=0,
                    result=resolver.resolve_item(command.ground_item_id),
                )
            )
        for stack_layer, item_id in enumerate(command.item_ids, start=1):
            resources.append(
                FrameSpriteResource(
                    position=command.position,
                    item_id=item_id,
                    stack_layer=stack_layer,
                    result=resolver.resolve_item(item_id),
                )
            )
    return tuple(resources)
