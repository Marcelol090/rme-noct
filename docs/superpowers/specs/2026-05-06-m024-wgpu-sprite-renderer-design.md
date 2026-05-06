# M024 WGPU Sprite Renderer Design

## Source

M023 staged resolved sprite payloads in Rust through `render.SpriteAtlas` and left real GPU upload/draw/readback to M024. PR #89 (`M037/S01: restore sprite draw plan`) is still open, so implementation must wait for that PR to merge or be explicitly stacked.

Context7 source for WGPU API details: `/gfx-rs/wgpu/wgpu-v29.0.1`.

## Goal

Render staged 32x32 RGBA sprite payloads through a real headless WGPU path and return deterministic RGBA bytes to Python.

## Current State

- `crates/rme_core/src/render/sprite_atlas.rs` validates sprite payload shape and records frame commands with `(x, y, layer, sprite_id, pixels)`.
- `crates/rme_core/src/render/sprite.wgsl` already describes a textured quad shader with `texture_2d_array<f32>`, sampler, and `SpriteUniforms`.
- `crates/rme_core/src/render/mod.rs` exports `sprite_atlas` and `sprite_shader`.
- `crates/rme_core/src/lib.rs` does not yet expose a Python `render` submodule, so M024 must make that boundary explicit.
- Python tests already serialize frame-plan sprite resources into `render.SpriteAtlas.render_frame()`.

## Design

Add a focused Rust module at `crates/rme_core/src/render/wgpu_sprite_renderer.rs`.

The renderer owns a WGPU instance, adapter, device, queue, output texture, sprite texture array, bind groups, render pipeline, and readback staging buffer. It renders into an offscreen `Rgba8Unorm` texture with `TextureUsages::RENDER_ATTACHMENT | COPY_SRC`. Readback uses `copy_texture_to_buffer`, `MAP_READ`, and row padding aligned to WGPU's 256-byte copy pitch requirement. The public result strips padded rows and returns tightly packed RGBA bytes.

Python keeps using `render.SpriteAtlas` as the entry point. `SpriteAtlas.render_frame()` remains the staging call; a new `render_headless(width, height)` method asks the Rust renderer to draw the last staged frame and returns a dict with `width`, `height`, `rgba`, `rendered_sprite_count`, and `missing_sprite_count`.

No Qt-native WGPU surface is introduced. `RendererHostCanvasWidget` stays an OpenGL diagnostic host until a later UI slice consumes headless RGBA output.

## Scope

- Add `wgpu = "29.0.1"` to `rme_core`.
- Add exact headless renderer contract and unit tests.
- Upload staged sprite pixels into a texture array and render textured quads through WGPU.
- Read back a tightly packed RGBA buffer.
- Expose the result through `pyrme.rme_core.render.SpriteAtlas`.
- Add focused Python bridge tests for the new result shape and pixel evidence.
- Record GSD M024/S01 plan artifacts.

## Non-Goals

- No CPU rendering fallback.
- No Qt surface or swapchain integration.
- No minimap integration.
- No live canvas painting changes.
- No SPR decoding changes.
- No atlas packing beyond one 32x32 RGBA layer per staged sprite.
- No lighting, animation, blend modes, floor ghosting, or selection overlays.

## Contracts

### Sprite Input

Each sprite command contains:

```text
x: u32
y: u32
layer: u32
sprite_id: u32
pixels: 4096 bytes of RGBA8
```

Pixel length remains `32 * 32 * 4`. Invalid lengths still raise `ValueError`.

### Headless Output

`SpriteAtlas.render_headless(width, height)` returns:

```python
{
    "width": width,
    "height": height,
    "rgba": bytes,
    "rendered_sprite_count": int,
    "missing_sprite_count": int,
}
```

`len(rgba) == width * height * 4`. Rows are tightly packed even though internal WGPU readback rows are padded to 256 bytes.

### Unavailable Adapter

If WGPU cannot create an adapter/device, the renderer raises a clear runtime error:

```text
WGPU renderer unavailable: no compatible adapter
```

This is not a CPU fallback. It is an explicit environment failure.

## Acceptance

- Empty render returns a buffer filled with clear RGBA `(10, 10, 18, 255)`.
- Rendering one solid red sprite changes exactly the covered 32x32 output region to red.
- Rendering two stacked sprites at the same tile draws the higher layer last.
- Python can call `render.SpriteAtlas.render_headless()` after `render_frame()`.
- `rendered_sprite_count` matches staged commands drawn by WGPU.
- `missing_sprite_count` is zero for validated staged payloads.
- `cargo test -p rme_core` passes with the documented PyO3 Python 3.12 environment.
- Focused Python bridge tests pass after rebuilding the native module.

## Implementation Gate

Do not implement this slice until one condition is true:

- PR #89 is merged into `origin/main`, then create a fresh implementation worktree from updated `origin/main`.
- User explicitly approves stacking M024 implementation on top of the current unmerged PR lineage.
