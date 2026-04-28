//! OTB format parser (items.otb).

use pyo3::prelude::*;
use std::collections::HashMap;
use std::fs;

use super::binary_tree::{OtbTreeReader, ParserError, PayloadReader};

#[derive(Debug)]
pub enum OtbError {
    IoError(std::io::Error),
    ParserError(ParserError),
    InvalidFormat(&'static str),
}

impl From<std::io::Error> for OtbError {
    fn from(err: std::io::Error) -> Self {
        OtbError::IoError(err)
    }
}

impl From<ParserError> for OtbError {
    fn from(err: ParserError) -> Self {
        OtbError::ParserError(err)
    }
}

// OTB Attributes
const ROOT_ATTR_VERSION: u8 = 0x01;
const ITEM_ATTR_SERVERID: u8 = 0x10;
const ITEM_ATTR_CLIENTID: u8 = 0x11;
const ITEM_ATTR_NAME: u8 = 0x12;
const ITEM_ATTR_DESCR: u8 = 0x13;
const ITEM_ATTR_SPEED: u8 = 0x14;
const ITEM_ATTR_MAXITEMS: u8 = 0x17;

#[pyclass]
#[derive(Debug, Clone, Default)]
pub struct OtbItem {
    #[pyo3(get, set)]
    pub server_id: u16,
    #[pyo3(get, set)]
    pub client_id: u16,
    #[pyo3(get, set)]
    pub group: u8,
    #[pyo3(get, set)]
    pub flags: u32,
    #[pyo3(get, set)]
    pub name: String,
    #[pyo3(get, set)]
    pub description: String,
    #[pyo3(get, set)]
    pub speed: u16,
    #[pyo3(get, set)]
    pub volume: u16,
    #[pyo3(get, set)]
    pub weight: f32,
}

#[pyclass]
pub struct OtbDatabase {
    items: HashMap<u16, OtbItem>,
}

impl OtbDatabase {
    pub fn parse(buffer: &[u8]) -> Result<Self, OtbError> {
        if buffer.len() < 4 {
            return Err(OtbError::InvalidFormat("Buffer too small"));
        }

        let mut reader = OtbTreeReader::new(buffer);
        // Magic check. "OTBI" or "0 0 0 0"
        let magic = &buffer[0..4];
        if magic != b"OTBI" && magic != [0, 0, 0, 0] {
            return Err(OtbError::InvalidFormat("Invalid magic signature"));
        }
        reader.skip(4)?;

        let root = reader.parse_root()?;

        let mut root_payload = PayloadReader::new(&root.data);
        root_payload.skip(4); // Legacy skip 4 bytes

        let root_attr = root_payload
            .read_u8()
            .ok_or(OtbError::InvalidFormat("Missing root attr"))?;
        if root_attr != ROOT_ATTR_VERSION {
            return Err(OtbError::InvalidFormat("Expected ROOT_ATTR_VERSION"));
        }

        let _version_len = root_payload
            .read_u16()
            .ok_or(OtbError::InvalidFormat("Missing version length"))?;
        let major = root_payload
            .read_u32()
            .ok_or(OtbError::InvalidFormat("Missing major version"))?;

        // Skip checking the other version fields (minor, build) for now as we just need items
        if major > 3 {
            return Err(OtbError::InvalidFormat("Unsupported major version"));
        }

        let mut items = HashMap::new();

        for child in root.children {
            let mut fr = OtbItem {
                group: child.node_type,
                ..OtbItem::default()
            };

            let mut pl = PayloadReader::new(&child.data);
            if let Some(flags) = pl.read_u32() {
                fr.flags = flags;
            }

            // Loop attributes
            while let Some(attr) = pl.read_u8() {
                let length = match pl.read_u16() {
                    Some(len) => len as usize,
                    None => break,
                };

                match attr {
                    ITEM_ATTR_SERVERID if length == 2 => {
                        if let Some(id) = pl.read_u16() {
                            fr.server_id = id;
                        }
                    }
                    ITEM_ATTR_SERVERID => {
                        pl.skip(length);
                    }
                    ITEM_ATTR_CLIENTID if length == 2 => {
                        if let Some(id) = pl.read_u16() {
                            fr.client_id = id;
                        }
                    }
                    ITEM_ATTR_CLIENTID => {
                        pl.skip(length);
                    }
                    ITEM_ATTR_NAME => {
                        if let Some(bytes) = pl.read_bytes(length) {
                            fr.name = String::from_utf8_lossy(bytes).into_owned();
                        }
                    }
                    ITEM_ATTR_DESCR => {
                        if let Some(bytes) = pl.read_bytes(length) {
                            fr.description = String::from_utf8_lossy(bytes).into_owned();
                        }
                    }
                    ITEM_ATTR_SPEED if length == 2 => {
                        if let Some(v) = pl.read_u16() {
                            fr.speed = v;
                        }
                    }
                    ITEM_ATTR_SPEED => {
                        pl.skip(length);
                    }
                    ITEM_ATTR_MAXITEMS if length == 2 => {
                        if let Some(v) = pl.read_u16() {
                            fr.volume = v;
                        }
                    }
                    ITEM_ATTR_MAXITEMS => {
                        pl.skip(length);
                    }
                    // weight is stored as 8-byte double? Wait, or what is it?
                    // legacy: double weight = 0.0; readFixedPayload(item_node, length, weight) => length=8?
                    // We'll skip for now if we can't parse it reliably, wait, legacy reads it as double (float64) under ITEM_ATTR_WEIGHT.
                    // Oh, actually in C++ it is read as `double` because `cast<double>`. Wait no, in legacy: `double weight = 0.0; readFixedPayload(item_node, length, weight)`. Yes, it's 8 bytes.
                    _ => {
                        pl.skip(length);
                    }
                }
            }

            if fr.server_id != 0 {
                items.insert(fr.server_id, fr);
            }
        }

        Ok(Self { items })
    }
}

#[pymethods]
impl OtbDatabase {
    #[new]
    fn new() -> Self {
        Self {
            items: HashMap::new(),
        }
    }

