from __future__ import annotations

import pytest
from pyrme.rme_core import render

from pyrme.editor import MapPosition
from pyrme.rendering.frame_plan import RenderFramePlan, RenderTileCommand
from pyrme.rendering.frame_sprite_resources import build_frame_sprite_resources
from pyrme.rendering.sprite_resolver import SpriteItemMetadata, SpriteResourceResolver
from pyrme.ui.viewport import ViewportSnapshot

SPRITE_BYTE_LEN = 32 * 32 * 4


def _sprite_pixels(seed: int) -> bytes:
    return bytes((seed + index) % 256 for index in range(SPRITE_BYTE_LEN))


def _resolved_frame_payload() -> list[dict[str, object]]:
    frame_plan = RenderFramePlan(
        viewport=ViewportSnapshot(floor=7),
        visible_rect=(32000.0, 32000.0, 1.0, 1.0),
        tile_commands=(
            RenderTileCommand(
                position=MapPosition(32000, 32000, 7),
                ground_item_id=2148,
                item_ids=(3031,),
            ),
        ),
    )
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
            3031: SpriteItemMetadata(item_id=3031, sprite_ids=(77,)),
        },
        sprites={
            55: _sprite_pixels(1),
            77: _sprite_pixels(2),
        },
    )

    return [
        {
            "x": resource.position.x,
            "y": resource.position.y,
            "layer": resource.stack_layer,
            "sprite_id": resource.result.sprite_id,
            "pixels": resource.result.pixels,
        }
        for resource in build_frame_sprite_resources(frame_plan, resolver)
        if resource.result.available
    ]


def test_render_frame_serializes_resolved_sprite_resources_to_typed_frame() -> None:
    atlas = render.SpriteAtlas()
    payload = _resolved_frame_payload()

    processed = atlas.render_frame(payload)

    assert processed == 2
    assert atlas.last_frame_sprite_ids() == [55, 77]
    assert atlas.last_frame_positions() == [(32000, 32000, 0), (32000, 32000, 1)]
    assert atlas.last_frame_pixel_byte_lens() == [SPRITE_BYTE_LEN, SPRITE_BYTE_LEN]


def test_render_frame_rejects_missing_sprite_id() -> None:
    atlas = render.SpriteAtlas()
    payload = _resolved_frame_payload()
    del payload[0]["sprite_id"]

    with pytest.raises(TypeError, match="sprite_id"):
        atlas.render_frame(payload)


def test_render_frame_rejects_wrong_field_type() -> None:
    atlas = render.SpriteAtlas()
    payload = _resolved_frame_payload()
    payload[0]["x"] = "32000"

    with pytest.raises(TypeError, match="x"):
        atlas.render_frame(payload)


def test_render_frame_rejects_oversized_single_sprite_pixels() -> None:
    atlas = render.SpriteAtlas()
    payload = _resolved_frame_payload()
    payload[0]["pixels"] = b"\x00" * (SPRITE_BYTE_LEN * 2)

    with pytest.raises(ValueError, match=str(SPRITE_BYTE_LEN)):
        atlas.render_frame(payload)
