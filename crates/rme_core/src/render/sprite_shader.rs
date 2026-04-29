pub const SPRITE_SHADER_WGSL: &str = include_str!("sprite.wgsl");

pub fn validate_sprite_shader_wgsl() -> Result<(), String> {
    validate_wgsl_source(SPRITE_SHADER_WGSL)
}

fn validate_wgsl_source(source: &str) -> Result<(), String> {
    let module = naga::front::wgsl::parse_str(source)
        .map_err(|error| format!("sprite WGSL parse failed: {error}"))?;

    naga::valid::Validator::new(
        naga::valid::ValidationFlags::all(),
        naga::valid::Capabilities::all(),
    )
    .validate(&module)
    .map_err(|error| format!("sprite WGSL validation failed: {error}"))?;

    Ok(())
}

#[allow(dead_code)]
fn main() -> std::process::ExitCode {
    match validate_sprite_shader_wgsl() {
        Ok(()) => {
            println!("sprite WGSL validated with naga");
            std::process::ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("{error}");
            std::process::ExitCode::FAILURE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{validate_sprite_shader_wgsl, SPRITE_SHADER_WGSL};

    #[test]
    fn sprite_shader_wgsl_validates_with_naga() {
        validate_sprite_shader_wgsl().expect("sprite WGSL should validate with naga");
    }

    #[test]
    fn sprite_shader_declares_sprite_uniforms_and_bindings() {
        assert!(SPRITE_SHADER_WGSL.contains("struct SpriteUniforms"));
        assert!(SPRITE_SHADER_WGSL.contains("offset: vec2<f32>"));
        assert!(SPRITE_SHADER_WGSL.contains("layer"));
        assert!(SPRITE_SHADER_WGSL.contains("@group(0) @binding(0)"));
        assert!(SPRITE_SHADER_WGSL.contains("texture_2d_array<f32>"));
        assert!(SPRITE_SHADER_WGSL.contains("@group(0) @binding(1)"));
        assert!(SPRITE_SHADER_WGSL.contains("@group(1) @binding(0)"));
    }

    #[test]
    fn sprite_shader_defines_textured_triangle_list_quad() {
        assert!(SPRITE_SHADER_WGSL.contains("array<vec2<f32>, 6>"));
        assert!(SPRITE_SHADER_WGSL.contains("quad_positions"));
        assert!(SPRITE_SHADER_WGSL.contains("quad_uvs"));
        assert!(SPRITE_SHADER_WGSL.contains("uniforms.offset"));
        assert!(SPRITE_SHADER_WGSL.contains("uniforms.layer"));
    }

    #[test]
    fn sprite_shader_does_not_claim_render_pass_clear_color() {
        assert!(!SPRITE_SHADER_WGSL.contains("clear color"));
        assert!(!SPRITE_SHADER_WGSL.contains("Void Black"));
        assert!(!SPRITE_SHADER_WGSL.contains("#0A0A12"));
    }
}
