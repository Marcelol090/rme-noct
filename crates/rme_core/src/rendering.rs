//! Rendering-adjacent state for the Rust core.
//!
//! Keep rendering preparation separate from the Python UI layer so future
//! frame assembly can be parallelized or moved to a dedicated backend.

use std::collections::BTreeMap;
use std::thread;

pub const MIN_ZOOM_PERCENT: u16 = 10;
pub const MAX_ZOOM_PERCENT: u16 = 800;
pub const DEFAULT_ZOOM_PERCENT: u16 = 100;

pub const VIEW_FLAG_NAMES: &[&str] = &[
    "show_all_floors",
    "show_as_minimap",
    "show_only_colors",
    "show_only_modified",
    "always_show_zones",
    "extended_house_shader",
    "show_tooltips",
    "show_client_box",
    "ghost_loose_items",
    "show_shade",
];

pub const SHOW_FLAG_NAMES: &[&str] = &[
    "show_animation",
    "show_light",
    "show_light_strength",
    "show_technical_items",
    "show_invalid_tiles",
    "show_invalid_zones",
    "show_creatures",
    "show_spawns",
    "show_special",
    "show_houses",
    "show_pathing",
    "show_towns",
    "show_waypoints",
    "highlight_items",
    "highlight_locked_doors",
    "show_wall_hooks",
];

fn default_flags(names: &[&str]) -> BTreeMap<String, bool> {
    names
        .iter()
        .map(|name| ((*name).to_string(), false))
        .collect()
}

/// Rendering state mirrored into the Python shell.
#[derive(Debug, Clone)]
pub struct RenderState {
    zoom_percent: u16,
    show_grid: bool,
    ghost_higher: bool,
    show_lower: bool,
    view_flags: BTreeMap<String, bool>,
    show_flags: BTreeMap<String, bool>,
}

impl Default for RenderState {
    fn default() -> Self {
        Self {
            zoom_percent: DEFAULT_ZOOM_PERCENT,
            show_grid: false,
            ghost_higher: false,
            show_lower: true,
            view_flags: default_flags(VIEW_FLAG_NAMES),
            show_flags: default_flags(SHOW_FLAG_NAMES),
        }
    }
}

impl RenderState {
    /// Returns the current zoom percent.
    pub const fn zoom_percent(&self) -> u16 {
        self.zoom_percent
    }

    /// Updates the zoom percent and returns the clamped value.
    pub fn set_zoom_percent(&mut self, percent: i32) -> u16 {
        self.zoom_percent =
            percent.clamp(i32::from(MIN_ZOOM_PERCENT), i32::from(MAX_ZOOM_PERCENT)) as u16;
        self.zoom_percent
    }

    /// Returns whether the grid overlay is enabled.
    pub const fn show_grid(&self) -> bool {
        self.show_grid
    }

    /// Enables or disables the grid overlay.
    pub fn set_show_grid(&mut self, enabled: bool) -> bool {
        self.show_grid = enabled;
        self.show_grid
    }

    /// Returns whether higher floors are ghosted.
    pub const fn ghost_higher(&self) -> bool {
        self.ghost_higher
    }

    /// Enables or disables higher-floor ghosting.
    pub fn set_ghost_higher(&mut self, enabled: bool) -> bool {
        self.ghost_higher = enabled;
        self.ghost_higher
    }

    /// Returns whether lower floors remain visible.
    pub const fn show_lower(&self) -> bool {
        self.show_lower
    }

    /// Enables or disables lower-floor visibility.
    pub fn set_show_lower(&mut self, enabled: bool) -> bool {
        self.show_lower = enabled;
        self.show_lower
    }

    /// Returns a copy of all view flags.
    pub fn view_flags(&self) -> BTreeMap<String, bool> {
        self.view_flags.clone()
    }

    /// Returns a copy of all show flags.
    pub fn show_flags(&self) -> BTreeMap<String, bool> {
        self.show_flags.clone()
    }

    /// Returns one named view flag.
    pub fn view_flag(&self, name: &str) -> Result<bool, String> {
        self.view_flags
            .get(name)
            .copied()
            .ok_or_else(|| format!("unknown view flag: {name}"))
    }

    /// Returns one named show flag.
    pub fn show_flag(&self, name: &str) -> Result<bool, String> {
        self.show_flags
            .get(name)
            .copied()
            .ok_or_else(|| format!("unknown show flag: {name}"))
    }

    /// Updates one named view flag and returns the resulting value.
    pub fn set_view_flag(&mut self, name: &str, enabled: bool) -> Result<bool, String> {
        let entry = self
            .view_flags
            .get_mut(name)
            .ok_or_else(|| format!("unknown view flag: {name}"))?;
        *entry = enabled;
        Ok(*entry)
    }

    /// Updates one named show flag and returns the resulting value.
    pub fn set_show_flag(&mut self, name: &str, enabled: bool) -> Result<bool, String> {
        let entry = self
            .show_flags
            .get_mut(name)
            .ok_or_else(|| format!("unknown show flag: {name}"))?;
        *entry = enabled;
        Ok(*entry)
    }

    /// Returns a concise rendering summary for the shell.
    pub fn render_summary(&self, budget: RenderBudget) -> String {
        format!(
            "zoom={}%, grid={}, ghost_higher={}, show_lower={}, worker_threads={}",
            self.zoom_percent,
            if self.show_grid { "on" } else { "off" },
            if self.ghost_higher { "on" } else { "off" },
            if self.show_lower { "on" } else { "off" },
            budget.worker_threads_hint,
        )
    }
}

/// Minimal render budget placeholder.
#[derive(Debug, Default, Clone, Copy)]
pub struct RenderBudget {
    /// Suggested worker count for background preparation.
    pub worker_threads_hint: usize,
}

impl RenderBudget {
    /// Creates a budget aligned with the current machine parallelism.
    pub fn default_budget() -> Self {
        let detected = thread::available_parallelism()
            .map(|count| count.get())
            .unwrap_or(1);
        Self {
            worker_threads_hint: detected.clamp(1, 16),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn render_budget_uses_positive_worker_hint() {
        assert!(RenderBudget::default_budget().worker_threads_hint >= 1);
    }

    #[test]
    fn render_state_clamps_zoom_and_updates_flags() {
        let mut state = RenderState::default();
        assert_eq!(state.set_zoom_percent(2_000), MAX_ZOOM_PERCENT);
        assert!(state.set_show_grid(true));
        assert!(state.set_view_flag("show_all_floors", true).unwrap());
        assert!(state.view_flag("show_all_floors").unwrap());
    }

    #[test]
    fn render_state_rejects_unknown_flags() {
        let mut state = RenderState::default();
        let error = state.set_show_flag("missing_flag", true).unwrap_err();
        assert!(error.contains("unknown show flag"));
    }
}
