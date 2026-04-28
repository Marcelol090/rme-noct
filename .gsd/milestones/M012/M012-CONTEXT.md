# M012 - Sprite Asset Bundle

## Context

`M011/S01` added the provider seam: canvas hosts can consume a `SpriteDrawAssetProvider` that returns `SpriteCatalog` and `SpriteAtlas` inputs together.

The next narrow step is a fixture asset bundle owner. It groups already-materialized DAT-like item records, SPR-like frame records, and atlas regions, then exposes them through the same provider interface.

## Constraints

- No real DAT/SPR file discovery.
- No binary parsing.
- No pixel decoding.
- No atlas texture construction or GL upload.
- No sprite painting, screenshots, lighting, or `wgpu`.

## Source Of Truth

- `pyrme.rendering.sprite_catalog_adapter` owns DAT-like and SPR-like record adaptation.
- `pyrme.rendering.sprite_draw_commands` owns atlas region lookup and draw command planning.
- `pyrme.rendering.sprite_asset_provider` owns provider assembly only.
