//! File I/O support for Tibia legacy formats.
//!
//! Submodules support parsing definitions, client catalogs, and sprites.

pub mod binary_tree;
pub mod dat;
pub mod items;
pub mod otb;
pub mod otbm;
pub mod spr;
pub mod xml;

pub use dat::{DatDatabase, DatItem};
pub use items::{parse_items, ItemType, ItemsXmlError};
pub use otb::{OtbDatabase, OtbItem};
pub use spr::SprDatabase;

/// Minimal IO plan placeholder for future read/write operations.
#[derive(Debug, Default, Clone, Copy)]
pub struct IoPlan {
    /// Hint that future implementations may batch or parallelize IO work.
    pub threaded: bool,
}

impl IoPlan {
    /// Returns a conservative single-threaded IO plan.
    pub const fn single_threaded() -> Self {
        Self { threaded: false }
    }
}
