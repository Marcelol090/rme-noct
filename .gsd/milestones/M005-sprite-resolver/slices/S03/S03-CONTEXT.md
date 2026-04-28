# S03 Context - CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS

## Purpose

Surface honest sprite resource diagnostics after S02 resource collection, without drawing sprites or claiming visual parity.

## Existing Inputs

- `FrameSpriteResource` records carry item id, stack layer, position, and `SpriteResourceResult`.
- `build_frame_sprite_resources()` preserves resolver success and failure outcomes.
- `RendererHostCanvasWidget.diagnostic_text()` already reports frame plan, visible tile, map generation, visible rect, and diagnostic primitive counts.

## Honest Boundary

This slice may report counts and missing-resource status text. It must not add sprite drawing, atlas packing, OpenGL/wgpu draw passes, item catalog loading UI, or visual sprite overlays.

## Default Runtime Constraint

The app does not yet load real DAT/SPR sources into the renderer host. Runtime diagnostics may therefore use an explicit empty resolver or injected resolver seam and must label results honestly.
