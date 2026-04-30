//! Map-domain primitives for the Rust core.
//!
//! Keep map representation data-oriented so hot paths can stay cache-friendly
//! and easy to parallelize later with Rayon.

use std::collections::HashMap;

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

use crate::item::Item;

pub const DEFAULT_X: u16 = 32_000;
pub const DEFAULT_Y: u16 = 32_000;
pub const DEFAULT_Z: u8 = 7;
pub const MAX_XY: u16 = 65_000;
pub const MAX_Z: u8 = 15;

/// Minimal map position model used by the shell bridge.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct MapPosition {
    x: u16,
    y: u16,
    z: u8,
}

impl MapPosition {
    /// Creates a clamped map position.
    pub fn new(x: i32, y: i32, z: i32) -> Self {
        Self {
            x: x.clamp(0, i32::from(MAX_XY)) as u16,
            y: y.clamp(0, i32::from(MAX_XY)) as u16,
            z: z.clamp(0, i32::from(MAX_Z)) as u8,
        }
    }

    /// Returns the position as a tuple.
    pub const fn as_tuple(self) -> (u16, u16, u8) {
        (self.x, self.y, self.z)
    }

    /// Returns the current X coordinate.
    pub const fn x(self) -> u16 {
        self.x
    }

    /// Returns the current Y coordinate.
    pub const fn y(self) -> u16 {
        self.y
    }

    /// Returns the current floor.
    pub const fn z(self) -> u8 {
        self.z
    }

