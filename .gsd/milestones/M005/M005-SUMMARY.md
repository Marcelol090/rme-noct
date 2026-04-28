---
provides:
  - CANVAS-60-SPRITE-CATALOG-SEAM
key_files:
  - pyrme/rendering/sprite_frame.py
  - pyrme/rendering/__init__.py
  - tests/python/test_sprite_frame.py
key_decisions:
  - Sprite catalog lookup remains a pure renderer seam.
  - SpriteCatalogEntry.metadata defaults to None and is not read by build_sprite_frame.
  - Unresolved item ids are reported as sorted unique ids.
---

# M005 Summary

`CANVAS-60-SPRITE-CATALOG-SEAM` is complete: renderer frame planning now has a pure `SpriteCatalog` and `SpriteFrame` seam that resolves visible ground and stack item ids without claiming real sprite drawing.

Remaining gaps: DAT/SPR parsing integration, atlas lookup, image decoding, real tile sprite painting, lighting, screenshots, and `wgpu`.
