struct VertexOutput {
    @builtin(position) clip_position: vec4<f32>,
    @location(0) tex_coords: vec2<f32>,
};

struct SpriteUniforms {
    offset: vec2<f32>,
    layer: u32,
};

@group(0) @binding(0)
var t_diffuse: texture_2d_array<f32>;
@group(0) @binding(1)
var s_diffuse: sampler;
@group(1) @binding(0)
var<uniform> uniforms: SpriteUniforms;

@vertex
fn vs_main(
    @builtin(vertex_index) vertex_index: u32,
) -> VertexOutput {
    let quad_positions = array<vec2<f32>, 6>(
        vec2<f32>(-1.0, -1.0),
        vec2<f32>(1.0, -1.0),
        vec2<f32>(-1.0, 1.0),
        vec2<f32>(-1.0, 1.0),
        vec2<f32>(1.0, -1.0),
        vec2<f32>(1.0, 1.0),
    );
    let quad_uvs = array<vec2<f32>, 6>(
        vec2<f32>(0.0, 1.0),
        vec2<f32>(1.0, 1.0),
        vec2<f32>(0.0, 0.0),
        vec2<f32>(0.0, 0.0),
        vec2<f32>(1.0, 1.0),
        vec2<f32>(1.0, 0.0),
    );
    let index = vertex_index % 6u;
    let position = quad_positions[index] + uniforms.offset;

    var out: VertexOutput;
    out.tex_coords = quad_uvs[index];
    out.clip_position = vec4<f32>(position, 0.0, 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    return textureSample(t_diffuse, s_diffuse, in.tex_coords, i32(uniforms.layer));
}
