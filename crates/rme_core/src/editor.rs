//! Editor coordination state for the Rust core.
//!
//! This module hosts the first stable shell-facing state bridge without
//! dragging Qt or other UI concerns into Rust.

use std::collections::BTreeMap;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::item::Item;
use crate::map::{
    Creature, House, MapModel, MapPosition, Spawn, Waypoint, DEFAULT_X, DEFAULT_Y, DEFAULT_Z,
};
use crate::rendering::{RenderBudget, RenderState};

/// Minimal editor state placeholder.
#[derive(Debug, Default, Clone)]
pub struct EditorState;

impl EditorState {
    /// Creates an empty editor state.
    pub const fn new() -> Self {
        Self
    }
}

/// PyO3 shell bridge exposing safe editor state to Python.
#[pyclass]
#[derive(Debug, Clone)]
pub struct EditorShellState {
    map: MapModel,
    render: RenderState,
    budget: RenderBudget,
}

impl Default for EditorShellState {
    fn default() -> Self {
        Self {
            map: MapModel::new(),
            render: RenderState::default(),
            budget: RenderBudget::default_budget(),
        }
    }
}

#[pymethods]
impl EditorShellState {
    #[new]
    fn py_new() -> Self {
        Self::default()
    }

    fn position(&self) -> (u16, u16, u8) {
        self.map.position().as_tuple()
    }

    fn set_position(&mut self, x: i32, y: i32, z: i32) -> (u16, u16, u8) {
        self.map.set_position(x, y, z).as_tuple()
    }

    fn floor(&self) -> u8 {
        self.map.position().z()
    }

    fn set_floor(&mut self, z: i32) -> u8 {
        self.map.set_floor(z).z()
    }

    fn zoom_percent(&self) -> u16 {
        self.render.zoom_percent()
    }

    fn set_zoom_percent(&mut self, percent: i32) -> u16 {
        self.render.set_zoom_percent(percent)
    }

    fn show_grid(&self) -> bool {
        self.render.show_grid()
    }

    fn set_show_grid(&mut self, enabled: bool) -> bool {
        self.render.set_show_grid(enabled)
    }

    fn ghost_higher(&self) -> bool {
        self.render.ghost_higher()
    }

    fn set_ghost_higher(&mut self, enabled: bool) -> bool {
        self.render.set_ghost_higher(enabled)
    }

    fn show_lower(&self) -> bool {
        self.render.show_lower()
    }

    fn set_show_lower(&mut self, enabled: bool) -> bool {
        self.render.set_show_lower(enabled)
    }

    fn set_view_flag(&mut self, name: &str, enabled: bool) -> PyResult<bool> {
        self.render
            .set_view_flag(name, enabled)
            .map_err(PyValueError::new_err)
    }

    fn view_flag(&self, name: &str) -> PyResult<bool> {
        self.render.view_flag(name).map_err(PyValueError::new_err)
    }

    fn view_flags(&self) -> BTreeMap<String, bool> {
        self.render.view_flags()
    }

    fn set_show_flag(&mut self, name: &str, enabled: bool) -> PyResult<bool> {
        self.render
            .set_show_flag(name, enabled)
            .map_err(PyValueError::new_err)
    }

    fn show_flag(&self, name: &str) -> PyResult<bool> {
        self.render.show_flag(name).map_err(PyValueError::new_err)
    }

    fn show_flags(&self) -> BTreeMap<String, bool> {
        self.render.show_flags()
    }

    fn recommended_worker_threads(&self) -> usize {
        self.budget.worker_threads_hint
    }

    fn render_summary(&self) -> String {
        self.render.render_summary(self.budget)
    }

    fn reset_defaults(&mut self) -> (u16, u16, u8) {
        self.map = MapModel::new();
        self.render = RenderState::default();
        self.map
            .set_position(
                i32::from(DEFAULT_X),
                i32::from(DEFAULT_Y),
                i32::from(DEFAULT_Z),
            )
            .as_tuple()
    }

    // --- Tile storage bridge ---

