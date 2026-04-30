//! DAT format parser (Tibia.dat).

use pyo3::prelude::*;
use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};

#[derive(Debug)]
pub enum DatError {
    Io(std::io::Error),
    InvalidFormat(&'static str),
}

impl From<std::io::Error> for DatError {
    fn from(err: std::io::Error) -> Self {
        DatError::Io(err)
    }
}

#[pyclass]
#[derive(Debug, Clone, Default)]
pub struct DatItem {
    #[pyo3(get, set)]
    pub client_id: u16,
    #[pyo3(get, set)]
    pub ground: bool,
    #[pyo3(get, set)]
    pub speed: u16,
    #[pyo3(get, set)]
    pub impassable: bool,
    #[pyo3(get, set)]
    pub block_missiles: bool,
    #[pyo3(get, set)]
    pub elevation: u16,
    #[pyo3(get, set)]
    pub sprite_ids: Vec<u32>,
    #[pyo3(get, set)]
    pub width: u8,
    #[pyo3(get, set)]
    pub height: u8,
    #[pyo3(get, set)]
    pub layers: u8,
    #[pyo3(get, set)]
    pub pattern_x: u8,
    #[pyo3(get, set)]
    pub pattern_y: u8,
    #[pyo3(get, set)]
    pub pattern_z: u8,
    #[pyo3(get, set)]
    pub frames: u8,
}

#[pyclass]
pub struct DatDatabase {
    items: HashMap<u16, DatItem>,
}

impl DatDatabase {
    pub fn parse(mut file: File) -> Result<Self, DatError> {
        let mut items = HashMap::new();

        // Read signature
        let mut sig_buf = [0u8; 4];
        file.read_exact(&mut sig_buf)?;

        let mut counts = [0u8; 8];
        file.read_exact(&mut counts)?;

        let item_count = u16::from_le_bytes(counts[0..2].try_into().unwrap());
        // Skip creature, effect, distance counts

        for client_id in 100..=item_count {
            let mut it = DatItem::default();
            it.client_id = client_id;

            // Read flags
            loop {
                let mut flag_buf = [0u8; 1];
                file.read_exact(&mut flag_buf)?;
                let flag = flag_buf[0];

                if flag == 0xFF {
                    break;
                }

                // 8.6+ Flag mapping (simplified)
                match flag {
                    0x00 => {
                        // Ground
                        it.ground = true;
                        let mut speed_buf = [0u8; 2];
                        file.read_exact(&mut speed_buf)?;
                        it.speed = u16::from_le_bytes(speed_buf);
                    }
                    0x01..=0x03 => {} // Bottom/Top order
                    0x04 => {}               // Container
                    0x05 => {}               // Stackable
                    0x09 => {
                        it.impassable = true;
                    }
                    0x0B => {
                        it.block_missiles = true;
                    }
                    0x1A => {
                        // Elevation
                        let mut elev_buf = [0u8; 2];
                        file.read_exact(&mut elev_buf)?;
                        it.elevation = u16::from_le_bytes(elev_buf);
                    }
                    // Many payloads are 2 bytes, some more.
                    // This is a simplified parser for the TDD milestone.
                    0x11 | 0x12 | 0x13 | 0x14 | 0x19 | 0x1B | 0x1C => {
                        file.seek(SeekFrom::Current(2))?;
                    }
                    0x18 => {
                        // Light
                        file.seek(SeekFrom::Current(4))?;
                    }
                    0x1D => {
                        // Market
                        file.seek(SeekFrom::Current(2))?; // Category
                        let mut name_len_buf = [0u8; 2];
                        file.read_exact(&mut name_len_buf)?;
                        let name_len = u16::from_le_bytes(name_len_buf) as i64;
                        file.seek(SeekFrom::Current(name_len + 8))?; // name + 8 junk
                    }
                    _ => {
                        // Unknown flag, we might desync here if payload exists.
                        // In real RME it defines ranges.
                    }
                }
            }

            // Read dimensions
            let mut dims = [0u8; 2];
            file.read_exact(&mut dims)?;
            it.width = dims[0];
            it.height = dims[1];

            if it.width > 1 || it.height > 1 {
                file.seek(SeekFrom::Current(1))?; // Jump?
            }

            let mut rest = [0u8; 5];
            file.read_exact(&mut rest)?;
            it.layers = rest[0];
            it.pattern_x = rest[1];
            it.pattern_y = rest[2];
            it.pattern_z = rest[3];
            it.frames = rest[4];

            let num_sprites = (it.width as u32)
                * (it.height as u32)
                * (it.layers as u32)
                * (it.pattern_x as u32)
                * (it.pattern_y as u32)
                * (it.pattern_z as u32)
                * (it.frames as u32);

            for _ in 0..num_sprites {
                let mut sid_buf = [0u8; 2];
                file.read_exact(&mut sid_buf)?;
                it.sprite_ids.push(u16::from_le_bytes(sid_buf) as u32);
            }

            items.insert(client_id, it);
        }

        Ok(Self { items })
    }
}

#[pymethods]
impl DatDatabase {
    #[staticmethod]
    pub fn from_file(path: String) -> PyResult<Self> {
        let file = File::open(path)?;
        Self::parse(file)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Dat error: {:?}", e)))
    }

    pub fn get_item(&self, client_id: u16) -> Option<DatItem> {
        self.items.get(&client_id).cloned()
    }

    pub fn item_count(&self) -> usize {
        self.items.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_mock_dat_parse() {
        let mut file = NamedTempFile::new().unwrap();

        let mut buf = Vec::new();
        buf.extend_from_slice(&[0, 0, 0, 0]); // Signature
                                              // counts: items, creatures, effects, distances (8 bytes)
        buf.extend_from_slice(&100_u16.to_le_bytes()); // Item count = 100
        buf.extend_from_slice(&0_u16.to_le_bytes()); // Creature count
        buf.extend_from_slice(&0_u16.to_le_bytes()); // Effect count
        buf.extend_from_slice(&0_u16.to_le_bytes()); // Distance count

        // Item 100 flags
        buf.push(0x00); // Ground
        buf.extend_from_slice(&50_u16.to_le_bytes()); // Speed
        buf.push(0x09); // Impassable
        buf.push(0xFF); // End flags

        buf.push(1); // Width
        buf.push(1); // Height
                     // No jump byte since width=1, height=1

        buf.push(1); // Layers
        buf.push(1); // PX
        buf.push(1); // PY
        buf.push(1); // PZ
        buf.push(1); // Frames

        buf.extend_from_slice(&123_u16.to_le_bytes()); // Sprite ID

        file.write_all(&buf).unwrap();

        // Use parse instead of from_file to avoid re-opening if possible,
        // but since parse takes File ownership, let's just use from_file here.
        let db = DatDatabase::from_file(file.path().to_str().unwrap().to_string()).unwrap();

        // item_count is 100, but we only have 1 item (the 100th).
        // Wait, my loop does 100..=item_count. So for item_count=100, it reads 1 item.
        assert_eq!(db.item_count(), 1);

        let item = db.get_item(100).unwrap();
        assert_eq!(item.client_id, 100);
        assert!(item.ground);
        assert_eq!(item.speed, 50);
        assert!(item.impassable);
        assert_eq!(item.sprite_ids[0], 123);
    }
}
