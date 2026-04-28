# M011 - Sprite Asset Provider Summary

## Result

`M011/S01` adds `SpriteDrawAssetInputs`, `SpriteDrawAssetProvider`, and `StaticSpriteDrawAssetProvider` under `pyrme.rendering`.

Canvas hosts now accept `set_sprite_asset_provider(provider)` and query the provider during live sprite draw synchronization. The older `set_sprite_draw_inputs(catalog, atlas)` fixture seam remains supported, and explicit `set_sprite_draw_plan()` still disables live/provider generation as an override.

## Verification

- `tests/python/test_sprite_asset_provider.py`
- `tests/python/test_canvas_sprite_draw_diagnostics.py`
- Adjacent canvas/render/sprite planning regression paths
- Ruff on touched rendering, canvas, and test files
- `git diff --check`

## Remaining Gaps

- Real DAT/SPR file loading.
- Pixel decoding.
- Atlas texture construction and GL upload.
- Sprite painting, screenshots, lighting, and `wgpu`.