    /// Returns tile data as a Python dict-friendly tuple, or None.
    /// Format: (ground_id_or_none, [item_ids], house_id, mapflags)
    fn get_tile_data(&self, x: i32, y: i32, z: i32) -> Option<(Option<u16>, Vec<u16>, u32, u32)> {
        let pos = MapPosition::new(x, y, z);
        self.map.get_tile(&pos).map(|t| {
            let ground_id = t.ground().map(|g| g.id());
            let item_ids: Vec<u16> = t.items().iter().map(|i| i.id()).collect();
            (ground_id, item_ids, t.house_id(), t.mapflags())
        })
    }

    /// Sets ground item on tile at position. Creates tile if needed.
    fn set_tile_ground(&mut self, x: i32, y: i32, z: i32, item_id: u16) -> bool {
        let pos = MapPosition::new(x, y, z);
        self.map
            .get_or_create_tile(pos)
            .set_ground(Some(Item::new(item_id)));
        true
    }

    /// Adds an item to the tile stack at position. Creates tile if needed.
    fn add_tile_item(&mut self, x: i32, y: i32, z: i32, item_id: u16) -> bool {
        let pos = MapPosition::new(x, y, z);
        self.map
            .get_or_create_tile(pos)
            .add_item(Item::new(item_id));
        true
    }

    /// Removes tile at position. Returns true if tile existed.
    fn remove_tile(&mut self, x: i32, y: i32, z: i32) -> bool {
        let pos = MapPosition::new(x, y, z);
        self.map.remove_tile(&pos).is_some()
    }

    /// Returns number of stored tiles.
    fn tile_count(&self) -> usize {
        self.map.tile_count()
    }

    /// Returns (waypoints, spawns, creatures, houses).
    fn sidecar_counts(&self) -> (usize, usize, usize, usize) {
        self.map.sidecar_counts()
    }

    /// Returns the map mutation generation counter.
    fn map_generation(&self) -> u64 {
        self.map.generation()
    }

    // --- XML sidecar bridge ---

    fn add_waypoint(&mut self, name: &str, x: i32, y: i32, z: i32) -> bool {
        self.map
            .add_waypoint(Waypoint::new(name, MapPosition::new(x, y, z)));
        true
    }

    fn add_spawn(&mut self, centerx: i32, centery: i32, centerz: i32, radius: i32) -> usize {
        self.map.add_spawn(Spawn::new(
            MapPosition::new(centerx, centery, centerz),
            radius,
        ))
    }

    fn add_spawn_creature(
        &mut self,
        spawn_index: usize,
        name: &str,
        x: i32,
        y: i32,
        spawntime: u32,
        is_npc: bool,
        direction: u8,
    ) -> PyResult<bool> {
        self.map
            .add_spawn_creature(
                spawn_index,
                Creature::new(name, x, y, spawntime, is_npc, direction),
            )
            .map(|()| true)
            .map_err(PyValueError::new_err)
    }

    fn add_house(
        &mut self,
        houseid: u32,
        name: &str,
        entryx: i32,
        entryy: i32,
        entryz: i32,
        rent: u32,
        townid: u32,
        guildhall: bool,
        size: u32,
    ) -> bool {
        self.map.add_house(House::new(
            houseid,
            name,
            MapPosition::new(entryx, entryy, entryz),
            rent,
            townid,
            guildhall,
            size,
        ));
        true
    }

    // --- OTBM persistence bridge ---

    /// Loads an OTBM map file. Returns (width, height, tile_count) on success.
    fn load_otbm(&mut self, path: &str) -> PyResult<(u16, u16, usize)> {
        let data = std::fs::read(path)
            .map_err(|e| PyValueError::new_err(format!("Failed to read file: {e}")))?;
        let (header, model) = crate::io::otbm::load_otbm(&data)
            .map_err(|e| PyValueError::new_err(format!("OTBM parse error: {e:?}")))?;
        let tile_count = model.tile_count();
        self.map = model;
        crate::io::xml::load_sidecar_xml(&mut self.map, path)
            .map_err(|e| PyValueError::new_err(format!("XML load error: {e}")))?;
        self.map.mark_clean();
        Ok((header.width, header.height, tile_count))
    }

