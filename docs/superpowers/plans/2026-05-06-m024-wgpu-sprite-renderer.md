# M024 WGPU Sprite Renderer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real headless WGPU sprite renderer that draws staged RGBA sprites and exposes tightly packed output bytes to Python.

**Architecture:** Keep the renderer below the PyO3 boundary in `crates/rme_core/src/render`. `SpriteAtlas` remains the Python-facing staging object, while `HeadlessSpriteRenderer` owns WGPU resources, renders to an offscreen texture, and strips padded readback rows before returning RGBA bytes.

**Tech Stack:** Rust 2021, PyO3 0.23, WGPU 29.0.1, WGSL, pollster, pytest, maturin, rtk, WSL Python 3.12.

---

## Context

Design source: `docs/superpowers/specs/2026-05-06-m024-wgpu-sprite-renderer-design.md`

M023 source: `.gsd/M023-SUMMARY.md`

WGPU API source: Context7 `/gfx-rs/wgpu/wgpu-v29.0.1`

Implementation may start only after PR #89 is merged or user explicitly approves a stacked branch.

## Scope Guards

- No CPU fallback.
- No Qt-native WGPU surface.
- No `RendererHostCanvasWidget` paint path change.
- No minimap.
- No SPR decoding.
- No atlas packing beyond one 32x32 layer per staged sprite.
- No lighting, animation, blend modes, floor ghosting, or selection overlays.

## Files

- Modify: `crates/rme_core/Cargo.toml`
- Modify: `crates/rme_core/src/lib.rs`
- Modify: `crates/rme_core/src/render/mod.rs`
- Modify: `crates/rme_core/src/render/sprite_atlas.rs`
- Create: `crates/rme_core/src/render/wgpu_sprite_renderer.rs`
- Create: `tests/python/test_wgpu_sprite_renderer.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M024-wgpu-sprite-renderer/M024-wgpu-sprite-renderer-META.json`
- Modify: `.gsd/milestones/M024-wgpu-sprite-renderer/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M024-wgpu-sprite-renderer/slices/S01/S01-SUMMARY.md`

## Environment

Run from the implementation worktree in WSL:

```bash
cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/<m024-implementation-worktree>"
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e '.[dev]'
export PYTHON312_LIB=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib
export PYO3_PYTHON="$(pwd)/.venv/bin/python"
export LD_LIBRARY_PATH="$PYTHON312_LIB:${LD_LIBRARY_PATH:-}"
export RUSTFLAGS="-L native=$PYTHON312_LIB -l dylib=python3.12"
```

## Task 1: Dependency And Python Render Submodule Gate

**Files:**
- Modify: `crates/rme_core/Cargo.toml`
- Modify: `crates/rme_core/src/lib.rs`
- Modify: `crates/rme_core/src/render/mod.rs`
- Test: `tests/python/test_sprite_rendering.py`

- [ ] **Step 1: Write failing Python export test**

Add this test to `tests/python/test_sprite_rendering.py`:

```python
def test_native_render_submodule_exposes_sprite_atlas() -> None:
    assert hasattr(render, "SpriteAtlas")
    atlas = render.SpriteAtlas()
    assert atlas.mapped_byte_len() == 0
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_sprite_rendering.py::test_native_render_submodule_exposes_sprite_atlas -q --tb=short
```

Expected before export fix: `ImportError` or assertion failure showing `pyrme.rme_core.render` is missing `SpriteAtlas`.

- [ ] **Step 3: Add dependencies**

In `crates/rme_core/Cargo.toml`, replace the old commented WGPU note with:

```toml
wgpu = "29.0.1"
pollster = "0.4"
```

- [ ] **Step 4: Export render module from Rust**

In `crates/rme_core/src/lib.rs`, add:

```rust
pub mod render;
```

Inside `fn rme_core(m: &Bound<'_, PyModule>) -> PyResult<()>`, before `Ok(())`, add:

```rust
let render_module = PyModule::new(m.py(), "render")?;
render::register_python_module(&render_module)?;
m.add_submodule(&render_module)?;
```

