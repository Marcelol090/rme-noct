from __future__ import annotations

from pyrme.rendering import (
    SpriteAtlas,
    SpriteDrawAssetBundle,
    SpriteDrawAssetInputs,
    StaticSpriteDrawAssetProvider,
    build_sprite_draw_asset_bundle,
)
from pyrme.rendering.sprite_catalog_adapter import DatSpriteRecord, SprFrameRecord
from pyrme.rendering.sprite_draw_commands import SpriteAtlasRegion
from pyrme.rendering.sprite_frame import SpriteCatalog, SpriteCatalogEntry


def test_static_sprite_asset_provider_returns_catalog_and_atlas_inputs() -> None:
    catalog = SpriteCatalog((SpriteCatalogEntry(item_id=2148, sprite_id=9001),))
    atlas = SpriteAtlas(
        (SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32)),)
    )
    provider = StaticSpriteDrawAssetProvider(
        SpriteDrawAssetInputs(catalog=catalog, atlas=atlas)
    )

    inputs = provider.sprite_draw_inputs()

    assert inputs.catalog is catalog
    assert inputs.atlas is atlas


def test_static_sprite_asset_provider_does_not_claim_pixel_loading() -> None:
    catalog = SpriteCatalog(())
    atlas = SpriteAtlas(())
    provider = StaticSpriteDrawAssetProvider(
        SpriteDrawAssetInputs(catalog=catalog, atlas=atlas)
    )

    assert not hasattr(provider, "load_pixels")


def test_sprite_asset_bundle_builds_catalog_and_atlas_inputs_from_records() -> None:
    bundle = SpriteDrawAssetBundle(
        dat_records=(DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground"),),
        spr_frames=(
            SprFrameRecord(
                sprite_id=9001,
                frame_index=0,
                width=32,
                height=32,
                offset_x=4,
                offset_y=-2,
            ),
        ),
        atlas_regions=(
            SpriteAtlasRegion(sprite_id=9001, source_rect=(64, 0, 32, 32)),
        ),
    )

    inputs = bundle.sprite_draw_inputs()

    entry = inputs.catalog.resolve(2148)
    assert entry is not None
    assert entry.sprite_id == 9001
    assert entry.metadata is not None
    assert entry.metadata["sprite_frames"] == (
        {
            "frame_index": 0,
            "size": (32, 32),
            "offset": (4, -2),
        },
    )
    region = inputs.atlas.resolve(9001)
    assert region is not None
    assert region.source_rect == (64, 0, 32, 32)
    assert not hasattr(bundle, "load_pixels")


def test_sprite_asset_bundle_builder_snapshots_record_iterables() -> None:
    dat_records = [DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground")]
    spr_frames = [SprFrameRecord(sprite_id=9001, frame_index=0, width=32, height=32)]
    atlas_regions = [SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32))]

    bundle = build_sprite_draw_asset_bundle(
        dat_records=dat_records,
        spr_frames=spr_frames,
        atlas_regions=atlas_regions,
    )
    dat_records.append(DatSpriteRecord(item_id=100, sprite_id=9100, name="Torch"))
    spr_frames.append(SprFrameRecord(sprite_id=9100, frame_index=0, width=16, height=24))
    atlas_regions.append(SpriteAtlasRegion(sprite_id=9100, source_rect=(32, 0, 16, 24)))

    inputs = bundle.sprite_draw_inputs()

    assert inputs.catalog.item_ids == (2148,)
    assert inputs.atlas.resolve(9001) is not None
    assert inputs.atlas.resolve(9100) is None


def test_sprite_asset_bundle_constructor_snapshots_record_iterables() -> None:
    dat_records = [DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground")]
    spr_frames = [SprFrameRecord(sprite_id=9001, frame_index=0, width=32, height=32)]
    atlas_regions = [SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32))]

    bundle = SpriteDrawAssetBundle(
        dat_records=dat_records,
        spr_frames=spr_frames,
        atlas_regions=atlas_regions,
    )
    dat_records.append(DatSpriteRecord(item_id=100, sprite_id=9100, name="Torch"))
    spr_frames.append(SprFrameRecord(sprite_id=9100, frame_index=0, width=16, height=24))
    atlas_regions.append(SpriteAtlasRegion(sprite_id=9100, source_rect=(32, 0, 16, 24)))

    inputs = bundle.sprite_draw_inputs()

    assert inputs.catalog.item_ids == (2148,)
    assert inputs.atlas.resolve(9001) is not None
    assert inputs.atlas.resolve(9100) is None
