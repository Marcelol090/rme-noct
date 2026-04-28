# M009 — Sprite Draw Diagnostics Context

## Goal

Expose sprite draw plan diagnostics through the canvas host without painting pixels.

## Current State

- `CANVAS-60-SPRITE-CATALOG-SEAM` resolves frame-plan item ids into sprite entries.
- `CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` feeds DAT-like item records into the catalog.
- `CANVAS-80-SPR-FRAME-METADATA` attaches SPR-like frame metadata.
- `CANVAS-90-SPRITE-DRAW-COMMAND-PLAN` builds pure atlas-backed sprite draw commands.
- The renderer host still draws only diagnostic tile rectangles and text.

## Boundary

`S01 / CANVAS-100-SPRITE-DRAW-DIAGNOSTICS` adds a shell-facing seam for `SpriteDrawPlan` diagnostics. It reports command counts and unresolved sprite ids through `PlaceholderCanvasWidget` and `RendererHostCanvasWidget`, but does not connect live catalog generation or paint sprite pixels.

## Decisions

- `SpriteDrawPlan` remains data owned by the rendering layer.
- Canvas widgets expose a protocol method for accepting a plan.
- Diagnostics stay textual and honest until an actual sprite paint path exists.
- Real atlas textures, file parsing, GL upload, lighting, and screenshots remain follow-on work.
