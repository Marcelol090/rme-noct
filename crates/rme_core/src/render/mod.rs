pub mod sprite_atlas;
pub mod sprite_shader;
pub mod wgpu_sprite_renderer;

use pyo3::prelude::*;

pub fn register_python_module(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<sprite_atlas::SpriteAtlas>()?;
    Ok(())
}