In `crates/rme_core/src/render/mod.rs`, replace the file with:

```rust
pub mod sprite_atlas;
pub mod sprite_shader;
pub mod wgpu_sprite_renderer;

use pyo3::prelude::*;

pub fn register_python_module(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<sprite_atlas::SpriteAtlas>()?;
    Ok(())
}
```

- [ ] **Step 5: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_sprite_rendering.py::test_native_render_submodule_exposes_sprite_atlas -q --tb=short
```

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add crates/rme_core/Cargo.toml crates/rme_core/src/lib.rs crates/rme_core/src/render/mod.rs tests/python/test_sprite_rendering.py Cargo.lock
git commit -m "feat(M024/S01): expose render submodule"
```

## Task 2: Headless Renderer Contract

**Files:**
- Create: `crates/rme_core/src/render/wgpu_sprite_renderer.rs`
- Modify: `crates/rme_core/src/render/mod.rs`

- [ ] **Step 1: Write contract tests**

Create `crates/rme_core/src/render/wgpu_sprite_renderer.rs` with tests first:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn padded_bytes_per_row_aligns_to_wgpu_copy_pitch() {
        assert_eq!(padded_bytes_per_row(1), 256);
        assert_eq!(padded_bytes_per_row(32), 256);
        assert_eq!(padded_bytes_per_row(64), 256);
        assert_eq!(padded_bytes_per_row(65), 512);
    }

    #[test]
    fn stripped_readback_rows_remove_wgpu_padding() {
        let padded = 256usize;
        let width = 2u32;
        let height = 2u32;
        let mut input = vec![0u8; padded * height as usize];
        input[0..8].copy_from_slice(&[1, 2, 3, 4, 5, 6, 7, 8]);
        input[padded..padded + 8].copy_from_slice(&[9, 10, 11, 12, 13, 14, 15, 16]);

        assert_eq!(
            strip_padded_rows(&input, width, height, padded),
            vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        );
    }
}
```

- [ ] **Step 2: Run RED**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::padded_bytes_per_row_aligns_to_wgpu_copy_pitch render::wgpu_sprite_renderer::tests::stripped_readback_rows_remove_wgpu_padding
```

Expected: compile fails because helpers are undefined.

- [ ] **Step 3: Implement contract types and row helpers**

Add this code above the tests in `crates/rme_core/src/render/wgpu_sprite_renderer.rs`:

```rust
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

pub const SPRITE_SIZE: u32 = 32;
pub const RGBA_BYTES_PER_PIXEL: u32 = 4;
pub const CLEAR_RGBA: [u8; 4] = [10, 10, 18, 255];

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeadlessRenderResult {
    pub width: u32,
    pub height: u32,
    pub rgba: Vec<u8>,
    pub rendered_sprite_count: usize,
    pub missing_sprite_count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum HeadlessRendererError {
    AdapterUnavailable,
    DeviceUnavailable(String),
    MapFailed(String),
}

impl From<HeadlessRendererError> for PyErr {
    fn from(error: HeadlessRendererError) -> Self {
        match error {
            HeadlessRendererError::AdapterUnavailable => {
                PyRuntimeError::new_err("WGPU renderer unavailable: no compatible adapter")
            }
            HeadlessRendererError::DeviceUnavailable(message) => {
                PyRuntimeError::new_err(format!("WGPU renderer unavailable: {message}"))
            }
            HeadlessRendererError::MapFailed(message) => {
                PyRuntimeError::new_err(format!("WGPU readback failed: {message}"))
            }
        }
    }
}

pub fn padded_bytes_per_row(width: u32) -> usize {
    let unpadded = width as usize * RGBA_BYTES_PER_PIXEL as usize;
    let align = wgpu::COPY_BYTES_PER_ROW_ALIGNMENT as usize;
    unpadded.div_ceil(align) * align
}

pub fn strip_padded_rows(
    padded: &[u8],
    width: u32,
    height: u32,
    padded_bytes_per_row: usize,
) -> Vec<u8> {
    let tight_row_len = width as usize * RGBA_BYTES_PER_PIXEL as usize;
    let mut tight = Vec::with_capacity(tight_row_len * height as usize);
    for row in 0..height as usize {
        let row_start = row * padded_bytes_per_row;
        tight.extend_from_slice(&padded[row_start..row_start + tight_row_len]);
    }
    tight
}
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::padded_bytes_per_row_aligns_to_wgpu_copy_pitch render::wgpu_sprite_renderer::tests::stripped_readback_rows_remove_wgpu_padding
```