    /// Saves the current map to an OTBM file.
    fn save_otbm(&mut self, path: &str) -> PyResult<()> {
        crate::io::otbm::save_otbm(&self.map, path)
            .map_err(|e| PyValueError::new_err(format!("OTBM save error: {e:?}")))?;
        crate::io::xml::save_sidecar_xml(&self.map, path)
            .map_err(|e| PyValueError::new_err(format!("XML save error: {e}")))?;
        self.map.mark_clean();
        Ok(())
    }

    /// Returns map name.
    fn map_name(&self) -> &str {
        self.map.name()
    }

    /// Returns map description.
    fn map_description(&self) -> &str {
        self.map.description()
    }

    /// Returns true if map has been modified.
    fn map_is_dirty(&self) -> bool {
        self.map.is_dirty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn editor_shell_state_clamps_navigation_and_zoom() {
        let mut shell = EditorShellState::default();
        assert_eq!(shell.set_position(99_999, -4, 99), (65_000, 0, 15));
        assert_eq!(shell.set_floor(6), 6);
        assert_eq!(shell.set_zoom_percent(1), 10);
    }

    #[test]
    fn editor_shell_state_tracks_flags() {
        let mut shell = EditorShellState::default();
        assert!(shell.set_show_grid(true));
        assert!(shell.set_show_flag("show_spawns", true).unwrap());
        assert!(shell.show_flag("show_spawns").unwrap());
        assert!(shell.render_summary().contains("worker_threads="));
    }

    #[test]
    fn editor_bridge_set_and_get_tile() {
        let mut shell = EditorShellState::default();
        assert!(shell.set_tile_ground(100, 200, 7, 4526));
        let data = shell.get_tile_data(100, 200, 7).unwrap();
        assert_eq!(data.0, Some(4526)); // ground_id
        assert!(data.1.is_empty()); // no stack items
        assert_eq!(shell.tile_count(), 1);
    }

    #[test]
    fn editor_bridge_add_tile_item() {
        let mut shell = EditorShellState::default();
        assert!(shell.add_tile_item(100, 200, 7, 2148));
        assert!(shell.add_tile_item(100, 200, 7, 2160));
        let data = shell.get_tile_data(100, 200, 7).unwrap();
        assert_eq!(data.1, vec![2148, 2160]);
    }

    #[test]
    fn editor_bridge_remove_tile() {
        let mut shell = EditorShellState::default();
        shell.set_tile_ground(100, 200, 7, 4526);
        assert!(shell.remove_tile(100, 200, 7));
        assert!(!shell.remove_tile(100, 200, 7)); // already gone
        assert_eq!(shell.tile_count(), 0);
    }

    #[test]
    fn editor_bridge_generation_tracks_mutations() {
        let mut shell = EditorShellState::default();
        assert_eq!(shell.map_generation(), 0);
        shell.set_tile_ground(1, 1, 0, 100);
        assert!(shell.map_generation() > 0);
    }

    #[test]
    fn editor_bridge_stores_xml_sidecar_domains() {
        let mut shell = EditorShellState::default();
        assert!(shell.add_waypoint("Temple", 100, 200, 7));
        let spawn_index = shell.add_spawn(101, 201, 7, 5);
        assert!(shell
            .add_spawn_creature(spawn_index, "Rat", 1, -1, 60, false, 2)
            .unwrap());
        assert!(shell.add_house(12, "Depot", 102, 202, 7, 500, 3, true, 14));
    }

    #[test]
    fn editor_load_otbm_loads_xml_sidecars_and_marks_clean() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("roundtrip.otbm");
        let path_str = path.to_str().unwrap();

        let mut writer = EditorShellState::default();
        assert!(writer.add_waypoint("Temple", 100, 200, 7));
        let spawn_index = writer.add_spawn(101, 201, 7, 5);
        assert!(writer
            .add_spawn_creature(spawn_index, "Rat", 1, -1, 60, false, 2)
            .unwrap());
        assert!(writer.add_house(12, "Depot", 102, 202, 7, 500, 3, true, 14));
        writer.save_otbm(path_str).unwrap();

        let mut reader = EditorShellState::default();
        let loaded = reader.load_otbm(path_str).unwrap();

        assert_eq!(loaded.2, 0);
        assert_eq!(reader.sidecar_counts(), (1, 1, 1, 1));
        assert!(!reader.map_is_dirty());
    }
}
