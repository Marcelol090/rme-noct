//! OTBM map file reader for the Rust core.
//!
//! Reads `.otbm` binary map files into `MapModel`, matching the legacy
//! C++ `iomap_otbm.cpp` + `otbm/` serialization contract.

use crate::io::binary_tree::{OtbNode, OtbTreeReader, ParserError, PayloadReader, PayloadWriter};
use crate::item::Item;
use crate::map::{MapModel, MapPosition, Tile};
use std::collections::BTreeMap;

// ── OTBM Node Types (matches legacy otbm_types.h) ──────────────────

pub const OTBM_ROOTV1: u8 = 1;
pub const OTBM_MAP_DATA: u8 = 2;
pub const OTBM_ITEM_DEF: u8 = 3;
pub const OTBM_TILE_AREA: u8 = 4;
pub const OTBM_TILE: u8 = 5;
pub const OTBM_ITEM: u8 = 6;
pub const OTBM_TILE_SQUARE: u8 = 7;
pub const OTBM_TILE_REF: u8 = 8;
pub const OTBM_SPAWNS: u8 = 9;
pub const OTBM_SPAWN_AREA: u8 = 10;
pub const OTBM_MONSTER: u8 = 11;
pub const OTBM_TOWNS: u8 = 12;
pub const OTBM_TOWN: u8 = 13;
pub const OTBM_HOUSETILE: u8 = 14;
pub const OTBM_WAYPOINTS: u8 = 15;
pub const OTBM_WAYPOINT: u8 = 16;

// ── OTBM Attribute IDs ─────────────────────────────────────────────

pub const OTBM_ATTR_DESCRIPTION: u8 = 1;
pub const OTBM_ATTR_EXT_FILE: u8 = 2;
pub const OTBM_ATTR_TILE_FLAGS: u8 = 3;
pub const OTBM_ATTR_ACTION_ID: u8 = 4;
pub const OTBM_ATTR_UNIQUE_ID: u8 = 5;
pub const OTBM_ATTR_TEXT: u8 = 6;
pub const OTBM_ATTR_DESC: u8 = 7;
pub const OTBM_ATTR_TELE_DEST: u8 = 8;
pub const OTBM_ATTR_ITEM: u8 = 9;
pub const OTBM_ATTR_DEPOT_ID: u8 = 10;
pub const OTBM_ATTR_EXT_SPAWN_FILE: u8 = 11;
pub const OTBM_ATTR_RUNE_CHARGES: u8 = 12;
pub const OTBM_ATTR_EXT_HOUSE_FILE: u8 = 13;
pub const OTBM_ATTR_HOUSEDOORID: u8 = 14;
pub const OTBM_ATTR_COUNT: u8 = 15;
pub const OTBM_ATTR_CHARGES: u8 = 22;
pub const OTBM_ATTR_ATTRIBUTE_MAP: u8 = 128;

// ── Error type ──────────────────────────────────────────────────────

#[derive(Debug, PartialEq)]
pub enum OtbmError {
    TreeParseError(ParserError),
    InvalidRootNode,
    InvalidMapData,
    InvalidTileArea,
    InvalidTile,
    UnexpectedEof,
    UnsupportedVersion(u32),
    IoError(std::io::ErrorKind),
}

impl From<ParserError> for OtbmError {
    fn from(e: ParserError) -> Self {
        OtbmError::TreeParseError(e)
    }
}

impl From<std::io::Error> for OtbmError {
    fn from(e: std::io::Error) -> Self {
        OtbmError::IoError(e.kind())
    }
}

// ── Header ──────────────────────────────────────────────────────────

/// Parsed OTBM root header matching legacy `loadMapRoot`.
#[derive(Debug, Clone, PartialEq)]
pub struct OtbmHeader {
    pub version: u32,
    pub width: u16,
    pub height: u16,
    pub items_major: u32,
    pub items_minor: u32,
}

