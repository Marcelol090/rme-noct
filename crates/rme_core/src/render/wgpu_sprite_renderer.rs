//! Headless WGPU sprite renderer.
//!
//! M024 fills this module after the Python render-submodule gate is green.

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