Expected: both tests pass.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/render/wgpu_sprite_renderer.rs crates/rme_core/src/render/mod.rs
git commit -m "feat(M024/S01): add headless renderer contract"
```

## Task 3: WGPU Device And Empty Offscreen Readback

**Files:**
- Modify: `crates/rme_core/src/render/wgpu_sprite_renderer.rs`

- [ ] **Step 1: Add empty render test**

Add this test in `crates/rme_core/src/render/wgpu_sprite_renderer.rs`:

```rust
#[test]
fn render_empty_frame_returns_clear_rgba() {
    let renderer = match HeadlessSpriteRenderer::new() {
        Ok(renderer) => renderer,
        Err(HeadlessRendererError::AdapterUnavailable) => return,
        Err(error) => panic!("unexpected renderer init error: {error:?}"),
    };

    let result = renderer.render_frame(4, 3, &[]).unwrap();

    assert_eq!(result.width, 4);
    assert_eq!(result.height, 3);
    assert_eq!(result.rendered_sprite_count, 0);
    assert_eq!(result.missing_sprite_count, 0);
    assert_eq!(result.rgba.len(), 4 * 3 * 4);
    assert!(result.rgba.chunks_exact(4).all(|pixel| pixel == CLEAR_RGBA));
}
```

- [ ] **Step 2: Run RED**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::render_empty_frame_returns_clear_rgba
```

Expected: compile fails because `HeadlessSpriteRenderer` is undefined.

- [ ] **Step 3: Implement WGPU empty render path**

Add this code above the tests:

```rust
pub struct HeadlessSpriteRenderer {
    device: wgpu::Device,
    queue: wgpu::Queue,
}

impl HeadlessSpriteRenderer {
    pub fn new() -> Result<Self, HeadlessRendererError> {
        let instance = wgpu::Instance::default();
        let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::LowPower,
            compatible_surface: None,
            force_fallback_adapter: false,
            ..Default::default()
        }))
        .map_err(|_| HeadlessRendererError::AdapterUnavailable)?;
        let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor {
            label: Some("rme_core headless sprite device"),
            required_features: wgpu::Features::empty(),
            required_limits: wgpu::Limits::default(),
            experimental_features: wgpu::ExperimentalFeatures::disabled(),
            memory_hints: wgpu::MemoryHints::Performance,
            trace: wgpu::Trace::Off,
        }))
        .map_err(|error| HeadlessRendererError::DeviceUnavailable(error.to_string()))?;
        Ok(Self { device, queue })
    }

    pub fn render_frame(
        &self,
        width: u32,
        height: u32,
        sprites: &[GpuSpriteCommand],
    ) -> Result<HeadlessRenderResult, HeadlessRendererError> {
        let output = self.device.create_texture(&wgpu::TextureDescriptor {
            label: Some("rme_core headless sprite output"),
            size: wgpu::Extent3d {
                width,
                height,
                depth_or_array_layers: 1,
            },
            mip_level_count: 1,
            sample_count: 1,
            dimension: wgpu::TextureDimension::D2,
            format: wgpu::TextureFormat::Rgba8Unorm,
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
            view_formats: &[],
        });
        let view = output.create_view(&wgpu::TextureViewDescriptor::default());
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor {
                label: Some("rme_core headless sprite encoder"),
            });
        {
            let _pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("rme_core headless sprite clear pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &view,
                    resolve_target: None,
                    depth_slice: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color {
                            r: f64::from(CLEAR_RGBA[0]) / 255.0,
                            g: f64::from(CLEAR_RGBA[1]) / 255.0,
                            b: f64::from(CLEAR_RGBA[2]) / 255.0,
                            a: 1.0,
                        }),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: None,
                timestamp_writes: None,
                occlusion_query_set: None,
            });
        }
        let rgba = self.read_texture_rgba(&output, width, height, encoder)?;
        Ok(HeadlessRenderResult {
            width,
            height,
            rgba,
            rendered_sprite_count: sprites.len(),
            missing_sprite_count: 0,
        })
    }

    fn read_texture_rgba(
        &self,
        output: &wgpu::Texture,
        width: u32,
        height: u32,
        mut encoder: wgpu::CommandEncoder,
    ) -> Result<Vec<u8>, HeadlessRendererError> {
        let padded_row = padded_bytes_per_row(width);
        let buffer_size = padded_row as u64 * height as u64;
        let staging = self.device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("rme_core headless sprite readback"),
            size: buffer_size,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });
        encoder.copy_texture_to_buffer(
            wgpu::TexelCopyTextureInfo {
                texture: output,
                mip_level: 0,
                origin: wgpu::Origin3d::ZERO,
                aspect: wgpu::TextureAspect::All,
            },
            wgpu::TexelCopyBufferInfo {
                buffer: &staging,
                layout: wgpu::TexelCopyBufferLayout {
                    offset: 0,
                    bytes_per_row: Some(padded_row as u32),
                    rows_per_image: Some(height),
                },
            },
            wgpu::Extent3d {
                width,
                height,
                depth_or_array_layers: 1,
            },
        );
        self.queue.submit(Some(encoder.finish()));
        let slice = staging.slice(..);
        let (tx, rx) = std::sync::mpsc::channel();
        slice.map_async(wgpu::MapMode::Read, move |result| {
            let _ = tx.send(result);
        });
        let _ = self.device.poll(wgpu::PollType::Wait);
        rx.recv()
            .map_err(|error| HeadlessRendererError::MapFailed(error.to_string()))?
            .map_err(|error| HeadlessRendererError::MapFailed(error.to_string()))?;
        let mapped = slice.get_mapped_range();
        let rgba = strip_padded_rows(&mapped, width, height, padded_row);
        drop(mapped);
        staging.unmap();
        Ok(rgba)
    }
}

#[derive(Debug, Clone)]
pub struct GpuSpriteCommand {
    pub x: u32,
    pub y: u32,
    pub layer: u32,
    pub sprite_id: u32,
    pub pixels: Vec<u8>,
}
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::render_empty_frame_returns_clear_rgba
```

Expected: test passes on hosts with WGPU adapter; test returns early only for explicit `AdapterUnavailable`.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/render/wgpu_sprite_renderer.rs
git commit -m "feat(M024/S01): read headless WGPU output"
```

## Task 4: Textured Sprite Draw Pass

**Files:**
- Modify: `crates/rme_core/src/render/wgpu_sprite_renderer.rs`
- Test: `crates/rme_core/src/render/sprite.wgsl`

- [ ] **Step 1: Add one-sprite pixel evidence test**

Add this test:

```rust
#[test]
fn render_one_solid_sprite_writes_sprite_pixels() {
    let renderer = match HeadlessSpriteRenderer::new() {
        Ok(renderer) => renderer,
        Err(HeadlessRendererError::AdapterUnavailable) => return,
        Err(error) => panic!("unexpected renderer init error: {error:?}"),
    };
    let pixels = vec![255u8, 0, 0, 255].repeat((SPRITE_SIZE * SPRITE_SIZE) as usize);
    let sprite = GpuSpriteCommand {
        x: 0,
        y: 0,
        layer: 0,
        sprite_id: 55,
        pixels,
    };

    let result = renderer.render_frame(32, 32, &[sprite]).unwrap();

    assert_eq!(result.rendered_sprite_count, 1);
    assert_eq!(result.missing_sprite_count, 0);
    assert!(result.rgba.chunks_exact(4).all(|pixel| pixel == [255, 0, 0, 255]));
}
```

- [ ] **Step 2: Run RED**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::render_one_solid_sprite_writes_sprite_pixels
```

Expected: test fails because current render path clears only.