/// Reads OTBM header from root node payload.
/// Legacy: skip type byte, read u32 version, u16 width, u16 height, u32 major, u32 minor.
pub fn read_header(root: &OtbNode) -> Result<OtbmHeader, OtbmError> {
    let mut r = PayloadReader::new(&root.data);
    // Root payload: [type_byte(1)] [version(4)] [width(2)] [height(2)] [items_major(4)] [items_minor(4)]
    let _type_byte = r.read_u8().ok_or(OtbmError::InvalidRootNode)?;
    let version = r.read_u32().ok_or(OtbmError::InvalidRootNode)?;
    let width = r.read_u16().ok_or(OtbmError::InvalidRootNode)?;
    let height = r.read_u16().ok_or(OtbmError::InvalidRootNode)?;
    let items_major = r.read_u32().ok_or(OtbmError::InvalidRootNode)?;
    let items_minor = r.read_u32().ok_or(OtbmError::InvalidRootNode)?;

    Ok(OtbmHeader {
        version,
        width,
        height,
        items_major,
        items_minor,
    })
}

/// Builds OTBM root node (header) from a MapModel.
pub fn write_header(map: &MapModel) -> OtbNode {
    let mut writer = PayloadWriter::new();
    writer.write_u8(0); // type byte inside payload is 0 for root
    writer.write_u32(2); // version = OTBM v2
    writer.write_u16(map.width() as u16);
    writer.write_u16(map.height() as u16);
    writer.write_u32(1); // items_major
    writer.write_u32(0); // items_minor

    OtbNode {
        node_type: OTBM_ROOTV1,
        data: writer.into_inner(),
        children: vec![],
    }
}

/// Reads map attributes (description, spawnfile, housefile) from MAP_DATA node.
/// Matches legacy `readMapAttributes`.
pub fn read_map_attributes(map_data_node: &OtbNode, map: &mut MapModel) -> Result<(), OtbmError> {
    let mut r = PayloadReader::new(&map_data_node.data);

    // First byte is node type — must be OTBM_MAP_DATA
    let node_type = r.read_u8().ok_or(OtbmError::InvalidMapData)?;
    if node_type != OTBM_MAP_DATA {
        return Err(OtbmError::InvalidMapData);
    }

    // Read attribute loop
    while let Some(attr) = r.read_u8() {
        match attr {
            OTBM_ATTR_DESCRIPTION => {
                let desc = r.read_string().ok_or(OtbmError::UnexpectedEof)?;
                map.set_description(desc);
            }
            OTBM_ATTR_EXT_SPAWN_FILE => {
                let path = r.read_string().ok_or(OtbmError::UnexpectedEof)?;
                map.set_spawnfile(path);
            }
            OTBM_ATTR_EXT_HOUSE_FILE => {
                let path = r.read_string().ok_or(OtbmError::UnexpectedEof)?;
                map.set_housefile(path);
            }
            _ => {
                // Unknown attribute — stop parsing attributes (legacy behavior)
                break;
            }
        }
    }
    Ok(())
}

/// Builds MAP_DATA node with map attributes from a MapModel.
pub fn write_map_attributes(map: &MapModel) -> OtbNode {
    let mut writer = PayloadWriter::new();
    // First byte of payload is node type again
    writer.write_u8(OTBM_MAP_DATA);

    if !map.description().is_empty() {
        writer.write_u8(OTBM_ATTR_DESCRIPTION);
        writer.write_string(map.description());
    }
    if !map.spawnfile().is_empty() {
        writer.write_u8(OTBM_ATTR_EXT_SPAWN_FILE);
        writer.write_string(map.spawnfile());
    }
    if !map.housefile().is_empty() {
        writer.write_u8(OTBM_ATTR_EXT_HOUSE_FILE);
        writer.write_string(map.housefile());
    }

    OtbNode {
        node_type: OTBM_MAP_DATA,
        data: writer.into_inner(),
        children: vec![],
    }
}

// ── S02: Tile Area Reader ───────────────────────────────────────────

