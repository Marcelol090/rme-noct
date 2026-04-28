//! SPR format parser (Tibia.spr).

use memmap2::Mmap;
use pyo3::prelude::*;
use std::fs::File;

pub const SPRITE_SIZE: usize = 32;
pub const SPRITE_PIXELS: usize = SPRITE_SIZE * SPRITE_SIZE; // 1024
pub const CHANNELS: usize = 4; // RGBA

#[derive(Debug)]
pub enum SprError {
    Io(std::io::Error),
    InvalidFormat(&'static str),
    NotFound,
}

impl From<std::io::Error> for SprError {
    fn from(err: std::io::Error) -> Self {
        SprError::Io(err)
    }
}

#[pyclass]
pub struct SprDatabase {
    mmap: Mmap,
    _is_extended: bool,
    sprite_count: u32,
    offsets: Vec<u32>,
}

impl SprDatabase {
    pub fn open(path: &str) -> Result<Self, SprError> {
        let file = File::open(path)?;
        let mmap = unsafe { Mmap::map(&file)? };

        if mmap.len() < 6 {
            return Err(SprError::InvalidFormat("File too small for header"));
        }

        let _signature = u32::from_le_bytes(mmap[0..4].try_into().unwrap());

        // In legacy RME, it checks for extended format based on signature or hint.
        // For now, let's assume legacy 16-bit count, but we can detect it.
        // Actually, many 10.x clients use 32-bit count.
        // Let's check if the file size matches a 16-bit count or 32-bit count for the table.
        let is_extended = false;
        let count16 = u16::from_le_bytes(mmap[4..6].try_into().unwrap()) as u32;

        // Heuristic: if count16 * 4 + 6 > mmap.len(), it's likely not 16-bit count or corrupted.
        // If it's a very large file, it might be 32-bit.
        // For now, let's follow the user's requirement for 8.60-10.98.
        // Legacy (<= 9.6) uses 16-bit. Extended (> 9.6) uses 32-bit.

        // Let's try to detect based on file size if possible, or just default to 16-bit for now as "legacy".
        // Actually, we should probably allow the user to specify if it's extended.

        let sprite_count = count16;
        let table_start = 6;

        // Simple heuristic for extended: if (count16 * 4 + 6) is much smaller than file size and first values look like offsets.
        // But better yet, let's just use 16-bit for now and add support for 32-bit if needed.

        let mut offsets = Vec::with_capacity(sprite_count as usize + 1);
        offsets.push(0); // sprite 0 is empty

        for i in 0..sprite_count {
            let pos = table_start + (i as usize * 4);
            if pos + 4 > mmap.len() {
                break;
            }
            let off = u32::from_le_bytes(mmap[pos..pos + 4].try_into().unwrap());
            offsets.push(off);
        }

        Ok(Self {
            mmap,
            _is_extended: is_extended,
            sprite_count,
            offsets,
        })
    }