- [ ] **Step 3: Implement upload, pipeline, and draw pass**

Extend `render_frame()` so it:

```rust
let sprite_texture = self.create_sprite_texture(sprites);
let sprite_view = sprite_texture.create_view(&wgpu::TextureViewDescriptor {
    dimension: Some(wgpu::TextureViewDimension::D2Array),
    ..Default::default()
});
let sampler = self.device.create_sampler(&wgpu::SamplerDescriptor {
    label: Some("rme_core sprite nearest sampler"),
    mag_filter: wgpu::FilterMode::Nearest,
    min_filter: wgpu::FilterMode::Nearest,
    mipmap_filter: wgpu::FilterMode::Nearest,
    ..Default::default()
});
let shader = self.device.create_shader_module(wgpu::ShaderModuleDescriptor {
    label: Some("rme_core sprite shader"),
    source: wgpu::ShaderSource::Wgsl(crate::render::sprite_shader::SPRITE_SHADER_WGSL.into()),
});
```

Add helper methods with these signatures:

```rust
fn create_sprite_texture(&self, sprites: &[GpuSpriteCommand]) -> wgpu::Texture;
fn create_pipeline(
    &self,
    shader: &wgpu::ShaderModule,
    texture_layout: &wgpu::BindGroupLayout,
    uniform_layout: &wgpu::BindGroupLayout,
) -> wgpu::RenderPipeline;
fn sprite_offset(width: u32, height: u32, x: u32, y: u32) -> [f32; 2];
```

Use `queue.write_texture()` once per sprite layer with:

```rust
wgpu::TexelCopyTextureInfo {
    texture: &sprite_texture,
    mip_level: 0,
    origin: wgpu::Origin3d {
        x: 0,
        y: 0,
        z: sprite.layer,
    },
    aspect: wgpu::TextureAspect::All,
}
```

Draw each staged sprite with `render_pass.draw(0..6, 0..1)` after setting the texture bind group and per-sprite uniform bind group.

- [ ] **Step 4: Run GREEN**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::render_one_solid_sprite_writes_sprite_pixels
```

Expected: test passes on hosts with WGPU adapter.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/render/wgpu_sprite_renderer.rs
git commit -m "feat(M024/S01): draw headless sprites with WGPU"
```

## Task 5: Layer Ordering

**Files:**
- Modify: `crates/rme_core/src/render/wgpu_sprite_renderer.rs`

- [ ] **Step 1: Add stacked layer test**

Add this test:

```rust
#[test]
fn higher_layer_draws_last_for_same_tile() {
    let renderer = match HeadlessSpriteRenderer::new() {
        Ok(renderer) => renderer,
        Err(HeadlessRendererError::AdapterUnavailable) => return,
        Err(error) => panic!("unexpected renderer init error: {error:?}"),
    };
    let red = vec![255u8, 0, 0, 255].repeat((SPRITE_SIZE * SPRITE_SIZE) as usize);
    let blue = vec![0u8, 0, 255, 255].repeat((SPRITE_SIZE * SPRITE_SIZE) as usize);
    let sprites = vec![
        GpuSpriteCommand {
            x: 0,
            y: 0,
            layer: 0,
            sprite_id: 55,
            pixels: red,
        },
        GpuSpriteCommand {
            x: 0,
            y: 0,
            layer: 1,
            sprite_id: 77,
            pixels: blue,
        },
    ];

    let result = renderer.render_frame(32, 32, &sprites).unwrap();

    assert!(result.rgba.chunks_exact(4).all(|pixel| pixel == [0, 0, 255, 255]));
}
```

- [ ] **Step 2: Run RED**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::higher_layer_draws_last_for_same_tile
```

Expected: fails if draw order follows input texture layer but not sorted command layer.

- [ ] **Step 3: Sort draw commands by layer**

Before drawing, clone sprite references and sort:

```rust
let mut draw_order = sprites.iter().collect::<Vec<_>>();
draw_order.sort_by_key(|sprite| sprite.layer);
```

Use `draw_order` for the render pass and keep texture upload indexed by each sprite's layer.

- [ ] **Step 4: Run GREEN**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core render::wgpu_sprite_renderer::tests::higher_layer_draws_last_for_same_tile
```

