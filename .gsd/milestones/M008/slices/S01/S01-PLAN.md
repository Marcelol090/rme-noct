# S01 — CANVAS-90-SPRITE-DRAW-COMMAND-PLAN

## Summary

Create pure sprite draw command planning from resolved `SpriteFrame` data plus atlas region metadata, without painting or uploading textures.

## Must-Haves

- Add atlas region and atlas lookup contracts.
- Add draw command and draw plan data contracts.
- Build commands in stable ground-then-stack order.
- Use SPR frame size and offset metadata to compute destination rectangles.
- Report missing atlas regions or missing frame metadata as deterministic sorted `unresolved_sprite_ids`.
- Do not add real atlas textures, image bytes, GL drawing, screenshots, lighting, or `wgpu` work.

## Tasks

- [x] T01 — Define `SpriteAtlas` and `SpriteAtlasRegion`.
- [x] T02 — Define sprite draw command/plan contracts.
- [x] T03 — Build sprite draw plans from `SpriteFrame`, atlas regions, and viewport math.
- [x] T04 — Verify, summarize, and decide the next renderer slice.

## Verification

```bash
python3 -m pytest tests/python/test_sprite_draw_commands.py tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q
python3 -m ruff check pyrme/rendering tests/python
```

## Out Of Scope

- Real atlas texture loading.
- Sprite pixel extraction.
- Renderer host painting.
- Screenshot capture.
- Lighting.
- `QOpenGLWidget` validity under offscreen CI.
