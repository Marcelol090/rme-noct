# M023: Sprite Rendering Parity

Status: [x] COMPLETE
Branch: `gsd/M023/S01`

## Goal
Implement high-performance sprite rendering parity in Rust core with PyO3 bridge.

## Tasks
- [x] T01: Sprite Buffer [NEW] [sprite_atlas.rs](file:///c:/Users/Marcelo%20Henrique/Desktop/rme-noct/.worktrees/m023-sprite-parity/crates/rme_core/src/render/sprite_atlas.rs)
- [x] T02: WGSL Shader [NEW] [sprite.wgsl](file:///c:/Users/Marcelo%20Henrique/Desktop/rme-noct/.worktrees/m023-sprite-parity/crates/rme_core/src/render/sprite.wgsl)
- [x] T03: Frame Payload [MODIFY] [sprite_atlas.rs](file:///c:/Users/Marcelo%20Henrique/Desktop/rme-noct/.worktrees/m023-sprite-parity/crates/rme_core/src/render/sprite_atlas.rs)
- [x] T04: Canvas Loop [MODIFY] [canvas_host.py](file:///c:/Users/Marcelo%20Henrique/Desktop/rme-noct/.worktrees/m023-sprite-parity/pyrme/ui/canvas_host.py)
- [x] T05: Diagnostics [MODIFY] [canvas_host.py](file:///c:/Users/Marcelo%20Henrique/Desktop/rme-noct/.worktrees/m023-sprite-parity/pyrme/ui/canvas_host.py)
- [x] T06: Invalid & Selected Tiles [MODIFY] [canvas_host.py](file:///c:/Users/Marcelo%20Henrique/Desktop/rme-noct/.worktrees/m023-sprite-parity/pyrme/ui/canvas_host.py)

## Summary
- Implemented `SpriteAtlas` in Rust for CPU staging and validation.
- WGSL shader prepared for future WGPU upload.
- PyO3 bridge supports complex `render_frame` payloads with type-safe extraction.
- `RendererHostCanvasWidget` refactored to use Noct design tokens (Selection 0.2, Invalid 0.4).
- High-contrast diagnostic overlay (Moonstone White on JetBrains Mono) implemented for real-time profiling.
