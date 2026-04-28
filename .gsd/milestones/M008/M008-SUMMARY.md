---
provides:
  - CANVAS-90-SPRITE-DRAW-COMMAND-PLAN
key_files:
  - pyrme/rendering/sprite_draw_commands.py
  - pyrme/rendering/__init__.py
  - tests/python/test_sprite_draw_commands.py
key_decisions:
  - Draw planning remains pure data.
  - Atlas lookup uses in-memory regions keyed by sprite id.
  - Missing atlas regions or frame metadata are reported as unresolved sprite ids.
---

# M008 Summary

`CANVAS-90-SPRITE-DRAW-COMMAND-PLAN` is complete: resolved sprite-frame data now converts into deterministic atlas-backed draw command data with source rectangles, destination rectangles, layer order, and missing draw-input reporting.

Remaining gaps: renderer host integration, real atlas textures, pixel extraction, tile sprite painting, lighting, screenshots, and `wgpu`.
