# S01 - CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES

## Goal

Convert renderer frame-plan tile commands into screen-space diagnostic primitives consumed by `RendererHostCanvasWidget`.

## Must Haves

- A pure builder maps tile commands to stable widget-space rectangles through `EditorViewport.map_to_screen()`.
- Primitive size follows viewport zoom.
- Primitive order preserves frame-plan order.
- `RendererHostCanvasWidget` receives primitive tuples through an explicit optional seam.
- Diagnostics expose primitive count.

## Non Goals

- No sprite atlas lookup.
- No real item artwork.
- No lighting, animations, screenshots, or `wgpu`.

## Verification

- `tests/python/test_diagnostic_tile_primitives.py`
- `tests/python/test_renderer_frame_plan_integration.py`
- Existing M003/M002 regression batch.
