# S01 - CANVAS-40-RENDER-FRAME-PLAN

## Goal

Create a renderer frame-plan seam that converts real map state plus the active viewport into stable tile draw commands.

## Must Haves

- `MapModel` exposes tiles in stable map-position order.
- A pure `CanvasFrame` includes only tiles on the active floor and inside `EditorViewport.visible_rect()`.
- `CanvasFrame.map_generation` mirrors the incremental `MapModel.generation` integer.
- `CanvasTile.screen_rect` is derived from `EditorViewport.map_to_screen()` with less than 1px position error at 100% zoom.
- Missing editor context or map state produces an empty frame instead of breaking canvas initialization.
- The plan preserves ground item and stack item IDs without doing sprite lookup.
- `RendererHostCanvasWidget` reports a frame-plan diagnostic through an optional canvas seam.
- Existing canvas shell behavior remains unchanged.

## Non Goals

- No actual OpenGL sprite drawing.
- No sprite atlas loading.
- No screenshots.
- No `wgpu`.

## Verification

- `tests/python/test_canvas_frame_model.py`
- `tests/python/test_render_frame_plan.py`
- `tests/python/test_renderer_frame_plan_integration.py`
- Existing M002 canvas and viewport regression batch.
