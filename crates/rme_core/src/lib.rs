#![allow(clippy::too_many_arguments)]
#![allow(clippy::field_reassign_with_default)]
#![allow(clippy::collapsible_match)]
//! Python-facing entrypoint for the Rust core.
//!
//! Architecture note:
//! - Keep heavy map, IO, and render work below the PyO3 boundary.
//! - Prefer data-oriented Rust modules for CPU-bound work.
//! - Use Rayon or dedicated worker threads for parallel work, and detach
//!   from the GIL while long-running Rust code is executing.

use pyo3::prelude::*;

pub mod brushes;
pub mod editor;
pub mod io;
pub mod item;
pub mod map;
pub mod rendering;

/// Returns the version of the rme_core Rust library.
#[pyfunction]
fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

/// Returns basic build information.
#[pyfunction]
fn build_info() -> PyResult<String> {
    Ok(format!(
        "rme_core v{} (Rust {} / PyO3)",
        env!("CARGO_PKG_VERSION"),
        rustc_version(),
    ))
}

fn rustc_version() -> &'static str {
    "stable"
}

/// The main Python module for rme_core.
///
/// Keep this module thin: it should only expose the Python boundary and
/// delegate substantive work to Rust submodules.
#[pymodule]
fn rme_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(build_info, m)?)?;
    m.add_class::<editor::EditorShellState>()?;
    m.add_class::<map::MapStatistics>()?;
    m.add_class::<io::otb::OtbDatabase>()?;
    m.add_class::<io::otb::OtbItem>()?;
    m.add_class::<io::spr::SprDatabase>()?;
    m.add_class::<io::dat::DatDatabase>()?;
    m.add_class::<io::dat::DatItem>()?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version_not_empty() {
        let v = version();
        assert!(!v.is_empty());
        assert!(v.starts_with("0."));
    }
}
