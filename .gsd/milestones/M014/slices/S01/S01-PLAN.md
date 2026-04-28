# S01 - CANVAS-150-CLIENT-ASSET-SIGNATURES

## Summary

Read DAT/SPR signatures from discovered client files without parsing records or decoding pixels.

## Must-Haves

- Add `ClientAssetSignatures`.
- Add `read_client_asset_signatures()`.
- Preserve discovery warnings when discovery is incomplete.
- Read only the first 4 bytes from discovered DAT and SPR files.
- Interpret signatures as little-endian unsigned values.
- Report legacy-style warnings for open failures and short headers.
- Do not parse DAT records, parse SPR frame tables, decode pixels, upload textures, paint sprites, capture screenshots, handle lighting, or introduce `wgpu`.

## Tasks

- [x] T01 - Add failing client asset signature tests.
- [x] T02 - Implement signature reads and warnings.
- [x] T03 - Verify focused and adjacent render/sprite tests.
- [x] T04 - Document and summarize the slice.

## Verification

```bash
python3 -m pytest tests/python/test_client_asset_discovery.py -q --tb=short
python3 -m pytest tests/python/test_client_asset_discovery.py tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_sprite_asset_provider.py tests/python/test_canvas_seam_m4.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_sprite_draw_commands.py tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q --tb=short
python3 -m ruff check pyrme/rendering/client_asset_discovery.py pyrme/rendering/__init__.py tests/python/test_client_asset_discovery.py
python3 -m json.tool .gsd/task-registry.json
git diff --check
```

## Out Of Scope

- DAT item record parsing.
- SPR frame table parsing.
- Pixel decoding.
- Atlas texture construction and GL upload.
- OpenGL sprite drawing.
- Screenshot capture.
- Lighting.
- `wgpu`.
