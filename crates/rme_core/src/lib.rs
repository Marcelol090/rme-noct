use pyo3::prelude::*;

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

/// The main Python module for rme_core, providing high-performance
/// Rust bindings for map editing operations.
#[pymodule]
fn rme_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(build_info, m)?)?;

    // Future submodules will be registered here:
    // m.add_submodule(&map_module)?;
    // m.add_submodule(&io_module)?;
    // m.add_submodule(&rendering_module)?;
    // m.add_submodule(&brushes_module)?;
    // m.add_submodule(&editor_module)?;

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
