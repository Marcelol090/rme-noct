# S01 — CANVAS-80-SPR-FRAME-METADATA

## Summary

Attach SPR-like frame metadata to renderer sprite catalog entries without adding real SPR parsing, image decoding, atlas placement, or sprite drawing.

## Must-Haves

- Add an SPR-like frame record contract for sprite id, frame index, size, and offset.
- Build `SpriteCatalog` entries from DAT-like records plus SPR-like frame records.
- Attach only matching frame metadata by `sprite_id`.
- Sort frame metadata by frame index.
- Preserve DAT-only catalog behavior with empty frame metadata.
- Do not add file parsing, atlas loading, image decoding, screenshots, or `wgpu` work.

## Tasks

- [x] T01 — Define `SprFrameRecord`.
- [x] T02 — Join SPR-like frame records into catalog metadata by `sprite_id`.
- [x] T03 — Verify DAT-only behavior and adjacent sprite-frame regressions.
- [x] T04 — Verify, summarize, and decide the next renderer slice.

## Verification

```bash
python3 -m pytest tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q
python3 -m ruff check pyrme/rendering tests/python
```

## Out Of Scope

- Real SPR parsing.
- Sprite pixel extraction.
- Texture atlas placement.
- Real map sprite painting.
- Screenshot capture.
- `QOpenGLWidget` validity under offscreen CI.
