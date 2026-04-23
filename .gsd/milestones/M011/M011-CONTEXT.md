# M011 - Sprite Asset Provider

## Context

`M010/S01` proved live sprite draw diagnostics from `CanvasFrame` data when tests inject a fixture `SpriteCatalog` and `SpriteAtlas` directly into the canvas host.

The next narrow renderer step is to stop making the canvas own raw catalog/atlas wiring directly. It should consume a provider that returns both draw assets as one unit, while preserving the old fixture input seam for focused tests.

## Constraints

- No real DAT/SPR file loading.
- No pixel decoding.
- No atlas texture construction or GL upload.
- No sprite painting, screenshots, lighting, or `wgpu`.
- Explicit `set_sprite_draw_plan()` remains a manual override.
- Provider failures must not keep stale sprite commands visible.

## Source Of Truth

- Legacy renderer behavior remains in `remeres-map-editor-redux`.
- Python tests define the current safe renderer-planning contract.