    /// Returns a copy with an updated floor, clamped to the supported range.
    pub fn with_floor(self, z: i32) -> Self {
        Self::new(i32::from(self.x), i32::from(self.y), z)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Waypoint {
    name: String,
    position: MapPosition,
}

impl Waypoint {
    pub fn new(name: impl Into<String>, position: MapPosition) -> Self {
        Self {
            name: name.into(),
            position,
        }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub const fn position(&self) -> MapPosition {
        self.position
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Creature {
    name: String,
    offset_x: i32,
    offset_y: i32,
    spawntime: u32,
    is_npc: bool,
    direction: u8,
}

impl Creature {
    pub fn new(
        name: impl Into<String>,
        offset_x: i32,
        offset_y: i32,
        spawntime: u32,
        is_npc: bool,
        direction: u8,
    ) -> Self {
        Self {
            name: name.into(),
            offset_x,
            offset_y,
            spawntime,
            is_npc,
            direction,
        }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub const fn offset_x(&self) -> i32 {
        self.offset_x
    }

    pub const fn offset_y(&self) -> i32 {
        self.offset_y
    }

    pub const fn spawntime(&self) -> u32 {
        self.spawntime
    }

    pub const fn is_npc(&self) -> bool {
        self.is_npc
    }

    pub const fn direction(&self) -> u8 {
        self.direction
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Spawn {
    center: MapPosition,
    radius: u32,
    creatures: Vec<Creature>,
}

impl Spawn {
    pub fn new(center: MapPosition, radius: i32) -> Self {
        Self {
            center,
            radius: radius.max(0) as u32,
            creatures: Vec::new(),
        }
    }

    pub const fn center(&self) -> MapPosition {
        self.center
    }

    pub const fn radius(&self) -> u32 {
        self.radius
    }

    pub fn creatures(&self) -> &[Creature] {
        &self.creatures
    }

    pub fn add_creature(&mut self, creature: Creature) {
        self.creatures.push(creature);
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct House {
    id: u32,
    name: String,
    entry: MapPosition,
    rent: u32,
    townid: u32,
    guildhall: bool,
    size: u32,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Town {
    id: u32,
    name: String,
    temple_position: MapPosition,
}

impl Town {
    pub fn new(id: u32, name: impl Into<String>, temple_position: MapPosition) -> Self {
        Self {
            id,
            name: name.into(),
            temple_position,
        }
    }

    pub const fn id(&self) -> u32 {
        self.id
    }

    pub fn set_id(&mut self, id: u32) {
        self.id = id;
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn set_name(&mut self, name: impl Into<String>) {
        self.name = name.into();
    }

    pub const fn temple_position(&self) -> MapPosition {
        self.temple_position
    }

    pub fn set_temple_position(&mut self, pos: MapPosition) {
        self.temple_position = pos;
    }
}

impl House {
    pub fn new(
        id: u32,
        name: impl Into<String>,
        entry: MapPosition,
        rent: u32,
        townid: u32,
        guildhall: bool,
        size: u32,
    ) -> Self {
        Self {
            id,
            name: name.into(),
            entry,
            rent,
            townid,
            guildhall,
            size,
        }
    }

    pub const fn id(&self) -> u32 {
        self.id
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub const fn entry(&self) -> MapPosition {
        self.entry
    }

    pub const fn rent(&self) -> u32 {
        self.rent
    }

    pub const fn townid(&self) -> u32 {
        self.townid
    }

    pub const fn guildhall(&self) -> bool {
        self.guildhall
    }

    pub const fn size(&self) -> u32 {
        self.size
    }
}

#[pyclass]
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct MapStatistics {
    #[pyo3(get)]
    pub tile_count: u64,
    #[pyo3(get)]
    pub blocking_tile_count: u64,
    #[pyo3(get)]
    pub walkable_tile_count: u64,
    #[pyo3(get)]
    pub item_count: u64,
    #[pyo3(get)]
    pub spawn_count: u64,
    #[pyo3(get)]
    pub creature_count: u64,
    #[pyo3(get)]
    pub house_count: u64,
    #[pyo3(get)]
    pub total_house_sqm: u64,
    #[pyo3(get)]
    pub town_count: u64,
    #[pyo3(get)]
    pub waypoint_count: u64,
}

impl MapStatistics {
    pub fn new() -> Self {
        Self::default()
    }
}

/// Tile representation matching legacy C++ tile.h contract.
///
/// Owns a ground item slot, ordered item stack, house association,
/// and flag bitfields for map state and internal status.
#[derive(Debug, Clone, PartialEq)]
pub struct Tile {
    position: MapPosition,
    ground: Option<Item>,
    items: Vec<Item>,
    house_id: u32,
    mapflags: u32,
    statflags: u16,
}

impl Tile {
    /// Creates an empty tile at the given position.
    pub fn new(position: MapPosition) -> Self {
        Self {
            position,
            ground: None,
            items: Vec::new(),
            house_id: 0,
            mapflags: 0,
            statflags: 0,
        }
    }

    pub const fn position(&self) -> MapPosition {
        self.position
    }

    pub fn ground(&self) -> Option<&Item> {
        self.ground.as_ref()
    }

    pub fn set_ground(&mut self, item: Option<Item>) {
        self.ground = item;
    }

    pub fn items(&self) -> &[Item] {
        &self.items
    }

    pub fn add_item(&mut self, item: Item) {
        self.items.push(item);
    }

    pub fn remove_item(&mut self, index: usize) -> Option<Item> {
        if index < self.items.len() {
            Some(self.items.remove(index))
        } else {
            None
        }
    }

    pub fn item_count(&self) -> usize {
        self.items.len()
    }

    /// Total size: ground (if any) + stack items.
    pub fn size(&self) -> usize {
        let ground_count = if self.ground.is_some() { 1 } else { 0 };
        ground_count + self.items.len()
    }

    pub fn is_empty(&self) -> bool {
        self.size() == 0
    }

    pub const fn house_id(&self) -> u32 {
        self.house_id
    }

    pub fn set_house_id(&mut self, id: u32) {
        self.house_id = id;
    }

    pub fn is_house_tile(&self) -> bool {
        self.house_id != 0
    }

    pub const fn mapflags(&self) -> u32 {
        self.mapflags
    }

    pub fn set_mapflags(&mut self, flags: u32) {
        self.mapflags = flags;
    }

    pub const fn statflags(&self) -> u16 {
        self.statflags
    }

    pub fn set_statflags(&mut self, flags: u16) {
        self.statflags = flags;
    }

    /// Legacy TILESTATE_MODIFIED = 0x0040.
    pub fn is_modified(&self) -> bool {
        self.statflags & 0x0040 != 0
    }

    pub fn mark_modified(&mut self) {
        self.statflags |= 0x0040;
    }

    /// TILESTATE_BLOCKING = 0x0004.
    pub fn is_blocking(&self) -> bool {
        self.statflags & 0x0004 != 0
    }

    pub fn set_blocking(&mut self, blocking: bool) {
        if blocking {
            self.statflags |= 0x0004;
        } else {
            self.statflags &= !0x0004;
        }
    }
}

/// Map model with sparse tile storage, viewport position, and map metadata.
#[derive(Debug, Default, Clone)]
pub struct MapModel {
    position: MapPosition,
    tiles: HashMap<MapPosition, Tile>,
    generation: u64,
    // Map metadata — matches legacy map.h header
    name: String,
    description: String,
    width: u16,
    height: u16,
    spawnfile: String,
    housefile: String,
    waypointfile: String,
    waypoints: Vec<Waypoint>,
    spawns: Vec<Spawn>,
    houses: Vec<House>,
    towns: Vec<Town>,
    is_dirty: bool,
}

impl MapModel {
    /// Creates an empty map model.
    pub fn new() -> Self {
        Self {
            position: MapPosition::new(
                i32::from(DEFAULT_X),
                i32::from(DEFAULT_Y),
                i32::from(DEFAULT_Z),
            ),
            tiles: HashMap::new(),
            generation: 0,
            name: String::new(),
            description: String::new(),
            width: 0,
            height: 0,
            spawnfile: String::new(),
            housefile: String::new(),
            waypointfile: String::new(),
            waypoints: Vec::new(),
            spawns: Vec::new(),
            houses: Vec::new(),
            towns: Vec::new(),
            is_dirty: false,
        }
    }

    /// Returns `true` when no tiles are stored.
    pub fn is_empty(&self) -> bool {
        self.tiles.is_empty()
    }

    /// Returns the current viewport position.
    pub const fn position(&self) -> MapPosition {
        self.position
    }

    /// Updates the current viewport position and returns the clamped value.
    pub fn set_position(&mut self, x: i32, y: i32, z: i32) -> MapPosition {
        let next = MapPosition::new(x, y, z);
        self.position = next;
        next
    }

    /// Updates only the floor, preserving X and Y.
    pub fn set_floor(&mut self, z: i32) -> MapPosition {
        let next = self.position.with_floor(z);
        self.position = next;
        next
    }

    /// Returns a reference to the tile at the given position.
    pub fn get_tile(&self, pos: &MapPosition) -> Option<&Tile> {
        self.tiles.get(pos)
    }

    /// Returns a mutable reference to the tile at the given position.
    pub fn get_tile_mut(&mut self, pos: &MapPosition) -> Option<&mut Tile> {
        self.tiles.get_mut(pos)
    }

    /// Returns a mutable reference to the tile, creating an empty one if absent.
    pub fn get_or_create_tile(&mut self, pos: MapPosition) -> &mut Tile {
        self.tiles.entry(pos).or_insert_with(|| {
            self.generation += 1;
            Tile::new(pos)
        })
    }

    /// Inserts or replaces a tile. Returns the previous tile if any.
    pub fn set_tile(&mut self, tile: Tile) -> Option<Tile> {
        self.generation += 1;
        self.tiles.insert(tile.position(), tile)
    }

    /// Removes and returns the tile at the given position.
    pub fn remove_tile(&mut self, pos: &MapPosition) -> Option<Tile> {
        let removed = self.tiles.remove(pos);
        if removed.is_some() {
            self.generation += 1;
        }
        removed
    }

    /// Returns the number of stored tiles.
    pub fn tile_count(&self) -> usize {
        self.tiles.len()
    }

    /// Returns an iterator over all stored tiles.
    pub fn iter_tiles(&self) -> impl Iterator<Item = &Tile> {
        self.tiles.values()
    }

    /// Returns the mutation generation counter.
    pub const fn generation(&self) -> u64 {
        self.generation
    }

    /// Removes all tiles and increments generation.
    pub fn clear(&mut self) {
        if !self.tiles.is_empty() {
            self.tiles.clear();
            self.generation += 1;
        }
    }

    // --- Map metadata accessors ---

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn set_name(&mut self, name: impl Into<String>) {
        self.name = name.into();
        self.is_dirty = true;
    }

    pub fn description(&self) -> &str {
        &self.description
    }

    pub fn set_description(&mut self, desc: impl Into<String>) {
        self.description = desc.into();
        self.is_dirty = true;
    }

    pub const fn width(&self) -> u16 {
        self.width
    }

    pub const fn height(&self) -> u16 {
        self.height
    }

    pub fn set_dimensions(&mut self, width: u16, height: u16) {
        self.width = width;
        self.height = height;
        self.is_dirty = true;
    }

    pub fn spawnfile(&self) -> &str {
        &self.spawnfile
    }

    pub fn set_spawnfile(&mut self, path: impl Into<String>) {
        self.spawnfile = path.into();
    }

    pub fn housefile(&self) -> &str {
        &self.housefile
    }

    pub fn set_housefile(&mut self, path: impl Into<String>) {
        self.housefile = path.into();
    }

    pub fn waypointfile(&self) -> &str {
        &self.waypointfile
    }

    pub fn set_waypointfile(&mut self, path: impl Into<String>) {
        self.waypointfile = path.into();
    }

    pub fn waypoints(&self) -> &[Waypoint] {
        &self.waypoints
    }

    pub fn spawns(&self) -> &[Spawn] {
        &self.spawns
    }

    pub fn houses(&self) -> &[House] {
        &self.houses
    }

    pub fn towns(&self) -> &[Town] {
        &self.towns
    }

    pub fn add_town(&mut self, town: Town) {
        self.towns.push(town);
        self.is_dirty = true;
    }

    pub fn remove_town(&mut self, town_id: u32) -> bool {
        let len_before = self.towns.len();
        self.towns.retain(|t| t.id() != town_id);
        let removed = self.towns.len() < len_before;
        if removed {
            self.is_dirty = true;
        }
        removed
    }



    pub fn add_waypoint(&mut self, waypoint: Waypoint) {
        self.waypoints.push(waypoint);
        self.is_dirty = true;
    }

    pub fn add_spawn(&mut self, spawn: Spawn) -> usize {
        self.spawns.push(spawn);
        self.is_dirty = true;
        self.spawns.len() - 1
    }

    pub fn add_spawn_creature(
        &mut self,
        spawn_index: usize,
        creature: Creature,
    ) -> Result<(), String> {
        let spawn = self
            .spawns
            .get_mut(spawn_index)
            .ok_or_else(|| format!("Unknown spawn index: {spawn_index}"))?;
        spawn.add_creature(creature);
        self.is_dirty = true;
        Ok(())
    }

    pub fn add_house(&mut self, house: House) {
        self.houses.push(house);
        self.is_dirty = true;
    }

    pub const fn is_dirty(&self) -> bool {
        self.is_dirty
    }

    pub fn mark_clean(&mut self) {
        self.is_dirty = false;
    }

    /// Collects map statistics by iterating over all tiles and metadata.
    ///
    /// Performance: Synchronous iteration over the tile hashmap.
    pub fn collect_statistics(&self) -> MapStatistics {
        let mut stats = MapStatistics {
            tile_count: self.tiles.len() as u64,
            spawn_count: self.spawns.len() as u64,
            house_count: self.houses.len() as u64,
            waypoint_count: self.waypoints.len() as u64,
            town_count: self.towns.len() as u64,
            ..Default::default()
        };
        for house in &self.houses {
            stats.total_house_sqm += house.size() as u64;
        }

        for spawn in &self.spawns {
            stats.creature_count += spawn.creatures().len() as u64;
        }

        for tile in self.tiles.values() {
            if tile.is_blocking() {
                stats.blocking_tile_count += 1;
            } else {
                stats.walkable_tile_count += 1;
            }

            stats.item_count += tile.size() as u64;
        }

        stats
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn map_position_clamps_to_supported_bounds() {
        let position = MapPosition::new(99_999, -10, 99);
        assert_eq!(position.as_tuple(), (MAX_XY, 0, MAX_Z));
    }

    #[test]
    fn map_model_updates_floor_without_touching_xy() {
        let mut model = MapModel::new();
        model.set_position(32123, 32234, 7);
        let updated = model.set_floor(3);
        assert_eq!(updated.as_tuple(), (32123, 32234, 3));
    }

    // --- Tile tests ---

    #[test]
    fn tile_new_is_empty() {
        let tile = Tile::new(MapPosition::new(100, 200, 7));
        assert!(tile.is_empty());
        assert_eq!(tile.size(), 0);
        assert!(tile.ground().is_none());
        assert_eq!(tile.item_count(), 0);
        assert_eq!(tile.house_id(), 0);
        assert!(!tile.is_house_tile());
        assert!(!tile.is_modified());
    }

    #[test]
    fn tile_set_ground_makes_non_empty() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        tile.set_ground(Some(Item::new(4526)));
        assert!(!tile.is_empty());
        assert_eq!(tile.size(), 1);
        assert_eq!(tile.ground().unwrap().id(), 4526);
    }

    #[test]
    fn tile_add_items_to_stack() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        tile.add_item(Item::new(2148));
        tile.add_item(Item::new(2160));
        assert_eq!(tile.item_count(), 2);
        assert_eq!(tile.items()[0].id(), 2148);
        assert_eq!(tile.items()[1].id(), 2160);
    }

    #[test]
    fn tile_remove_item_by_index() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        tile.add_item(Item::new(2148));
        tile.add_item(Item::new(2160));
        let removed = tile.remove_item(0);
        assert_eq!(removed.unwrap().id(), 2148);
        assert_eq!(tile.item_count(), 1);
        assert_eq!(tile.items()[0].id(), 2160);
    }

    #[test]
    fn tile_remove_item_out_of_bounds_returns_none() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        assert!(tile.remove_item(0).is_none());
    }

    #[test]
    fn tile_size_counts_ground_plus_items() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        tile.set_ground(Some(Item::new(4526)));
        tile.add_item(Item::new(2148));
        assert_eq!(tile.size(), 2);
    }

    #[test]
    fn tile_house_id_operations() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        assert!(!tile.is_house_tile());
        tile.set_house_id(42);
        assert!(tile.is_house_tile());
        assert_eq!(tile.house_id(), 42);
    }

    #[test]
    fn tile_flag_operations() {
        let mut tile = Tile::new(MapPosition::new(100, 200, 7));
        tile.set_mapflags(0x0001); // PZ
        assert_eq!(tile.mapflags(), 0x0001);
        tile.mark_modified();
        assert!(tile.is_modified());
    }

    // --- MapModel tile storage tests ---

    #[test]
    fn map_model_starts_empty() {
        let model = MapModel::new();
        assert!(model.is_empty());
        assert_eq!(model.tile_count(), 0);
        assert_eq!(model.generation(), 0);
    }

    #[test]
    fn map_model_set_tile_increments_generation() {
        let mut model = MapModel::new();
        let tile = Tile::new(MapPosition::new(100, 200, 7));
        model.set_tile(tile);
        assert_eq!(model.tile_count(), 1);
        assert_eq!(model.generation(), 1);
        assert!(!model.is_empty());
    }

    #[test]
    fn map_model_get_tile_returns_stored() {
        let mut model = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);
        let mut tile = Tile::new(pos);
        tile.set_ground(Some(Item::new(4526)));
        model.set_tile(tile);
        let got = model.get_tile(&pos).unwrap();
        assert_eq!(got.ground().unwrap().id(), 4526);
    }

    #[test]
    fn map_model_remove_tile_decrements_count() {
        let mut model = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);
        model.set_tile(Tile::new(pos));
        assert_eq!(model.tile_count(), 1);
        let removed = model.remove_tile(&pos);
        assert!(removed.is_some());
        assert_eq!(model.tile_count(), 0);
        assert_eq!(model.generation(), 2); // set + remove
    }

    #[test]
    fn map_model_remove_nonexistent_no_generation_bump() {
        let mut model = MapModel::new();
        let pos = MapPosition::new(999, 999, 0);
        let removed = model.remove_tile(&pos);
        assert!(removed.is_none());
        assert_eq!(model.generation(), 0);
    }

    #[test]
    fn map_model_clear_empties_tiles() {
        let mut model = MapModel::new();
        model.set_tile(Tile::new(MapPosition::new(1, 1, 0)));
        model.set_tile(Tile::new(MapPosition::new(2, 2, 0)));
        assert_eq!(model.tile_count(), 2);
        model.clear();
        assert!(model.is_empty());
        assert_eq!(model.generation(), 3); // 2 sets + 1 clear
    }

    #[test]
    fn map_model_clear_empty_no_generation_bump() {
        let mut model = MapModel::new();
        model.clear();
        assert_eq!(model.generation(), 0);
    }

    #[test]
    fn map_model_replace_tile_returns_old() {
        let mut model = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);
        let mut t1 = Tile::new(pos);
        t1.set_ground(Some(Item::new(100)));
        model.set_tile(t1);

        let mut t2 = Tile::new(pos);
        t2.set_ground(Some(Item::new(200)));
        let old = model.set_tile(t2);
        assert_eq!(old.unwrap().ground().unwrap().id(), 100);
        assert_eq!(model.get_tile(&pos).unwrap().ground().unwrap().id(), 200);
    }

    // --- Map metadata tests ---

    #[test]
    fn map_metadata_defaults_empty() {
        let model = MapModel::new();
        assert_eq!(model.name(), "");
        assert_eq!(model.description(), "");
        assert_eq!(model.width(), 0);
        assert_eq!(model.height(), 0);
        assert_eq!(model.spawnfile(), "");
        assert_eq!(model.housefile(), "");
        assert_eq!(model.waypointfile(), "");
        assert!(!model.is_dirty());
    }

    #[test]
    fn map_metadata_set_name_marks_dirty() {
        let mut model = MapModel::new();
        model.set_name("Test Map");
        assert_eq!(model.name(), "Test Map");
        assert!(model.is_dirty());
    }

    #[test]
    fn map_metadata_set_description_marks_dirty() {
        let mut model = MapModel::new();
        model.set_description("A test map");
        assert_eq!(model.description(), "A test map");
        assert!(model.is_dirty());
    }

    #[test]
    fn map_metadata_set_dimensions_marks_dirty() {
        let mut model = MapModel::new();
        model.set_dimensions(256, 256);
        assert_eq!(model.width(), 256);
        assert_eq!(model.height(), 256);
        assert!(model.is_dirty());
    }

    #[test]
    fn map_metadata_mark_clean_clears_dirty() {
        let mut model = MapModel::new();
        model.set_name("dirty");
        assert!(model.is_dirty());
        model.mark_clean();
        assert!(!model.is_dirty());
    }

    #[test]
    fn map_metadata_file_paths() {
        let mut model = MapModel::new();
        model.set_spawnfile("spawn.xml");
        model.set_housefile("house.xml");
        model.set_waypointfile("waypoint.xml");
        assert_eq!(model.spawnfile(), "spawn.xml");
        assert_eq!(model.housefile(), "house.xml");
        assert_eq!(model.waypointfile(), "waypoint.xml");
    }

    #[test]
    fn map_model_town_operations() {
        let mut model = MapModel::new();
        let town = Town::new(1, "Thais", MapPosition::new(100, 100, 7));
        model.add_town(town);
        assert_eq!(model.towns().len(), 1);
        assert_eq!(model.towns()[0].name(), "Thais");
        assert!(model.is_dirty());

        let removed = model.remove_town(1);
        assert!(removed);
        assert_eq!(model.towns().len(), 0);
    }

    #[test]
    fn map_dirty_from_tile_mutation() {
        let mut model = MapModel::new();
        assert!(!model.is_dirty());
        // Tile mutations track via generation, not dirty flag.
        // dirty flag is metadata-only. This is by design.
        model.set_tile(Tile::new(MapPosition::new(1, 1, 0)));
        assert!(!model.is_dirty()); // tile ops don't set metadata dirty
        assert_eq!(model.generation(), 1); // generation tracks tile ops
    }

    #[test]
    fn map_model_stores_xml_sidecar_domains() {
        let mut model = MapModel::new();
        model.add_waypoint(Waypoint::new("Depot", MapPosition::new(10, 20, 7)));
        let spawn_index = model.add_spawn(Spawn::new(MapPosition::new(11, 21, 7), 5));
        model
            .add_spawn_creature(spawn_index, Creature::new("Rat", 1, -1, 60, false, 2))
            .unwrap();
        model.add_house(House::new(
            12,
            "House",
            MapPosition::new(12, 22, 7),
            500,
            3,
            true,
            14,
        ));

        assert_eq!(model.waypoints()[0].name(), "Depot");
        assert_eq!(model.spawns()[0].creatures()[0].name(), "Rat");
        assert_eq!(model.houses()[0].id(), 12);
        assert!(model.is_dirty());
    }

    #[test]
    fn map_model_collects_statistics_from_tiles_and_sidecars() {
        let mut model = MapModel::new();

        let mut walkable = Tile::new(MapPosition::new(1, 1, 7));
        walkable.set_ground(Some(Item::new(100)));
        walkable.add_item(Item::new(200));
        model.set_tile(walkable);

        let mut blocking = Tile::new(MapPosition::new(2, 1, 7));
        blocking.set_blocking(true);
        blocking.add_item(Item::new(300));
        model.set_tile(blocking);

        model.add_waypoint(Waypoint::new("Depot", MapPosition::new(10, 20, 7)));
        let spawn_index = model.add_spawn(Spawn::new(MapPosition::new(11, 21, 7), 5));
        model
            .add_spawn_creature(spawn_index, Creature::new("Rat", 1, -1, 60, false, 2))
            .unwrap();
        model
            .add_spawn_creature(spawn_index, Creature::new("Guide", 0, 0, 30, true, 0))
            .unwrap();
        model.add_house(House::new(
            12,
            "House",
            MapPosition::new(12, 22, 7),
            500,
            3,
            true,
            14,
        ));

        let stats = model.collect_statistics();

        assert_eq!(stats.tile_count, 2);
        assert_eq!(stats.walkable_tile_count, 1);
        assert_eq!(stats.blocking_tile_count, 1);
        assert_eq!(stats.item_count, 3);
        assert_eq!(stats.spawn_count, 1);
        assert_eq!(stats.creature_count, 2);
        assert_eq!(stats.waypoint_count, 1);
        assert_eq!(stats.house_count, 1);
        assert_eq!(stats.total_house_sqm, 14);
        model.add_town(Town::new(1, "Thais", MapPosition::new(1, 1, 7)));
        let stats = model.collect_statistics();
        assert_eq!(stats.town_count, 1);
    }
}
