from __future__ import annotations

from pyrme.rendering import (
    SpriteAtlas,
    SpriteDrawAssetInputs,
    StaticSpriteDrawAssetProvider,
)
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
