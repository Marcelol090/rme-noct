# M010 Context - Live sprite draw plan integration

## Purpose

M009 proved that canvas hosts can accept explicit `SpriteDrawPlan` values and report command/unresolved diagnostics. The next renderer risk is that those diagnostics are still manually injected instead of being derived from the live canvas frame.

## Boundary

This milestone connects the existing live `CanvasFrame` to fixture `SpriteCatalog` and `SpriteAtlas` inputs so the canvas can regenerate sprite draw diagnostics when map/frame state changes.

It does not load real DAT/SPR files, build a real atlas texture, upload GL resources, paint sprite pixels, add screenshots, add lighting, or introduce `wgpu`.