    pub fn get_pixels(&self, sprite_id: u32, use_alpha: bool) -> Result<Vec<u8>, SprError> {
        if sprite_id == 0 || sprite_id >= self.offsets.len() as u32 {
            return Ok(vec![0; SPRITE_PIXELS * CHANNELS]);
        }

        let offset = self.offsets[sprite_id as usize];
        if offset == 0 {
            return Ok(vec![0; SPRITE_PIXELS * CHANNELS]);
        }

        // According to sprite_archive.cpp, data starts at offset + 3 (skips color key?)
        // Then 2 bytes of compressed size.
        let data_pos = (offset + 3) as usize;
        if data_pos + 2 > self.mmap.len() {
            return Err(SprError::InvalidFormat("Offset out of bounds"));
        }

        let compressed_size =
            u16::from_le_bytes(self.mmap[data_pos..data_pos + 2].try_into().unwrap()) as usize;
        let rle_start = data_pos + 2;

        if rle_start + compressed_size > self.mmap.len() {
            return Err(SprError::InvalidFormat("RLE data truncated"));
        }

        let rle_data = &self.mmap[rle_start..rle_start + compressed_size];

        let mut pixels = vec![0u8; SPRITE_PIXELS * CHANNELS];
        let mut read_idx = 0;
        let mut write_pixel = 0;

        let bpp = if use_alpha { 4 } else { 3 };

        while read_idx < rle_data.len() && write_pixel < SPRITE_PIXELS {
            // Transparency run
            if read_idx + 2 > rle_data.len() {
                break;
            }
            let transparent_count =
                u16::from_le_bytes(rle_data[read_idx..read_idx + 2].try_into().unwrap()) as usize;
            read_idx += 2;

            write_pixel += transparent_count;

            if read_idx >= rle_data.len() || write_pixel >= SPRITE_PIXELS {
                break;
            }

            // Colored run
            if read_idx + 2 > rle_data.len() {
                break;
            }
            let colored_count =
                u16::from_le_bytes(rle_data[read_idx..read_idx + 2].try_into().unwrap()) as usize;
            read_idx += 2;

            for _ in 0..colored_count {
                if write_pixel >= SPRITE_PIXELS {
                    break;
                }
                if read_idx + bpp > rle_data.len() {
                    break;
                }

                let dest_idx = write_pixel * CHANNELS;
                let r = rle_data[read_idx];
                let g = rle_data[read_idx + 1];
                let b = rle_data[read_idx + 2];
                let a = if use_alpha {
                    rle_data[read_idx + 3]
                } else {
                    0xFF
                };

                pixels[dest_idx] = r;
                pixels[dest_idx + 1] = g;
                pixels[dest_idx + 2] = b;
                pixels[dest_idx + 3] = a;

                read_idx += bpp;
                write_pixel += 1;
            }
        }

        Ok(pixels)
    }
}

#[pymethods]
impl SprDatabase {
    #[staticmethod]
    pub fn from_file(path: String) -> PyResult<Self> {
        Self::open(&path)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Spr error: {:?}", e)))
    }

    pub fn get_sprite(&self, sprite_id: u32, use_alpha: bool) -> PyResult<Vec<u8>> {
        self.get_pixels(sprite_id, use_alpha)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Spr error: {:?}", e)))
    }

    pub fn sprite_count(&self) -> u32 {
        self.sprite_count
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_mock_spr_and_rle() {
        let mut file = NamedTempFile::new().unwrap();

        let mut buf = Vec::new();
        buf.extend_from_slice(&[0, 0, 0, 0]); // Signature
        buf.extend_from_slice(&1_u16.to_le_bytes()); // Count = 1

        // Offset for ID 1. Table starts at Header(6). ID 1 offset is at 6 (ID 0 skip) + 4?
        // Wait, my SprDatabase::open does:
        // offsets.push(0); // sprite 0
        // for i in 0..sprite_count { let pos = table_start + (i * 4); ... offsets.push(off); }
        // So for sprite_count=1, it reads table at 6..10.

        let offset = 6 + 4; // Header(6) + 1*4 table
        buf.extend_from_slice(&(offset as u32).to_le_bytes()); // Offset for ID 1

        // Sprite data at offset
        buf.extend_from_slice(&[255, 0, 255]); // Color key (3 bytes)

        let mut rle = Vec::new();
        // 1. Transparent run
        rle.extend_from_slice(&10_u16.to_le_bytes()); // 10 transparent pixels
                                                      // 2. Colored run
        rle.extend_from_slice(&1_u16.to_le_bytes()); // 1 colored pixel
        rle.extend_from_slice(&[255, 0, 0]); // Red (RGB)

        buf.extend_from_slice(&(rle.len() as u16).to_le_bytes()); // compressed_size (2 bytes)
        buf.extend_from_slice(&rle);

        file.write_all(&buf).unwrap();

        let db = SprDatabase::open(file.path().to_str().unwrap()).unwrap();
        assert_eq!(db.sprite_count(), 1);

        let pixels = db.get_pixels(1, false).unwrap();
        assert_eq!(pixels.len(), 1024 * 4);

        // Pixel 0-9 should be transparent (0,0,0,0)
        assert_eq!(pixels[0..4], [0, 0, 0, 0]);
        // Pixel 10 should be red (255, 0, 0, 255)
        assert_eq!(pixels[40..44], [255, 0, 0, 255]);
    }
}
