---
provides:
  - CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER
key_files:
  - pyrme/rendering/sprite_catalog_adapter.py
  - pyrme/rendering/__init__.py
  - tests/python/test_sprite_catalog_adapter.py
key_decisions:
  - DAT-facing metadata lives in the adapter layer.
  - Frame planning remains free of DAT adapter imports.
  - The adapter accepts in-memory records only; real DAT/SPR parsing remains future work.
---

# M006 Summary

`CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` is complete: DAT-like item sprite records now build `SpriteCatalog` entries that can feed the existing sprite-frame resolution seam.

Remaining gaps: real DAT parsing, SPR frame extraction, texture atlas lookup, real tile sprite painting, lighting, screenshots, and `wgpu`.
