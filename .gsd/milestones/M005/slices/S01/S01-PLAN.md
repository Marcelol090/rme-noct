# S01 — CANVAS-60-SPRITE-CATALOG-SEAM

## Summary

Define the renderer-facing sprite catalog seam that lets frame planning distinguish resolved and unresolved item IDs without claiming real sprite rendering.

## Must-Haves

- Add `SpriteCatalog` and `SpriteCatalogEntry` data contracts.
- Keep `SpriteCatalogEntry.metadata` as `None` by default.
- Add sprite-frame construction that resolves item IDs through the catalog.
- Report `unresolved_item_ids` deterministically.
- Keep `DatDatabase` adapter-level only; do not import or require it in renderer frame planning.
- Do not add atlas loading, image decoding, screenshots, or `wgpu` work.

## Tasks

- [x] T01 — Define `SpriteCatalog` and `SpriteCatalogEntry` contracts.
- [x] T02 — Build sprite-frame data from existing frame plans without reading metadata.
- [x] T03 — Add unresolved item ID tests and adjacent renderer regressions.
- [x] T04 — Verify, summarize, and decide the next renderer slice.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py tests/python/test_renderer_frame_plan_integration.py -q
.\.venv\Scripts\python.exe -m ruff check pyrme/rendering tests/python
```

WSL verification also covers the new sprite seam test:

```bash
python3 -m pytest tests/python/test_sprite_frame.py tests/python/test_render_frame_plan.py tests/python/test_diagnostic_tile_primitives.py tests/python/test_renderer_frame_plan_integration.py -q
python3 -m ruff check pyrme/rendering tests/python/test_sprite_frame.py
```

## Out Of Scope

- DAT/SPR parsing integration.
- Texture atlas loading.
- Real map sprite painting.
- Screenshot capture.
- `QOpenGLWidget` validity under offscreen CI.
