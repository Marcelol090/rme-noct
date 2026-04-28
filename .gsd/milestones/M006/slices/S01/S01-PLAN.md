# S01 — CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER

## Summary

Create an adapter seam that converts DAT-like item sprite records into `SpriteCatalog` entries without moving DAT parsing or DAT dependencies into renderer frame planning.

## Must-Haves

- Add a DAT-like record contract for item id, sprite id, name, and flags.
- Build `SpriteCatalog` instances from those records.
- Populate deterministic metadata at adapter level.
- Prove the resulting catalog feeds existing `build_sprite_frame` resolution.
- Prove frame planning remains free of DAT adapter imports.
- Do not add file parsing, atlas loading, image decoding, screenshots, or `wgpu` work.

## Tasks

- [x] T01 — Define `DatSpriteRecord`.
- [x] T02 — Convert DAT-like records into `SpriteCatalogEntry` values.
- [x] T03 — Verify integration with `build_sprite_frame` and unresolved IDs.
- [x] T04 — Verify, summarize, and decide the next renderer slice.

## Verification

```bash
python3 -m pytest tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py -q
python3 -m ruff check pyrme/rendering tests/python/test_sprite_catalog_adapter.py tests/python/test_sprite_frame.py
```

## Out Of Scope

- Real DAT parsing.
- SPR parsing or frame extraction.
- Texture atlas loading.
- Real map sprite painting.
- Screenshot capture.
- `QOpenGLWidget` validity under offscreen CI.
