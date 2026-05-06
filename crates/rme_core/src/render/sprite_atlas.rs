//! Sprite atlas upload staging.
//!
//! This module intentionally keeps the M023 surface CPU-side. It validates
//! sprite RGBA payloads and records typed frame commands for a later renderer
//! upload pass without claiming a live WGPU device exists.

use crate::render::wgpu_sprite_renderer::{GpuSpriteCommand, HeadlessSpriteRenderer};
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

const SPRITE_WIDTH: usize = 32;
const SPRITE_HEIGHT: usize = 32;
const RGBA_BYTES_PER_PIXEL: usize = 4;
const SPRITE_BYTE_LEN: usize = SPRITE_WIDTH * SPRITE_HEIGHT * RGBA_BYTES_PER_PIXEL;

#[derive(Clone)]
struct SpriteFrameCommand {
    x: u32,
    y: u32,
    layer: u32,
    sprite_id: u32,
    pixels: Vec<u8>,
}

pub struct SpriteData {
    x: u32,
    y: u32,
    layer: u32,
    sprite_id: u32,
    pixels: Vec<u8>,
}

impl<'py> FromPyObject<'py> for SpriteData {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let sprite = ob
            .downcast::<PyDict>()
            .map_err(|_| PyTypeError::new_err("sprite payload must be a mapping"))?;
        Ok(Self {
            x: extract_u32(sprite, "x")?,
            y: extract_u32(sprite, "y")?,
            layer: extract_u32(sprite, "layer")?,
            sprite_id: extract_u32(sprite, "sprite_id")?,
            pixels: extract_pixel_bytes(&extract_required(sprite, "pixels")?)?,
        })
    }
}

/// CPU staging wrapper for sprite pixel data.
#[pyclass]
#[derive(Clone)]
pub struct SpriteAtlas {
    mapped_pixels: Vec<u8>,
    mapped_sprite_count: usize,
    last_frame: Vec<SpriteFrameCommand>,
}

#[pymethods]
impl SpriteAtlas {
    #[new]
    pub fn new() -> Self {
        Self {
            mapped_pixels: Vec::new(),
            mapped_sprite_count: 0,
            last_frame: Vec::new(),
        }
    }

    /// Stage one 32x32 RGBA sprite payload for a later renderer upload.
    pub fn map_buffer(&mut self, pixels: &[u8]) -> PyResult<bool> {
        validate_sprite_byte_len(pixels.len())?;
        self.mapped_pixels.extend_from_slice(pixels);
        self.mapped_sprite_count += 1;
        Ok(true)
    }

    pub fn mapped_pixels<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.mapped_pixels)
    }

    pub fn mapped_byte_len(&self) -> usize {
        self.mapped_pixels.len()
    }

    pub fn mapped_sprite_count(&self) -> usize {
        self.mapped_sprite_count
    }

    /// Receives a list of sprite payloads and queues them for rendering.
    pub fn render_frame(&mut self, sprites: Vec<SpriteData>) -> PyResult<usize> {
        let mut frame = Vec::with_capacity(sprites.len());
        for sprite in sprites {
            validate_sprite_byte_len(sprite.pixels.len())?;
            frame.push(SpriteFrameCommand {
                x: sprite.x,
                y: sprite.y,
                layer: sprite.layer,
                sprite_id: sprite.sprite_id,
                pixels: sprite.pixels,
            });
        }
        let processed = frame.len();
        self.last_frame = frame;
        Ok(processed)
    }

    pub fn last_frame_sprite_ids(&self) -> Vec<u32> {
        self.last_frame
            .iter()
            .map(|command| command.sprite_id)
            .collect()
    }

    pub fn last_frame_positions(&self) -> Vec<(u32, u32, u32)> {
        self.last_frame
            .iter()
            .map(|command| (command.x, command.y, command.layer))
            .collect()
    }

    pub fn last_frame_pixel_byte_lens(&self) -> Vec<usize> {
        self.last_frame
            .iter()
            .map(|command| command.pixels.len())
            .collect()
    }

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
}

impl Default for SpriteAtlas {
    fn default() -> Self {
        Self::new()
    }
}

fn validate_sprite_byte_len(len: usize) -> PyResult<()> {
    if len == SPRITE_BYTE_LEN {
        return Ok(());
    }
    Err(PyValueError::new_err(format!(
        "sprite RGBA payload must be exactly {SPRITE_BYTE_LEN} bytes, got {len}",
    )))
}

fn extract_required<'py>(sprite: &Bound<'py, PyDict>, key: &str) -> PyResult<Bound<'py, PyAny>> {
    sprite.get_item(key)?.ok_or_else(|| {
        PyTypeError::new_err(format!("sprite payload missing required field `{key}`"))
    })
}

fn extract_u32(sprite: &Bound<'_, PyDict>, key: &str) -> PyResult<u32> {
    let value = extract_required(sprite, key)?;
    value
        .extract::<u32>()
        .map_err(|_| PyTypeError::new_err(format!("sprite payload field `{key}` must be int")))
}

fn extract_pixel_bytes(value: &Bound<'_, PyAny>) -> PyResult<Vec<u8>> {
    let bytes = value
        .downcast::<PyBytes>()
        .map_err(|_| PyTypeError::new_err("sprite payload field `pixels` must be bytes"))?;
    Ok(bytes.as_bytes().to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn map_buffer_stages_exact_sprite_bytes() {
        let pixels = (0..SPRITE_BYTE_LEN)
            .map(|index| (index % 256) as u8)
            .collect::<Vec<_>>();
        let mut atlas = SpriteAtlas::new();

        assert!(atlas.map_buffer(&pixels).unwrap());

        assert_eq!(atlas.mapped_pixels, pixels);
        assert_eq!(atlas.mapped_byte_len(), SPRITE_BYTE_LEN);
        assert_eq!(atlas.mapped_sprite_count(), 1);
    }

    #[test]
    fn map_buffer_rejects_invalid_sprite_byte_len() {
        let mut atlas = SpriteAtlas::new();

        assert!(atlas.map_buffer(&vec![0; SPRITE_BYTE_LEN - 1]).is_err());
        assert!(atlas.map_buffer(&vec![0; SPRITE_BYTE_LEN * 2]).is_err());
    }
}
