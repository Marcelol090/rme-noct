# M008 — Sprite Draw Command Plan Context

## Goal

Plan atlas-backed sprite draw commands from resolved sprite-frame data without drawing pixels.

## Current State

- `CANVAS-60-SPRITE-CATALOG-SEAM` resolves item ids into sprite entries.
- `CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` feeds DAT-like item records into the catalog.
- `CANVAS-80-SPR-FRAME-METADATA` attaches SPR-like frame metadata.
- No atlas image, GL upload, pixel decoding, or renderer-host sprite painting exists yet.

## Boundary

`S01 / CANVAS-90-SPRITE-DRAW-COMMAND-PLAN` creates pure command data from `SpriteFrame`, `SpriteAtlas`, and `EditorViewport`. It reports missing atlas regions but does not paint.

## Decisions

- Atlas lookup is represented by in-memory `SpriteAtlasRegion` records.
- Draw commands carry source and destination rectangles only.
- Missing atlas regions or missing frame metadata are reported separately from unresolved item ids.
- Renderer host integration remains a follow-on slice.
