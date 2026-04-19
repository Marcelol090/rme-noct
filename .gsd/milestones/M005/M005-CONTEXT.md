# M005 — Sprite Catalog Seam Context

## Goal

Introduce the first renderer-facing sprite catalog seam after the diagnostic tile primitive milestone.

## Current State

- `CANVAS-40-RENDER-FRAME-PLAN` builds visible tile command plans from `MapModel` and `EditorViewport`.
- `CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES` projects tile commands into diagnostic rectangles.
- No sprite catalog, atlas lookup, DAT/SPR binding, or real sprite drawing is in scope yet.

## Slice Boundary

`S01 / CANVAS-60-SPRITE-CATALOG-SEAM` should define catalog data structures and unresolved-item reporting without moving DAT/SPR parsing into the renderer path.

## Decisions

- `SpriteCatalogEntry.metadata` is `None` by default.
- `build_sprite_frame` does not read metadata during M005.
- `DatDatabase` stays adapter-level only.
- Offscreen `QOpenGLWidget` validity is not required for tests.