    #[staticmethod]
    pub fn from_file(path: String) -> PyResult<Self> {
        let bytes = fs::read(&path)?;
        Self::parse(&bytes)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Parse error: {:?}", e)))
    }

    pub fn get_item(&self, server_id: u16) -> Option<OtbItem> {
        self.items.get(&server_id).cloned()
    }

    pub fn item_count(&self) -> usize {
        self.items.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::io::binary_tree::{NODE_END, NODE_START};

    #[test]
    fn test_otb_parse() {
        let mut buf = Vec::new();
        // Magic
        buf.extend_from_slice(b"OTBI");

        // Root node
        buf.push(NODE_START);
        buf.push(0x00); // node_type
        buf.extend_from_slice(&[0, 0, 0, 0]); // dummy skip 4
        buf.push(ROOT_ATTR_VERSION);
        buf.extend_from_slice(&[12_u16.to_le_bytes()[0], 12_u16.to_le_bytes()[1]]); // length
        buf.extend_from_slice(&[3, 0, 0, 0]); // major
        buf.extend_from_slice(&[0, 0, 0, 0]); // minor
        buf.extend_from_slice(&[0, 0, 0, 0]); // build

        // Item child node
        buf.push(NODE_START);
        buf.push(0x01); // group
        buf.extend_from_slice(&[0, 0, 0, 0]); // flags

        // Attr server ID
        buf.push(ITEM_ATTR_SERVERID);
        buf.extend_from_slice(&2_u16.to_le_bytes()); // length
        buf.extend_from_slice(&100_u16.to_le_bytes()); // ID = 100

        buf.push(NODE_END); // end item
        buf.push(NODE_END); // end root

        let db = OtbDatabase::parse(&buf).unwrap();
        assert_eq!(db.item_count(), 1);
        let item = db.get_item(100).unwrap();
        assert_eq!(item.server_id, 100);
        assert_eq!(item.group, 0x01);
    }
}
