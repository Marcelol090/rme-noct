from __future__ import annotations

from pyrme.editor import MapModel, MapPosition, TileState
from pyrme.rendering.frame_plan import build_render_frame_plan
from pyrme.rendering.sprite_catalog_adapter import (
    DatSpriteRecord,
    SprFrameRecord,
    build_sprite_catalog_from_asset_records,
)
from pyrme.rendering.sprite_draw_commands import (
    SpriteAtlas,
    SpriteAtlasRegion,
    build_sprite_draw_plan,
)
from pyrme.rendering.sprite_frame import build_sprite_frame
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def _viewport() -> EditorViewport:
    viewport = EditorViewport(
        ViewportSnapshot(center_x=32000, center_y=32000, floor=7)
    )
    viewport.set_view_size(128, 128)
    return viewport


def _sprite_frame():
    map_model = MapModel()
    map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=2148,
            item_ids=(100, 101),
        )
    )
    viewport = _viewport()
    frame_plan = build_render_frame_plan(map_model, viewport)
    catalog = build_sprite_catalog_from_asset_records(
        dat_records=(
            DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground"),
            DatSpriteRecord(item_id=100, sprite_id=9100, name="Torch"),
            DatSpriteRecord(item_id=101, sprite_id=9101, name="Unmapped"),
        ),
        spr_frames=(
            SprFrameRecord(
                sprite_id=9001,
                frame_index=0,
                width=32,
                height=32,
                offset_x=0,
                offset_y=0,
            ),
            SprFrameRecord(
                sprite_id=9100,
                frame_index=0,
                width=16,
                height=24,
                offset_x=8,
                offset_y=-4,
            ),
        ),
    )
    return build_sprite_frame(frame_plan, catalog), viewport


def test_sprite_draw_plan_builds_ordered_commands_from_atlas_regions() -> None:
    sprite_frame, viewport = _sprite_frame()
    atlas = SpriteAtlas(
        (
            SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32)),
            SpriteAtlasRegion(sprite_id=9100, source_rect=(32, 0, 16, 24)),
        )
    )

    draw_plan = build_sprite_draw_plan(sprite_frame, atlas, viewport)

    assert len(draw_plan.commands) == 2
    assert [command.layer for command in draw_plan.commands] == [0, 1]
    assert [command.sprite_id for command in draw_plan.commands] == [9001, 9100]
    assert draw_plan.commands[0].destination_rect == (64, 64, 32, 32)
    assert draw_plan.commands[0].source_rect == (0, 0, 32, 32)
    assert draw_plan.commands[1].destination_rect == (72, 60, 16, 24)
    assert draw_plan.commands[1].source_rect == (32, 0, 16, 24)
    assert draw_plan.unresolved_sprite_ids == (9101,)


def test_sprite_draw_plan_reports_missing_atlas_regions_deterministically() -> None:
    sprite_frame, viewport = _sprite_frame()
    atlas = SpriteAtlas(())

    draw_plan = build_sprite_draw_plan(sprite_frame, atlas, viewport)

    assert draw_plan.commands == ()
    assert draw_plan.unresolved_sprite_ids == (9001, 9100, 9101)


def test_sprite_draw_plan_does_not_emit_zero_size_commands_without_frame_metadata() -> None:
    map_model = MapModel()
    map_model.set_tile(TileState(position=MapPosition(32000, 32000, 7), ground_item_id=2148))
    viewport = _viewport()
    frame_plan = build_render_frame_plan(map_model, viewport)
    catalog = build_sprite_catalog_from_asset_records(
        dat_records=(DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground"),),
        spr_frames=(),
    )
    sprite_frame = build_sprite_frame(frame_plan, catalog)
    atlas = SpriteAtlas((SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32)),))

    draw_plan = build_sprite_draw_plan(sprite_frame, atlas, viewport)

    assert draw_plan.commands == ()
    assert draw_plan.unresolved_sprite_ids == (9001,)


def test_sprite_draw_plan_stays_pixel_free() -> None:
    region = SpriteAtlasRegion(sprite_id=1, source_rect=(0, 0, 32, 32))

    assert not hasattr(region, "pixels")
