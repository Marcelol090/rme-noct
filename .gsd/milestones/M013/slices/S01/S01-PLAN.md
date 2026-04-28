# S01 - CANVAS-140-CLIENT-ASSET-DISCOVERY

## Summary

Discover client DAT/SPR file paths and pair that discovery with fixture sprite asset bundles, without opening the files.

## Must-Haves

- Add `ClientAssetFiles`.
- Add `discover_client_asset_files()`.
- Sanitize configured metadata and sprite names to basenames.
- Prefer configured file names, then fall back to `Tibia.dat` and `Tibia.spr`.
- Report legacy-style warnings for missing root, DAT, or SPR files.
- Add `ClientSpriteAssetBundle` to pair discovered files with an existing bundle provider.
- Do not read signatures, parse binaries, decode pixels, upload textures, paint sprites, capture screenshots, handle lighting, or introduce `wgpu`.

## Tasks

- [x] T01 - Add failing client asset discovery tests.
- [x] T02 - Implement pure discovery and bundle pairing.
- [x] T03 - Verify focused and adjacent render/sprite tests.
- [x] T04 - Document and summarize the slice.

## Verification

```bash
python3 -m pytest tests/python/test_client_asset_discovery.py -q --tb=short
python3 -m pytest tests/python/test_client_asset_discovery.py tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_sprite_asset_provider.py tests/python/test_canvas_seam_m4.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_sprite_draw_commands.py tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q --tb=short
python3 -m ruff check pyrme/rendering/client_asset_discovery.py pyrme/rendering/__init__.py tests/python/test_client_asset_discovery.py
git diff --check
```

## Out Of Scope

- DAT/SPR signature reads.
- DAT/SPR binary parsing.
- Pixel decoding.
- Atlas texture construction and GL upload.
- OpenGL sprite drawing.
- Screenshot capture.
- Lighting.
- `wgpu`.