/// Reads a single item from an OTBM_ITEM child node.
fn read_item_from_node(node: &OtbNode) -> Result<Item, OtbmError> {
    let mut r = PayloadReader::new(&node.data);

    // First byte is node type check
    let node_type = r.read_u8().ok_or(OtbmError::InvalidTile)?;
    if node_type != OTBM_ITEM {
        return Err(OtbmError::InvalidTile);
    }

    let item_id = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
    let mut item = Item::new(item_id);

    // Read item attributes
    while let Some(attr) = r.read_u8() {
        match attr {
            OTBM_ATTR_COUNT => {
                let count = r.read_u8().ok_or(OtbmError::UnexpectedEof)?;
                item.set_count(count);
            }
            OTBM_ATTR_ACTION_ID => {
                let aid = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
                item.set_action_id(aid);
            }
            OTBM_ATTR_UNIQUE_ID => {
                let uid = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
                item.set_unique_id(uid);
            }
            OTBM_ATTR_CHARGES | OTBM_ATTR_RUNE_CHARGES => {
                let _charges = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
                // charges stored as count for compatibility
            }
            OTBM_ATTR_TEXT | OTBM_ATTR_DESC => {
                let _text = r.read_string().ok_or(OtbmError::UnexpectedEof)?;
                // text/description deferred to attribute map
            }
            OTBM_ATTR_TELE_DEST => {
                // x(2) + y(2) + z(1) = 5 bytes
                if !r.skip(5) {
                    return Err(OtbmError::UnexpectedEof);
                }
            }
            OTBM_ATTR_DEPOT_ID | OTBM_ATTR_HOUSEDOORID => {
                // u16 value we skip
                if !r.skip(2) {
                    return Err(OtbmError::UnexpectedEof);
                }
            }
            _ => {
                // Unknown attribute — stop
                break;
            }
        }
    }
    Ok(item)
}

/// Reads a single tile (OTBM_TILE or OTBM_HOUSETILE) from node.
fn read_tile_from_node(
    node: &OtbNode,
    base_x: u16,
    base_y: u16,
    base_z: u8,
) -> Result<Tile, OtbmError> {
    let mut r = PayloadReader::new(&node.data);

    let node_type = r.read_u8().ok_or(OtbmError::InvalidTile)?;
    let is_house_tile = node_type == OTBM_HOUSETILE;

    if node_type != OTBM_TILE && node_type != OTBM_HOUSETILE {
        return Err(OtbmError::InvalidTile);
    }

    // Tile offset from area base
    let offset_x = r.read_u8().ok_or(OtbmError::UnexpectedEof)? as u16;
    let offset_y = r.read_u8().ok_or(OtbmError::UnexpectedEof)? as u16;

    let pos = MapPosition::new(
        (base_x + offset_x) as i32,
        (base_y + offset_y) as i32,
        base_z as i32,
    );
    let mut tile = Tile::new(pos);

    // House tile has house_id after offsets
    if is_house_tile {
        let house_id = r.read_u32().ok_or(OtbmError::UnexpectedEof)?;
        tile.set_house_id(house_id);
    }

    // Read tile attributes
    while let Some(attr) = r.read_u8() {
        match attr {
            OTBM_ATTR_TILE_FLAGS => {
                let flags = r.read_u32().ok_or(OtbmError::UnexpectedEof)?;
                tile.set_mapflags(flags);
            }
            OTBM_ATTR_ITEM => {
                // Inline item: just an id
                let item_id = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
                let item = Item::new(item_id);
                // First item with no ground = ground
                if tile.ground().is_none() {
                    tile.set_ground(Some(item));
                } else {
                    tile.add_item(item);
                }
            }
            _ => {
                break;
            }
        }
    }

    // Child nodes are full items (OTBM_ITEM)
    for child in &node.children {
        if child.node_type == OTBM_ITEM {
            let item = read_item_from_node(child)?;
            if tile.ground().is_none() {
                tile.set_ground(Some(item));
            } else {
                tile.add_item(item);
            }
        }
    }

    Ok(tile)
}

