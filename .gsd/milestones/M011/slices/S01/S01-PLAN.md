# S01 - CANVAS-120-SPRITE-ASSET-PROVIDER

## Summary

Move live sprite draw planning from direct catalog/atlas tuple injection toward a provider seam that supplies both draw inputs as a unit.

## Must-Haves

- Add a renderer-facing sprite draw asset provider contract.
- Add a static provider for tests and fixture-backed flows.
- Canvas hosts accept a provider and use it for live sprite draw diagnostics.
- Provider inputs refresh when canvas frame synchronization runs.
- Direct fixture inputs and explicit draw-plan override behavior remain supported.
- The paint path stays diagnostic-only.

## Tasks

- [x] T01 - Add failing provider and canvas integration tests.
- [x] T02 - Add sprite draw asset provider contract and static implementation.
- [x] T03 - Connect canvas live sprite draw planning to the provider seam.
- [x] T04 - Verify and summarize the slice.

## Verification

```bash
python3 -m pytest tests/python/test_sprite_asset_provider.py tests/python/test_canvas_sprite_draw_diagnostics.py -q --tb=short
python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_sprite_asset_provider.py tests/python/test_canvas_seam_m4.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_sprite_draw_commands.py tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q --tb=short
python3 -m ruff check pyrme/rendering/sprite_asset_provider.py pyrme/rendering/__init__.py pyrme/ui/canvas_host.py tests/python/test_sprite_asset_provider.py tests/python/test_canvas_sprite_draw_diagnostics.py
git diff --check
```

## Out Of Scope

- Real DAT/SPR file loading.
- Real atlas texture construction.
- OpenGL sprite drawing.
- Screenshot capture.
- Lighting.
- `wgpu`.
