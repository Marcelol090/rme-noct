from __future__ import annotations

import inspect

import pyrme.rendering.frame_plan as frame_plan_module
from pyrme.editor import MapModel, MapPosition, TileState
from pyrme.rendering.frame_plan import build_render_frame_plan
from pyrme.rendering.sprite_catalog_adapter import (
    DatSpriteRecord,
    SprFrameRecord,
    build_sprite_catalog_from_asset_records,
    build_sprite_catalog_from_dat_records,
)
from pyrme.rendering.sprite_frame import build_sprite_frame
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def _viewport() -> EditorViewport:
    viewport = EditorViewport(
        ViewportSnapshot(center_x=32000, center_y=32000, floor=7)
    )
    viewport.set_view_size(128, 128)
    return viewport


def test_dat_sprite_records_build_sprite_catalog_entries_with_metadata() -> None:
    catalog = build_sprite_catalog_from_dat_records(
        (
            DatSpriteRecord(
                item_id=2148,
                sprite_id=9001,
                name="Gold Coin",
                flags=frozenset({"stackable", "pickupable"}),
            ),
        )
    )

    entry = catalog.resolve(2148)

    assert entry is not None
    assert entry.sprite_id == 9001
    assert entry.metadata is not None
    assert entry.metadata["source"] == "dat"
    assert entry.metadata["name"] == "Gold Coin"
    assert entry.metadata["flags"] == ("pickupable", "stackable")


def test_spr_frame_records_attach_sorted_sprite_frame_metadata() -> None:
    catalog = build_sprite_catalog_from_asset_records(
        dat_records=(
            DatSpriteRecord(item_id=2148, sprite_id=9001, name="Gold Coin"),
        ),
        spr_frames=(
            SprFrameRecord(sprite_id=9001, frame_index=1, width=32, height=32),
            SprFrameRecord(
                sprite_id=9001,
                frame_index=0,
                width=32,
                height=32,
                offset_x=4,
                offset_y=-2,
            ),
            SprFrameRecord(sprite_id=9999, frame_index=0, width=16, height=16),
        ),
    )

    entry = catalog.resolve(2148)

    assert entry is not None
    assert entry.metadata is not None
    assert entry.metadata["sprite_frames"] == (
        {
            "frame_index": 0,
            "size": (32, 32),
            "offset": (4, -2),
            "archive_offset": 0,
        },
        {
            "frame_index": 1,
            "size": (32, 32),
            "offset": (0, 0),
            "archive_offset": 0,
        },
    )


def test_dat_only_catalog_uses_empty_sprite_frame_metadata() -> None:
    catalog = build_sprite_catalog_from_dat_records(
        (DatSpriteRecord(item_id=100, sprite_id=9100),)
    )

    entry = catalog.resolve(100)

    assert entry is not None
    assert entry.metadata is not None
    assert entry.metadata["sprite_frames"] == ()


def test_dat_sprite_catalog_feeds_existing_sprite_frame_resolution() -> None:
    map_model = MapModel()
    map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=2148,
            item_ids=(100, 101),
        )
    )
    plan = build_render_frame_plan(map_model, _viewport())
    catalog = build_sprite_catalog_from_dat_records(
        (
            DatSpriteRecord(item_id=2148, sprite_id=9001, name="Stone Floor"),
            DatSpriteRecord(item_id=100, sprite_id=9100, name="Torch"),
        )
    )

    frame = build_sprite_frame(plan, catalog)

    tile = frame.tile_commands[0]
    assert tile.ground_entry is not None
    assert tile.ground_entry.sprite_id == 9001
    assert [entry.sprite_id for entry in tile.item_entries] == [9100]
    assert tile.unresolved_item_ids == (101,)
    assert frame.unresolved_item_ids == (101,)


def test_dat_adapter_keeps_frame_planning_free_of_dat_database_imports() -> None:
    source = inspect.getsource(frame_plan_module)

    assert "DatDatabase" not in source
    assert "sprite_catalog_adapter" not in source