/// Reads all tile areas from MAP_DATA node children into map.
/// Returns number of tiles loaded.
pub fn read_tile_areas(map_data_node: &OtbNode, map: &mut MapModel) -> Result<u32, OtbmError> {
    let mut tile_count: u32 = 0;

    for child in &map_data_node.children {
        if child.node_type != OTBM_TILE_AREA {
            continue; // skip TOWNS, WAYPOINTS, SPAWNS nodes
        }

        let mut r = PayloadReader::new(&child.data);
        let node_type = r.read_u8().ok_or(OtbmError::InvalidTileArea)?;
        if node_type != OTBM_TILE_AREA {
            return Err(OtbmError::InvalidTileArea);
        }

        // Tile area base position: x(2) + y(2) + z(1)
        let base_x = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
        let base_y = r.read_u16().ok_or(OtbmError::UnexpectedEof)?;
        let base_z = r.read_u8().ok_or(OtbmError::UnexpectedEof)?;

        // Each child of tile_area is a tile
        for tile_node in &child.children {
            let tile = read_tile_from_node(tile_node, base_x, base_y, base_z)?;
            map.set_tile(tile);
            tile_count += 1;
        }
    }

    Ok(tile_count)
}

/// Builds an OTBM_ITEM node for a single item on a stack.
pub fn write_item(item: &Item) -> OtbNode {
    let mut w = PayloadWriter::new();
    w.write_u8(OTBM_ITEM);
    w.write_u16(item.id());

    if item.count() > 1 {
        w.write_u8(OTBM_ATTR_COUNT);
        w.write_u8(item.count());
    }
    if item.action_id() != 0 {
        w.write_u8(OTBM_ATTR_ACTION_ID);
        w.write_u16(item.action_id());
    }
    if item.unique_id() != 0 {
        w.write_u8(OTBM_ATTR_UNIQUE_ID);
        w.write_u16(item.unique_id());
    }

    OtbNode {
        node_type: OTBM_ITEM,
        data: w.into_inner(),
        children: vec![],
    }
}

/// Builds an OTBM_TILE or OTBM_HOUSETILE node from a MapModel Tile.
pub fn write_tile(tile: &Tile, base_x: u16, base_y: u16) -> OtbNode {
    let mut w = PayloadWriter::new();
    let pos = tile.position();
    let offset_x = (pos.x() - base_x) as u8;
    let offset_y = (pos.y() - base_y) as u8;

    let node_type = if tile.is_house_tile() { OTBM_HOUSETILE } else { OTBM_TILE };
    w.write_u8(node_type);
    w.write_u8(offset_x);
    w.write_u8(offset_y);

    if tile.is_house_tile() {
        w.write_u32(tile.house_id());
    }

    if tile.mapflags() != 0 {
        w.write_u8(OTBM_ATTR_TILE_FLAGS);
        w.write_u32(tile.mapflags());
    }

    // Inline item (ground)
    if let Some(ground) = tile.ground() {
        w.write_u8(OTBM_ATTR_ITEM);
        w.write_u16(ground.id());
    }

    let mut children = Vec::new();
    for item in tile.items() {
        children.push(write_item(item));
    }

    OtbNode {
        node_type,
        data: w.into_inner(),
        children,
    }
}

/// Iterates all tiles in the map, groups them by 256x256 areas,
/// and appends OTBM_TILE_AREA nodes to the given map_data_node.
pub fn write_tile_areas(map: &MapModel, map_data_node: &mut OtbNode) {
    let mut areas: BTreeMap<(u16, u16, u8), Vec<&Tile>> = BTreeMap::new();

    for tile in map.iter_tiles() {
        let pos = tile.position();
        let base_x = pos.x() & 0xFF00;
        let base_y = pos.y() & 0xFF00;
        let base_z = pos.z();

        areas.entry((base_x, base_y, base_z)).or_default().push(tile);
    }

    for ((base_x, base_y, base_z), tiles) in areas {
        let mut area_node = OtbNode {
            node_type: OTBM_TILE_AREA,
            data: {
                let mut w = PayloadWriter::new();
                w.write_u8(OTBM_TILE_AREA); // payload type
                w.write_u16(base_x);
                w.write_u16(base_y);
                w.write_u8(base_z);
                w.into_inner()
            },
            children: vec![],
        };

        for tile in tiles {
            area_node.children.push(write_tile(tile, base_x, base_y));
        }

        map_data_node.children.push(area_node);
    }
}

