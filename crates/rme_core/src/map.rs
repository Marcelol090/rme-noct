//! Map-domain primitives for the Rust core.
//!
//! Keep map representation data-oriented so hot paths can stay cache-friendly
//! and easy to parallelize later with Rayon.

use serde::{Deserialize, Serialize};

pub const DEFAULT_X: u16 = 32_000;
pub const DEFAULT_Y: u16 = 32_000;
pub const DEFAULT_Z: u8 = 7;
pub const MAX_XY: u16 = 65_000;
pub const MAX_Z: u8 = 15;

/// Minimal map position model used by the shell bridge.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
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

/// Minimal map model placeholder for the Rust-first split.
#[derive(Debug, Default, Clone)]
pub struct MapModel {
    position: MapPosition,
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
        }
    }

    /// Returns `true` for the current scaffolded state.
    pub const fn is_empty(&self) -> bool {
        true
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
}
