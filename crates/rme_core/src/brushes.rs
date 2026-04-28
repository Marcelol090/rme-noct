//! Brush-domain scaffolding for the Rust core.
//!
//! Keep brush metadata compact and clone-friendly so the editor can share
//! immutable snapshots between UI and worker code.

/// Minimal brush catalog placeholder.
#[derive(Debug, Default, Clone)]
pub struct BrushCatalog;

impl BrushCatalog {
    /// Creates an empty brush catalog.
    pub const fn new() -> Self {
        Self
    }
}