Expected: test passes.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/render/wgpu_sprite_renderer.rs
git commit -m "feat(M024/S01): preserve sprite layer order"
```

## Task 6: PyO3 Headless Bridge

**Files:**
- Modify: `crates/rme_core/src/render/sprite_atlas.rs`
- Test: `tests/python/test_wgpu_sprite_renderer.py`

- [ ] **Step 1: Write Python bridge tests**

Create `tests/python/test_wgpu_sprite_renderer.py`:

```python
from __future__ import annotations

import pytest

from pyrme.rme_core import render

SPRITE_BYTE_LEN = 32 * 32 * 4


def _solid(r: int, g: int, b: int, a: int = 255) -> bytes:
    return bytes((r, g, b, a)) * (32 * 32)


def test_render_headless_returns_tightly_packed_clear_buffer() -> None:
    atlas = render.SpriteAtlas()

    try:
        result = atlas.render_headless(4, 3)
    except RuntimeError as error:
        if "WGPU renderer unavailable: no compatible adapter" in str(error):
            pytest.skip(str(error))
        raise

    assert result["width"] == 4
    assert result["height"] == 3
    assert len(result["rgba"]) == 4 * 3 * 4
    assert result["rendered_sprite_count"] == 0
    assert result["missing_sprite_count"] == 0
    assert set(result["rgba"][index : index + 4] for index in range(0, len(result["rgba"]), 4)) == {
        bytes((10, 10, 18, 255))
    }


def test_render_headless_draws_last_staged_frame_sprite() -> None:
    atlas = render.SpriteAtlas()
    atlas.render_frame(
        [
            {
                "x": 0,
                "y": 0,
                "layer": 0,
                "sprite_id": 55,
                "pixels": _solid(255, 0, 0),
            }
        ]
    )

    try:
        result = atlas.render_headless(32, 32)
    except RuntimeError as error:
        if "WGPU renderer unavailable: no compatible adapter" in str(error):
            pytest.skip(str(error))
        raise

    assert result["rendered_sprite_count"] == 1
    assert result["missing_sprite_count"] == 0
    assert result["rgba"] == _solid(255, 0, 0)
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_wgpu_sprite_renderer.py -q --tb=short
```

Expected: fails because `SpriteAtlas.render_headless` does not exist.

- [ ] **Step 3: Add Rust bridge method**

In `crates/rme_core/src/render/sprite_atlas.rs`, import:

```rust
use crate::render::wgpu_sprite_renderer::{GpuSpriteCommand, HeadlessSpriteRenderer};
```

Inside `impl SpriteAtlas`, add:

```rust
pub fn render_headless<'py>(
    &self,
    py: Python<'py>,
    width: u32,
    height: u32,
) -> PyResult<Bound<'py, PyDict>> {
    let renderer = HeadlessSpriteRenderer::new()?;
    let sprites = self
        .last_frame
        .iter()
        .map(|command| GpuSpriteCommand {
            x: command.x,
            y: command.y,
            layer: command.layer,
            sprite_id: command.sprite_id,
            pixels: command.pixels.clone(),
        })
        .collect::<Vec<_>>();
    let result = renderer.render_frame(width, height, &sprites)?;
    let output = PyDict::new(py);
    output.set_item("width", result.width)?;
    output.set_item("height", result.height)?;
    output.set_item("rgba", PyBytes::new(py, &result.rgba))?;
    output.set_item("rendered_sprite_count", result.rendered_sprite_count)?;
    output.set_item("missing_sprite_count", result.missing_sprite_count)?;
    Ok(output)
}
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_wgpu_sprite_renderer.py -q --tb=short
```

Expected: both tests pass or skip only when adapter unavailable with the exact runtime message.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/render/sprite_atlas.rs tests/python/test_wgpu_sprite_renderer.py
git commit -m "feat(M024/S01): expose headless render bridge"
```