// ── Full OTBM Load ─────────────────────────────────────────────────

/// Loads an OTBM file from raw bytes into a new MapModel.
/// Returns (header, map_model).
pub fn load_otbm(data: &[u8]) -> Result<(OtbmHeader, MapModel), OtbmError> {
    // OTBM files start with 4 zero bytes (identifier), then the node tree
    if data.len() < 4 {
        return Err(OtbmError::UnexpectedEof);
    }

    let mut reader = OtbTreeReader::new(&data[4..]);
    let root = reader.parse_root()?;

    let header = read_header(&root)?;

    let mut map = MapModel::new();
    map.set_dimensions(header.width, header.height);

    // First child of root should be MAP_DATA
    if root.children.is_empty() {
        return Ok((header, map));
    }

    let map_data = &root.children[0];
    read_map_attributes(map_data, &mut map)?;
    read_tile_areas(map_data, &mut map)?;

    // Mark clean after load (loading isn't a user mutation)
    map.mark_clean();

    Ok((header, map))
}

/// Saves a MapModel to an OTBM file at the specified path.
pub fn save_otbm(map: &MapModel, path: &str) -> Result<(), OtbmError> {
    let mut root = write_header(map);
    let mut map_data = write_map_attributes(map);

    write_tile_areas(map, &mut map_data);

    root.children.push(map_data);

    let mut out = Vec::new();
    out.extend_from_slice(&[0u8; 4]); // 4-byte OTBM identifier
    root.write_to(&mut out);

    std::fs::write(path, out)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::io::binary_tree::{ESCAPE_CHAR, NODE_END, NODE_START};

    /// Helper: build a minimal OTBM binary for testing.
    /// Structure: [4 zero bytes] [root node with header + MAP_DATA child]
    fn build_test_otbm(
        description: &str,
        spawnfile: &str,
        housefile: &str,
        tiles: &[(u16, u16, u8, u16)], // (offset_x_from_base, offset_y_from_base, ground_id)
    ) -> Vec<u8> {
        let mut buf = Vec::new();

        // 4-byte OTBM identifier
        buf.extend_from_slice(&[0u8; 4]);

        // Root node start
        buf.push(NODE_START);
        // Root node type byte (inside payload)
        buf.push(OTBM_ROOTV1);
        // Root payload: type(1) + version(4) + width(2) + height(2) + major(4) + minor(4)
        buf.push(0x00); // type byte inside data
        push_u32_le(&mut buf, 2); // version = OTBM v2
        push_u16_le(&mut buf, 256); // width
        push_u16_le(&mut buf, 256); // height
        push_u32_le(&mut buf, 1); // items major
        push_u32_le(&mut buf, 0); // items minor

        // MAP_DATA child
        buf.push(NODE_START);
        buf.push(OTBM_MAP_DATA);
        // MAP_DATA payload: type byte + attributes
        buf.push(OTBM_MAP_DATA);

        // Description attribute
        if !description.is_empty() {
            buf.push(OTBM_ATTR_DESCRIPTION);
            push_string_le(&mut buf, description);
        }
        // Spawnfile attribute
        if !spawnfile.is_empty() {
            buf.push(OTBM_ATTR_EXT_SPAWN_FILE);
            push_string_le(&mut buf, spawnfile);
        }
        // Housefile attribute
        if !housefile.is_empty() {
            buf.push(OTBM_ATTR_EXT_HOUSE_FILE);
            push_string_le(&mut buf, housefile);
        }

        // Tile area child (if tiles provided)
        if !tiles.is_empty() {
            buf.push(NODE_START);
            buf.push(OTBM_TILE_AREA);
            // Tile area payload: type + base_x(2) + base_y(2) + base_z(1)
            buf.push(OTBM_TILE_AREA);
            push_u16_le(&mut buf, 1000); // base_x
            push_u16_le(&mut buf, 1000); // base_y
            buf.push(7); // base_z

            for &(ox, oy, _z, ground_id) in tiles {
                // Tile child
                buf.push(NODE_START);
                buf.push(OTBM_TILE);
                buf.push(OTBM_TILE);
                buf.push(ox as u8); // offset_x
                buf.push(oy as u8); // offset_y
                // Inline ground item
                buf.push(OTBM_ATTR_ITEM);
                push_u16_le(&mut buf, ground_id);
                buf.push(NODE_END); // end tile
            }

            buf.push(NODE_END); // end tile area
        }

        buf.push(NODE_END); // end MAP_DATA
        buf.push(NODE_END); // end root

        buf
    }

    fn push_u16_le(buf: &mut Vec<u8>, val: u16) {
        let bytes = val.to_le_bytes();
        for &b in &bytes {
            push_escaped(buf, b);
        }
    }

    fn push_u32_le(buf: &mut Vec<u8>, val: u32) {
        let bytes = val.to_le_bytes();
        for &b in &bytes {
            push_escaped(buf, b);
        }
    }

    fn push_string_le(buf: &mut Vec<u8>, s: &str) {
        push_u16_le(buf, s.len() as u16);
        for &b in s.as_bytes() {
            push_escaped(buf, b);
        }
    }

    fn push_escaped(buf: &mut Vec<u8>, b: u8) {
        if b == NODE_START || b == NODE_END || b == ESCAPE_CHAR {
            buf.push(ESCAPE_CHAR);
        }
        buf.push(b);
    }

    // ── S01 Tests ───────────────────────────────────────────────────

    #[test]
    fn otbm_header_parsed_correctly() {
        let data = build_test_otbm("", "", "", &[]);
        let (header, _map) = load_otbm(&data).unwrap();
        assert_eq!(header.version, 2);
        assert_eq!(header.width, 256);
        assert_eq!(header.height, 256);
        assert_eq!(header.items_major, 1);
        assert_eq!(header.items_minor, 0);
    }

    #[test]
    fn otbm_map_attributes_parsed() {
        let data = build_test_otbm("Test Map", "spawn.xml", "house.xml", &[]);
        let (_header, map) = load_otbm(&data).unwrap();
        assert_eq!(map.description(), "Test Map");
        assert_eq!(map.spawnfile(), "spawn.xml");
        assert_eq!(map.housefile(), "house.xml");
        assert_eq!(map.width(), 256);
        assert_eq!(map.height(), 256);
    }

    #[test]
    fn otbm_dimensions_set_from_header() {
        let data = build_test_otbm("", "", "", &[]);
        let (_header, map) = load_otbm(&data).unwrap();
        assert_eq!(map.width(), 256);
        assert_eq!(map.height(), 256);
    }

    #[test]
    fn otbm_map_clean_after_load() {
        let data = build_test_otbm("test", "", "", &[]);
        let (_header, map) = load_otbm(&data).unwrap();
        assert!(!map.is_dirty());
    }

    // ── S02 Tests ───────────────────────────────────────────────────

    #[test]
    fn otbm_tile_area_loads_tiles() {
        let tiles = vec![(0, 0, 7, 4526), (1, 0, 7, 4527), (0, 1, 7, 4528)];
        let data = build_test_otbm("", "", "", &tiles);
        let (_header, map) = load_otbm(&data).unwrap();
        assert_eq!(map.tile_count(), 3);
    }

    #[test]
    fn otbm_tile_has_correct_ground() {
        let tiles = vec![(5, 3, 7, 4526)];
        let data = build_test_otbm("", "", "", &tiles);
        let (_header, map) = load_otbm(&data).unwrap();

        let pos = MapPosition::new(1005, 1003, 7);
        let tile = map.get_tile(&pos).expect("tile should exist");
        assert_eq!(tile.ground().unwrap().id(), 4526);
    }

    #[test]
    fn otbm_tile_position_offset_from_base() {
        let tiles = vec![(10, 20, 7, 100)];
        let data = build_test_otbm("", "", "", &tiles);
        let (_header, map) = load_otbm(&data).unwrap();

        // base is 1000,1000,7 + offset 10,20
        let pos = MapPosition::new(1010, 1020, 7);
        assert!(map.get_tile(&pos).is_some());
    }

    #[test]
    fn otbm_empty_map_zero_tiles() {
        let data = build_test_otbm("empty", "", "", &[]);
        let (_header, map) = load_otbm(&data).unwrap();
        assert_eq!(map.tile_count(), 0);
        assert!(map.is_empty());
    }

    #[test]
    fn otbm_too_short_returns_error() {
        let data = vec![0u8; 2];
        assert!(load_otbm(&data).is_err());
    }

    #[test]
    fn test_otbm_roundtrip_serialization() {
        let mut original_map = MapModel::new();
        original_map.set_description("Roundtrip Map");
        original_map.set_spawnfile("spawns.xml");
        original_map.set_housefile("houses.xml");
        original_map.set_dimensions(256, 256);

        let mut t1 = Tile::new(MapPosition::new(1005, 1003, 7));
        t1.set_ground(Some(Item::new(4526)));
        t1.set_mapflags(42);

        let mut item1 = Item::new(100);
        item1.set_count(5);
        t1.add_item(item1);

        let mut item2 = Item::new(200);
        item2.set_action_id(1234);
        item2.set_unique_id(5678);
        t1.add_item(item2);

        original_map.set_tile(t1);

        let mut t2 = Tile::new(MapPosition::new(1006, 1003, 7));
        t2.set_ground(Some(Item::new(4527)));
        t2.set_house_id(99);
        original_map.set_tile(t2);

        // Serialize to bytes using same logic as save_otbm
        let mut root = write_header(&original_map);
        let mut map_data = write_map_attributes(&original_map);
        write_tile_areas(&original_map, &mut map_data);
        root.children.push(map_data);

        let mut out = Vec::new();
        out.extend_from_slice(&[0u8; 4]);
        root.write_to(&mut out);

        // Deserialize
        let (_header, loaded_map) = load_otbm(&out).expect("Failed to load serialized map");

        assert_eq!(loaded_map.description(), original_map.description());
        assert_eq!(loaded_map.spawnfile(), original_map.spawnfile());
        assert_eq!(loaded_map.housefile(), original_map.housefile());
        assert_eq!(loaded_map.width(), original_map.width());
        assert_eq!(loaded_map.height(), original_map.height());
        assert_eq!(loaded_map.tile_count(), original_map.tile_count());

        let t1_loaded = loaded_map.get_tile(&MapPosition::new(1005, 1003, 7)).unwrap();
        assert_eq!(t1_loaded.ground().unwrap().id(), 4526);
        assert_eq!(t1_loaded.mapflags(), 42);
        assert_eq!(t1_loaded.item_count(), 2);
        assert_eq!(t1_loaded.items()[0].id(), 100);
        assert_eq!(t1_loaded.items()[0].count(), 5);
        assert_eq!(t1_loaded.items()[1].id(), 200);
        assert_eq!(t1_loaded.items()[1].action_id(), 1234);
        assert_eq!(t1_loaded.items()[1].unique_id(), 5678);

        let t2_loaded = loaded_map.get_tile(&MapPosition::new(1006, 1003, 7)).unwrap();
        assert_eq!(t2_loaded.ground().unwrap().id(), 4527);
        assert_eq!(t2_loaded.house_id(), 99);
    }
}
