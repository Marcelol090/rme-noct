from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from pyrme.editor import MapPosition
from pyrme.rendering.frame_plan import RenderFramePlan, RenderTileCommand
from pyrme.rendering.frame_sprite_resources import (
    FrameSpriteResource,
    build_frame_sprite_resources,
)
from pyrme.rendering.sprite_resolver import (
    SpriteItemMetadata,
    SpriteLookupStatus,
    SpriteResourceResolver,
    SpriteResourceResult,
)
from pyrme.ui.viewport import ViewportSnapshot


def test_frame_sprite_resource_record_exposes_position_item_layer_and_result() -> None:
    result = SpriteResourceResult.resolved(
        item_id=2148,
        sprite_id=55,
        pixels=b"rgba-pixels",
    )

    resource = FrameSpriteResource(
        position=MapPosition(32000, 32000, 7),
        item_id=2148,
        stack_layer=0,
        result=result,
    )

    assert resource.position == MapPosition(32000, 32000, 7)
    assert resource.item_id == 2148
    assert resource.stack_layer == 0
    assert resource.result is result


def test_frame_sprite_resource_record_is_immutable() -> None:
    resource = FrameSpriteResource(
        position=MapPosition(32000, 32000, 7),
        item_id=2148,
        stack_layer=0,
        result=SpriteResourceResult.missing_item(2148),
    )

    with pytest.raises(FrozenInstanceError):
        resource.item_id = 100  # type: ignore[misc]


def test_build_frame_sprite_resources_resolves_ground_items_in_frame_order() -> None:
    first_position = MapPosition(32000, 32000, 7)
    second_position = MapPosition(32001, 32000, 7)
    frame_plan = RenderFramePlan(
        viewport=ViewportSnapshot(floor=7),
        visible_rect=(32000.0, 32000.0, 2.0, 1.0),
        tile_commands=(
            RenderTileCommand(
                position=first_position,
                ground_item_id=2148,
                item_ids=(),
            ),
            RenderTileCommand(
                position=MapPosition(32002, 32000, 7),
                ground_item_id=None,
                item_ids=(),
            ),
            RenderTileCommand(
                position=second_position,
                ground_item_id=2160,
                item_ids=(),
            ),
        ),
    )
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
            2160: SpriteItemMetadata(item_id=2160, sprite_ids=(99,)),
        },
        sprites={
            55: b"gold-coin",
            99: b"crystal-coin",
        },
    )

    resources = build_frame_sprite_resources(frame_plan, resolver)

    assert [
        (resource.position, resource.item_id, resource.stack_layer)
        for resource in resources
    ] == [
        (first_position, 2148, 0),
        (second_position, 2160, 0),
    ]
    assert [resource.result.status for resource in resources] == [
        SpriteLookupStatus.RESOLVED,
        SpriteLookupStatus.RESOLVED,
    ]
    assert [resource.result.pixels for resource in resources] == [
        b"gold-coin",
        b"crystal-coin",
    ]


def test_build_frame_sprite_resources_appends_stack_items_after_tile_ground() -> None:
    first_position = MapPosition(32000, 32000, 7)
    second_position = MapPosition(32001, 32000, 7)
    frame_plan = RenderFramePlan(
        viewport=ViewportSnapshot(floor=7),
        visible_rect=(32000.0, 32000.0, 2.0, 1.0),
        tile_commands=(
            RenderTileCommand(
                position=first_position,
                ground_item_id=2148,
                item_ids=(3031, 3035),
            ),
            RenderTileCommand(
                position=second_position,
                ground_item_id=None,
                item_ids=(2160,),
            ),
        ),
    )
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
            3031: SpriteItemMetadata(item_id=3031, sprite_ids=(77,)),
            3035: SpriteItemMetadata(item_id=3035, sprite_ids=(78,)),
            2160: SpriteItemMetadata(item_id=2160, sprite_ids=(99,)),
        },
        sprites={
            55: b"ground",
            77: b"stack-a",
            78: b"stack-b",
            99: b"stack-only",
        },
    )

    resources = build_frame_sprite_resources(frame_plan, resolver)

    assert [
        (resource.position, resource.item_id, resource.stack_layer)
        for resource in resources
    ] == [
        (first_position, 2148, 0),
        (first_position, 3031, 1),
        (first_position, 3035, 2),
        (second_position, 2160, 1),
    ]
    assert [resource.result.pixels for resource in resources] == [
        b"ground",
        b"stack-a",
        b"stack-b",
        b"stack-only",
    ]


def test_build_frame_sprite_resources_keeps_missing_item_and_sprite_results() -> None:
    frame_plan = RenderFramePlan(
        viewport=ViewportSnapshot(floor=7),
        visible_rect=(32000.0, 32000.0, 1.0, 1.0),
        tile_commands=(
            RenderTileCommand(
                position=MapPosition(32000, 32000, 7),
                ground_item_id=999_999,
                item_ids=(2148,),
            ),
        ),
    )
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
        },
        sprites={},
    )

    resources = build_frame_sprite_resources(frame_plan, resolver)

    assert [(resource.item_id, resource.result.status) for resource in resources] == [
        (999_999, SpriteLookupStatus.MISSING_ITEM),
        (2148, SpriteLookupStatus.MISSING_SPRITE),
    ]
    assert [resource.result.available for resource in resources] == [False, False]
