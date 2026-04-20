from __future__ import annotations

import inspect
from collections.abc import Iterator, Mapping
from typing import Any

import pyrme.rendering.sprite_frame as sprite_frame_module
from pyrme.editor import MapModel, MapPosition, TileState
from pyrme.rendering.frame_plan import build_render_frame_plan
from pyrme.rendering.sprite_frame import (
    SpriteCatalog,
    SpriteCatalogEntry,
    build_sprite_frame,
)
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def _viewport() -> EditorViewport:
    viewport = EditorViewport(
        ViewportSnapshot(center_x=32000, center_y=32000, floor=7)
    )
    viewport.set_view_size(128, 128)
    return viewport


class MetadataThatFailsOnRead(Mapping[str, Any]):
    def __getitem__(self, key: str) -> Any:
        raise AssertionError(f"metadata should not be read: {key}")

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("metadata should not be iterated")

    def __len__(self) -> int:
        raise AssertionError("metadata length should not be read")


def test_sprite_catalog_entry_metadata_defaults_to_none() -> None:
    entry = SpriteCatalogEntry(item_id=2148, sprite_id=2148)

    assert entry.metadata is None


def test_sprite_frame_resolves_ground_and_stack_items_without_reading_metadata() -> None:
    map_model = MapModel()
    map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=2148,
            item_ids=(100, 101),
        )
    )
    plan = build_render_frame_plan(map_model, _viewport())
    catalog = SpriteCatalog(
        (
            SpriteCatalogEntry(
                item_id=2148,
                sprite_id=9001,
                metadata=MetadataThatFailsOnRead(),
            ),
            SpriteCatalogEntry(item_id=100, sprite_id=9100),
            SpriteCatalogEntry(item_id=101, sprite_id=9101),
        )
    )

    frame = build_sprite_frame(plan, catalog)

    tile = frame.tile_commands[0]
    assert tile.ground_entry is not None
    assert tile.ground_entry.item_id == 2148
    assert tile.ground_entry.sprite_id == 9001
    assert [entry.sprite_id for entry in tile.item_entries] == [9100, 9101]
    assert tile.unresolved_item_ids == ()
    assert frame.unresolved_item_ids == ()


def test_sprite_frame_reports_sorted_unique_unresolved_item_ids() -> None:
    map_model = MapModel()
    map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=500,
            item_ids=(300, 2148, 300),
        )
    )
    map_model.set_tile(
        TileState(
            position=MapPosition(32001, 32000, 7),
            ground_item_id=500,
            item_ids=(100,),
        )
    )
    plan = build_render_frame_plan(map_model, _viewport())
    catalog = SpriteCatalog((SpriteCatalogEntry(item_id=2148, sprite_id=2148),))

    frame = build_sprite_frame(plan, catalog)

    assert frame.unresolved_item_ids == (100, 300, 500)
    assert frame.tile_commands[0].unresolved_item_ids == (300, 500)
    assert frame.tile_commands[1].unresolved_item_ids == (100, 500)


def test_sprite_frame_module_does_not_import_dat_database() -> None:
    source = inspect.getsource(sprite_frame_module)

    assert "DatDatabase" not in source
