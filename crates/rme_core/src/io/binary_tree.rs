//! Binary Tree parsing for OTB/OTBM format payloads.
//!
//! This parser reads binary streams into an "owned tree" representing the nodes.
//! It automatically handles escape sequences for `NODE_START` (0xFE), `NODE_END` (0xFF),
//! and `ESCAPE_CHAR` (0xFD).

pub const NODE_START: u8 = 0xFE;
pub const NODE_END: u8 = 0xFF;
pub const ESCAPE_CHAR: u8 = 0xFD;

#[derive(Debug, PartialEq, Clone)]
pub struct OtbNode {
    pub node_type: u8,
    pub data: Vec<u8>,
    pub children: Vec<OtbNode>,
}

#[derive(Debug, PartialEq)]
pub enum ParserError {
    UnexpectedEof,
    InvalidEscape,
    SyntaxError,
}

pub struct OtbTreeReader<'a> {
    buffer: &'a [u8],
    position: usize,
}

impl<'a> OtbTreeReader<'a> {
    pub fn new(buffer: &'a [u8]) -> Self {
        Self {
            buffer,
            position: 0,
        }
    }

    /// Skips a specific number of bytes (useful for bypassing magic numbers like "OTBI")
    pub fn skip(&mut self, amount: usize) -> Result<(), ParserError> {
        if self.position + amount > self.buffer.len() {
            return Err(ParserError::UnexpectedEof);
        }
        self.position += amount;
        Ok(())
    }

    /// Parses the root node. Expects the immediate next byte to be `NODE_START`.
    pub fn parse_root(&mut self) -> Result<OtbNode, ParserError> {
        let b = self.read_byte()?;
        if b != NODE_START {
            return Err(ParserError::SyntaxError);
        }
        self.parse_node()
    }

    fn read_byte(&mut self) -> Result<u8, ParserError> {
        if self.position >= self.buffer.len() {
            Err(ParserError::UnexpectedEof)
        } else {
            let b = self.buffer[self.position];
            self.position += 1;
            Ok(b)
        }
    }

    fn parse_node(&mut self) -> Result<OtbNode, ParserError> {
        let node_type = self.read_byte()?;

        let mut data = Vec::new();
        let mut children = Vec::new();

        // 1. Read payload
        loop {
            let b = self.read_byte()?;
            match b {
                ESCAPE_CHAR => {
                    let escaped = self.read_byte().map_err(|_| ParserError::InvalidEscape)?;
                    data.push(escaped);
                }
                NODE_START => {
                    // Payload ends, start of a child
                    let child = self.parse_node()?;
                    children.push(child);
                    break; // Move to parsing siblings (phase 2)
                }
                NODE_END => {
                    // Node ends completely payload+children
                    return Ok(OtbNode {
                        node_type,
                        data,
                        children,
                    });
                }
                _ => {
                    data.push(b);
                }
            }
        }

        // 2. Read children
        loop {
            let b = self.read_byte()?;
            match b {
                NODE_START => {
                    let child = self.parse_node()?;
                    children.push(child);
                }
                NODE_END => {
                    return Ok(OtbNode {
                        node_type,
                        data,
                        children,
                    });
                }
                _ => {
                    // Anything else is a syntax error after child blocks begin
                    return Err(ParserError::SyntaxError);
                }
            }
        }
    }
}

/// A lightweight cursor to extract primitives from an `OtbNode` payload mapping to `BinaryNode` methods in C++.
pub struct PayloadReader<'a> {
    data: &'a [u8],
    pos: usize,
}

