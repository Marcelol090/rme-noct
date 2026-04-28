# S01 - CANVAS-130-SPRITE-ASSET-BUNDLE

## Summary

Add a fixture asset bundle provider that groups DAT-like records, SPR-like frame records, and atlas regions into provider inputs.

## Must-Haves

- Add `SpriteDrawAssetBundle`.
- Add `build_sprite_draw_asset_bundle()` that snapshots incoming iterables.
- Bundle must implement `sprite_draw_inputs()`.
- Bundle must reuse existing catalog adapter and atlas region planner types.
- Bundle must not load files, decode pixels, upload textures, paint sprites, capture screenshots, handle lighting, or introduce `wgpu`.

## Tasks

- [x] T01 - Add failing bundle provider tests.
- [x] T02 - Implement bundle provider and exports.
- [x] T03 - Verify focused and adjacent render/sprite tests.
- [x] T04 - Document and summarize the slice.

## Verification

```bash
python3 -m pytest tests/python/test_sprite_asset_provider.py -q --tb=short
python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_sprite_asset_provider.py tests/python/test_canvas_seam_m4.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_sprite_draw_commands.py tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q --tb=short
python3 -m ruff check pyrme/rendering/sprite_asset_provider.py pyrme/rendering/__init__.py tests/python/test_sprite_asset_provider.py
git diff --check
```

## Out Of Scope

- Real DAT/SPR file loading.
- Real atlas texture construction.
- OpenGL sprite drawing.
- Screenshot capture.
- Lighting.
- `wgpu`.
