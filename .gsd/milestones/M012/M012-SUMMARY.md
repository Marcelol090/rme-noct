# M012 - Sprite Asset Bundle Summary

## Result

`M012/S01` adds `SpriteDrawAssetBundle` and `build_sprite_draw_asset_bundle()`.

The bundle snapshots DAT-like records, SPR-like frame records, and atlas regions. It implements the same provider surface as `StaticSpriteDrawAssetProvider`, generating `SpriteDrawAssetInputs` on demand from already-materialized records.

## Verification

- `tests/python/test_sprite_asset_provider.py`
- Adjacent canvas/render/sprite planning regression paths
- Ruff on touched rendering and test files
- `git diff --check`

## Remaining Gaps

- Real DAT/SPR discovery and parsing.
- Pixel decoding.
- Atlas texture construction and GL upload.
- Sprite painting, screenshots, lighting, and `wgpu`.