## Task 7: Verification And Closeout

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M024-wgpu-sprite-renderer/M024-wgpu-sprite-renderer-META.json`
- Modify: `.gsd/milestones/M024-wgpu-sprite-renderer/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M024-wgpu-sprite-renderer/slices/S01/S01-SUMMARY.md`

- [ ] **Step 1: Run formatting and Rust tests**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo fmt --all --check
PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core
```

Expected: both pass. If WGPU adapter is unavailable, GPU smoke tests skip only at the explicit adapter gate; pure row-copy tests still pass.

- [ ] **Step 2: Run focused Python tests**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_sprite_rendering.py tests/python/test_frame_payload.py tests/python/test_wgpu_sprite_renderer.py -q --tb=short
```

Expected: all pass, except WGPU bridge tests may skip only for `WGPU renderer unavailable: no compatible adapter`.

- [ ] **Step 3: Run preflight**

Run:

```bash
PATH="/home/marcelo/.local/bin:$PATH" npm run preflight
```

Expected: `Validation: ok`.

- [ ] **Step 4: Run caveman-review**

Review diff:

```bash
git diff --check
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- crates/rme_core tests/python .gsd docs/superpowers
```

Expected: no whitespace errors; diff contains only M024 renderer, bridge, tests, and GSD docs.

- [ ] **Step 5: Write closeout summary**

Create `.gsd/milestones/M024-wgpu-sprite-renderer/slices/S01/S01-SUMMARY.md`:

```markdown
# M024/S01 Summary

## Implemented

- Added WGPU 29.0.1 headless renderer contract.
- Rendered staged 32x32 RGBA sprites into an offscreen texture.
- Read back tightly packed RGBA bytes through WGPU texture-to-buffer copy.
- Exposed `SpriteAtlas.render_headless(width, height)` to Python.

## Verification

- `cargo fmt --all --check`
- `cargo test -p rme_core`
- `python3 -m pytest tests/python/test_sprite_rendering.py tests/python/test_frame_payload.py tests/python/test_wgpu_sprite_renderer.py -q --tb=short`
- `npm run preflight`

## Scope Notes

- No CPU fallback was added.
- No Qt-native WGPU surface was added.
- Canvas integration remains deferred to a later UI slice.
```

- [ ] **Step 6: Mark GSD done**

In `.gsd/milestones/M024-wgpu-sprite-renderer/slices/S01/S01-PLAN.md`, mark each task checkbox `[x]`.

Set `.gsd/milestones/M024-wgpu-sprite-renderer/M024-wgpu-sprite-renderer-META.json`:

```json
{
  "id": "M024-wgpu-sprite-renderer",
  "title": "WGPU Sprite Renderer",
  "status": "implemented",
  "active_slice": "S01",
  "updated_at": "2026-05-06T00:00:00-03:00"
}
```

Set `.gsd/STATE.md` active milestone to `M024-wgpu-sprite-renderer`, active slice to `S01-HEADLESS-WGPU-SPRITE-RENDERER`, phase to `review`, and next action to `Run caveman-review on M024/S01 diff, then push PR after clean review.`

- [ ] **Step 7: Commit closeout**

```bash
git add .gsd docs/superpowers
git commit -m "docs(M024/S01): close headless sprite renderer"
```

## Self-Review

- Spec coverage: tasks cover dependency gate, Rust renderer contract, WGPU offscreen clear/readback, textured sprite draw, layer order, PyO3 bridge, Python tests, and GSD closeout.
- Placeholder scan: clean for banned planning placeholders and vague handoff phrases.
- Type consistency: `HeadlessSpriteRenderer`, `HeadlessRenderResult`, `HeadlessRendererError`, `GpuSpriteCommand`, and `SpriteAtlas.render_headless(width, height)` are introduced before use in later tasks.

## Execution Choice

Plan complete and saved to `docs/superpowers/plans/2026-05-06-m024-wgpu-sprite-renderer.md`.

1. Subagent-Driven: dispatch one fresh subagent per task, review between tasks, fastest when PR #89 is merged.
2. Inline Execution: execute tasks in this session with `superpowers:executing-plans`, checkpoint after each task.
