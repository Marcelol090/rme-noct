# M037 Sprite Draw Plan Context

## Source

Renderer gap after PR #86 merge: sprite draw diagnostics tests exist, but canvas host no longer exposes the draw-plan seam.

## Current State

- `SpriteDrawPlan`, `SpriteAtlas`, `SpriteFrame`, and asset-provider inputs exist in `pyrme/rendering`.
- `tests/python/test_canvas_sprite_draw_diagnostics.py` covers explicit plan injection, live catalog/atlas input, and provider refresh.
- `pyrme/ui/canvas_host.py` currently reports frame primitives and sprite resource diagnostics only.
- `pyrme/rendering/__init__.py` does not export sprite draw asset inputs.

## Slice Boundary

M037/S01 restores diagnostic sprite draw plan wiring only. It does not draw sprites or load assets.