impl<'a> PayloadReader<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        Self { data, pos: 0 }
    }

    pub fn read_u8(&mut self) -> Option<u8> {
        if self.pos < self.data.len() {
            let val = self.data[self.pos];
            self.pos += 1;
            Some(val)
        } else {
            None
        }
    }

    pub fn read_u16(&mut self) -> Option<u16> {
        if self.pos + 2 <= self.data.len() {
            let val = u16::from_le_bytes([self.data[self.pos], self.data[self.pos + 1]]);
            self.pos += 2;
            Some(val)
        } else {
            None
        }
    }

    pub fn read_u32(&mut self) -> Option<u32> {
        if self.pos + 4 <= self.data.len() {
            let val = u32::from_le_bytes([
                self.data[self.pos],
                self.data[self.pos + 1],
                self.data[self.pos + 2],
                self.data[self.pos + 3],
            ]);
            self.pos += 4;
            Some(val)
        } else {
            None
        }
    }

    pub fn read_u64(&mut self) -> Option<u64> {
        if self.pos + 8 <= self.data.len() {
            let mut arr = [0u8; 8];
            arr.copy_from_slice(&self.data[self.pos..self.pos + 8]);
            self.pos += 8;
            Some(u64::from_le_bytes(arr))
        } else {
            None
        }
    }

    pub fn read_bytes(&mut self, length: usize) -> Option<&'a [u8]> {
        if self.pos + length <= self.data.len() {
            let slice = &self.data[self.pos..self.pos + length];
            self.pos += length;
            Some(slice)
        } else {
            None
        }
    }

    /// Reads a string prefixed by a 16-bit length
    pub fn read_string(&mut self) -> Option<String> {
        let len = self.read_u16()? as usize;
        let bytes = self.read_bytes(len)?;
        // Tibia strings can be ISO-8859-1. Let's just do lossy UTF-8 for now.
        Some(String::from_utf8_lossy(bytes).into_owned())
    }

    pub fn skip(&mut self, length: usize) -> bool {
        if self.pos + length <= self.data.len() {
            self.pos += length;
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_node() {
        let buf = [NODE_START, 0x01, NODE_END];
        let mut reader = OtbTreeReader::new(&buf);
        let root = reader.parse_root().unwrap();

        assert_eq!(root.node_type, 0x01);
        assert!(root.data.is_empty());
        assert!(root.children.is_empty());
    }

    #[test]
    fn test_node_with_payload() {
        let buf = [NODE_START, 0x01, 0x10, 0x20, 0x30, NODE_END];
        let mut reader = OtbTreeReader::new(&buf);
        let root = reader.parse_root().unwrap();

        assert_eq!(root.data, vec![0x10, 0x20, 0x30]);
    }

    #[test]
    fn test_node_with_children() {
        let buf = [
            NODE_START, 0x01, 0x10, // payload 10
            NODE_START, 0x02, 0x20, NODE_END, // child 1
            NODE_START, 0x03, 0x30, NODE_END, // child 2
            NODE_END,
        ];
        let mut reader = OtbTreeReader::new(&buf);
        let root = reader.parse_root().unwrap();

        assert_eq!(root.node_type, 0x01);
        assert_eq!(root.data, vec![0x10]);
        assert_eq!(root.children.len(), 2);

        assert_eq!(root.children[0].node_type, 0x02);
        assert_eq!(root.children[0].data, vec![0x20]);

        assert_eq!(root.children[1].node_type, 0x03);
        assert_eq!(root.children[1].data, vec![0x30]);
    }

    #[test]
    fn test_escaping() {
        let buf = [
            NODE_START,
            0x01, // node starts
            ESCAPE_CHAR,
            NODE_START, // escaped 0xFE
            ESCAPE_CHAR,
            NODE_END, // escaped 0xFF
            ESCAPE_CHAR,
            ESCAPE_CHAR, // escaped 0xFD
            0x40,        // standard stream byte
            NODE_END,
        ];
        let mut reader = OtbTreeReader::new(&buf);
        let root = reader.parse_root().unwrap();

        assert_eq!(root.data, vec![NODE_START, NODE_END, ESCAPE_CHAR, 0x40]);
    }

    #[test]
    fn test_payload_reader() {
        let payload = vec![0x01, 0x02, 0x03, 0x04, 0x05];
        let mut reader = PayloadReader::new(&payload);

        assert_eq!(reader.read_u8(), Some(0x01));
        assert_eq!(reader.read_u16(), Some(0x0302)); // LE: 02 03
        assert_eq!(reader.read_bytes(2), Some(&[0x04, 0x05][..]));
        assert_eq!(reader.read_u8(), None);
    }
}
