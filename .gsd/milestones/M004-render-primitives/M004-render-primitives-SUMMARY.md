---
provides:
  - CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES
key_files:
  - pyrme/rendering/diagnostic_primitives.py
  - pyrme/ui/canvas_host.py
  - pyrme/ui/main_window.py
key_decisions:
  - Diagnostic primitives precede sprite atlas rendering.
---

# M004-render-primitives Summary

`CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES` is complete: verified frame-plan tile commands now project into screen-space diagnostic rectangles, and the renderer host receives and reports those primitives.

Remaining gaps: sprite atlas lookup, real item artwork, floor/layer visual rules, lighting, screenshots, and `wgpu`.
