---
provides:
  - CANVAS-80-SPR-FRAME-METADATA
key_files:
  - pyrme/rendering/sprite_catalog_adapter.py
  - pyrme/rendering/__init__.py
  - tests/python/test_sprite_catalog_adapter.py
key_decisions:
  - SPR-like frame metadata is attached by adapter records, not by frame planning.
  - Metadata includes frame index, size, and offset only.
  - Real SPR parsing and atlas placement remain future work.
---

# M007 Summary

`CANVAS-80-SPR-FRAME-METADATA` is complete: SPR-like frame records now attach sorted, deterministic frame metadata to matching `SpriteCatalog` entries by `sprite_id`.

Remaining gaps: real SPR parsing, sprite pixel extraction, texture atlas lookup, real tile sprite painting, lighting, screenshots, and `wgpu`.
