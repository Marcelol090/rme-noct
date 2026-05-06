//! Headless WGPU sprite renderer.
//!
//! M024 fills this module after the Python render-submodule gate is green.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use wgpu::util::DeviceExt;

pub const SPRITE_SIZE: u32 = 32;
pub const RGBA_BYTES_PER_PIXEL: u32 = 4;
pub const CLEAR_RGBA: [u8; 4] = [10, 10, 18, 255];

#[repr(C)]
#[derive(Clone, Copy, bytemuck::Pod, bytemuck::Zeroable)]
struct SpriteUniformRaw {
    offset: [f32; 2],
    scale: [f32; 2],
    layer: u32,
    _pad: [u32; 3],
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeadlessRenderResult {
    pub width: u32,
    pub height: u32,
    pub rgba: Vec<u8>,
    pub rendered_sprite_count: usize,
    pub missing_sprite_count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum HeadlessRendererError {
    AdapterUnavailable,
    DeviceUnavailable(String),
    MapFailed(String),
}

impl From<HeadlessRendererError> for PyErr {
    fn from(error: HeadlessRendererError) -> Self {
        match error {
            HeadlessRendererError::AdapterUnavailable => {
                PyRuntimeError::new_err("WGPU renderer unavailable: no compatible adapter")
            }
            HeadlessRendererError::DeviceUnavailable(message) => {
                PyRuntimeError::new_err(format!("WGPU renderer unavailable: {message}"))
            }
            HeadlessRendererError::MapFailed(message) => {
                PyRuntimeError::new_err(format!("WGPU readback failed: {message}"))
            }
        }
    }
}

pub fn padded_bytes_per_row(width: u32) -> usize {
    let unpadded = width as usize * RGBA_BYTES_PER_PIXEL as usize;
    let align = wgpu::COPY_BYTES_PER_ROW_ALIGNMENT as usize;
    unpadded.div_ceil(align) * align
}

pub fn strip_padded_rows(
    padded: &[u8],
    width: u32,
    height: u32,
    padded_bytes_per_row: usize,
) -> Vec<u8> {
    let tight_row_len = width as usize * RGBA_BYTES_PER_PIXEL as usize;
    let mut tight = Vec::with_capacity(tight_row_len * height as usize);
    for row in 0..height as usize {
        let row_start = row * padded_bytes_per_row;
        tight.extend_from_slice(&padded[row_start..row_start + tight_row_len]);
    }
    tight
}

pub struct HeadlessSpriteRenderer {
    device: wgpu::Device,
    queue: wgpu::Queue,
}

impl HeadlessSpriteRenderer {
    pub fn new() -> Result<Self, HeadlessRendererError> {
        if host_wsl_without_render_node() {
            return Err(HeadlessRendererError::AdapterUnavailable);
        }
        let instance = wgpu::Instance::default();
        let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::LowPower,
            compatible_surface: None,
            force_fallback_adapter: false,
        }))
        .map_err(|_| HeadlessRendererError::AdapterUnavailable)?;
        let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor {
            label: Some("rme_core headless sprite device"),
            required_features: wgpu::Features::empty(),
            required_limits: wgpu::Limits::default(),
            experimental_features: wgpu::ExperimentalFeatures::disabled(),
            memory_hints: wgpu::MemoryHints::Performance,
            trace: wgpu::Trace::Off,
        }))
        .map_err(|error| HeadlessRendererError::DeviceUnavailable(error.to_string()))?;
        Ok(Self { device, queue })
    }

    pub fn render_frame(
        &self,
        width: u32,
        height: u32,
        sprites: &[GpuSpriteCommand],
    ) -> Result<HeadlessRenderResult, HeadlessRendererError> {
        let sprite_texture = self.create_sprite_texture(sprites);
        let sprite_view = sprite_texture.create_view(&wgpu::TextureViewDescriptor {
            dimension: Some(wgpu::TextureViewDimension::D2Array),
            ..Default::default()
        });
        let sampler = self.device.create_sampler(&wgpu::SamplerDescriptor {
            label: Some("rme_core sprite nearest sampler"),
            mag_filter: wgpu::FilterMode::Nearest,
            min_filter: wgpu::FilterMode::Nearest,
            mipmap_filter: wgpu::MipmapFilterMode::Nearest,
            ..Default::default()
        });
        let shader = self
            .device
            .create_shader_module(wgpu::ShaderModuleDescriptor {
                label: Some("rme_core sprite shader"),
                source: wgpu::ShaderSource::Wgsl(
                    crate::render::sprite_shader::SPRITE_SHADER_WGSL.into(),
                ),
            });
        let texture_layout =
            self.device
                .create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
                    label: Some("rme_core sprite texture layout"),
                    entries: &[
                        wgpu::BindGroupLayoutEntry {
                            binding: 0,
                            visibility: wgpu::ShaderStages::FRAGMENT,
                            ty: wgpu::BindingType::Texture {
                                sample_type: wgpu::TextureSampleType::Float { filterable: true },
                                view_dimension: wgpu::TextureViewDimension::D2Array,
                                multisampled: false,
                            },
                            count: None,
                        },
                        wgpu::BindGroupLayoutEntry {
                            binding: 1,
                            visibility: wgpu::ShaderStages::FRAGMENT,
                            ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
                            count: None,
                        },
                    ],
                });
        let uniform_layout =
            self.device
                .create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
                    label: Some("rme_core sprite uniform layout"),
                    entries: &[wgpu::BindGroupLayoutEntry {
                        binding: 0,
                        visibility: wgpu::ShaderStages::VERTEX | wgpu::ShaderStages::FRAGMENT,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Uniform,
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    }],
                });
        let texture_bind_group = self.device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("rme_core sprite texture bind group"),
            layout: &texture_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: wgpu::BindingResource::TextureView(&sprite_view),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: wgpu::BindingResource::Sampler(&sampler),
                },
            ],
        });
        let pipeline = self.create_pipeline(&shader, &texture_layout, &uniform_layout);
        let output = self.device.create_texture(&wgpu::TextureDescriptor {
            label: Some("rme_core headless sprite output"),
            size: wgpu::Extent3d {
                width,
                height,
                depth_or_array_layers: 1,
            },
            mip_level_count: 1,
            sample_count: 1,
            dimension: wgpu::TextureDimension::D2,
            format: wgpu::TextureFormat::Rgba8Unorm,
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
            view_formats: &[],
        });
        let view = output.create_view(&wgpu::TextureViewDescriptor::default());
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor {
                label: Some("rme_core headless sprite encoder"),
            });
        {
            let mut pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("rme_core headless sprite clear pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &view,
                    resolve_target: None,
                    depth_slice: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color {
                            r: f64::from(CLEAR_RGBA[0]) / 255.0,
                            g: f64::from(CLEAR_RGBA[1]) / 255.0,
                            b: f64::from(CLEAR_RGBA[2]) / 255.0,
                            a: 1.0,
                        }),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: None,
                timestamp_writes: None,
                occlusion_query_set: None,
                multiview_mask: None,
            });
            if !sprites.is_empty() {
                pass.set_pipeline(&pipeline);
                pass.set_bind_group(0, &texture_bind_group, &[]);
                for index in sorted_draw_indices(sprites) {
                    let sprite = &sprites[index];
                    let uniform = sprite_uniform(width, height, sprite);
                    let uniform_buffer =
                        self.device
                            .create_buffer_init(&wgpu::util::BufferInitDescriptor {
                                label: Some("rme_core sprite uniform buffer"),
                                contents: bytemuck::bytes_of(&uniform),
                                usage: wgpu::BufferUsages::UNIFORM,
                            });
                    let uniform_bind_group =
                        self.device.create_bind_group(&wgpu::BindGroupDescriptor {
                            label: Some("rme_core sprite uniform bind group"),
                            layout: &uniform_layout,
                            entries: &[wgpu::BindGroupEntry {
                                binding: 0,
                                resource: uniform_buffer.as_entire_binding(),
                            }],
                        });
                    pass.set_bind_group(1, &uniform_bind_group, &[]);
                    pass.draw(0..6, 0..1);
                }
            }
        }
        let rgba = self.read_texture_rgba(&output, width, height, encoder)?;
        Ok(HeadlessRenderResult {
            width,
            height,
            rgba,
            rendered_sprite_count: sprites.len(),
            missing_sprite_count: 0,
        })
    }

    fn create_sprite_texture(&self, sprites: &[GpuSpriteCommand]) -> wgpu::Texture {
        let layers = sprites
            .iter()
            .map(|sprite| sprite.layer)
            .max()
            .unwrap_or(0)
            .saturating_add(1);
        let texture = self.device.create_texture(&wgpu::TextureDescriptor {
            label: Some("rme_core sprite texture array"),
            size: wgpu::Extent3d {
                width: SPRITE_SIZE,
                height: SPRITE_SIZE,
                depth_or_array_layers: layers,
            },
            mip_level_count: 1,
            sample_count: 1,
            dimension: wgpu::TextureDimension::D2,
            format: wgpu::TextureFormat::Rgba8Unorm,
            usage: wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::COPY_DST,
            view_formats: &[],
        });
        for sprite in sprites {
            let upload_pixels = padded_sprite_upload_pixels(&sprite.pixels);
            self.queue.write_texture(
                wgpu::TexelCopyTextureInfo {
                    texture: &texture,
                    mip_level: 0,
                    origin: wgpu::Origin3d {
                        x: 0,
                        y: 0,
                        z: sprite.layer,
                    },
                    aspect: wgpu::TextureAspect::All,
                },
                &upload_pixels,
                wgpu::TexelCopyBufferLayout {
                    offset: 0,
                    bytes_per_row: Some(wgpu::COPY_BYTES_PER_ROW_ALIGNMENT),
                    rows_per_image: Some(SPRITE_SIZE),
                },
                wgpu::Extent3d {
                    width: SPRITE_SIZE,
                    height: SPRITE_SIZE,
                    depth_or_array_layers: 1,
                },
            );
        }
        texture
    }

    fn create_pipeline(
        &self,
        shader: &wgpu::ShaderModule,
        texture_layout: &wgpu::BindGroupLayout,
        uniform_layout: &wgpu::BindGroupLayout,
    ) -> wgpu::RenderPipeline {
        let layout = self
            .device
            .create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
                label: Some("rme_core sprite pipeline layout"),
                bind_group_layouts: &[Some(texture_layout), Some(uniform_layout)],
                immediate_size: 0,
            });
        self.device
            .create_render_pipeline(&wgpu::RenderPipelineDescriptor {
                label: Some("rme_core sprite pipeline"),
                layout: Some(&layout),
                vertex: wgpu::VertexState {
                    module: shader,
                    entry_point: Some("vs_main"),
                    compilation_options: Default::default(),
                    buffers: &[],
                },
                primitive: wgpu::PrimitiveState::default(),
                depth_stencil: None,
                multisample: wgpu::MultisampleState::default(),
                fragment: Some(wgpu::FragmentState {
                    module: shader,
                    entry_point: Some("fs_main"),
                    compilation_options: Default::default(),
                    targets: &[Some(wgpu::ColorTargetState {
                        format: wgpu::TextureFormat::Rgba8Unorm,
                        blend: Some(wgpu::BlendState::ALPHA_BLENDING),
                        write_mask: wgpu::ColorWrites::ALL,
                    })],
                }),
                multiview_mask: None,
                cache: None,
            })
    }

    fn read_texture_rgba(
        &self,
        output: &wgpu::Texture,
        width: u32,
        height: u32,
        mut encoder: wgpu::CommandEncoder,
    ) -> Result<Vec<u8>, HeadlessRendererError> {
        let padded_row = padded_bytes_per_row(width);
        let buffer_size = padded_row as u64 * height as u64;
        let staging = self.device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("rme_core headless sprite readback"),
            size: buffer_size,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });
        encoder.copy_texture_to_buffer(
            wgpu::TexelCopyTextureInfo {
                texture: output,
                mip_level: 0,
                origin: wgpu::Origin3d::ZERO,
                aspect: wgpu::TextureAspect::All,
            },
            wgpu::TexelCopyBufferInfo {
                buffer: &staging,
                layout: wgpu::TexelCopyBufferLayout {
                    offset: 0,
                    bytes_per_row: Some(padded_row as u32),
                    rows_per_image: Some(height),
                },
            },
            wgpu::Extent3d {
                width,
                height,
                depth_or_array_layers: 1,
            },
        );
        self.queue.submit(Some(encoder.finish()));
        let slice = staging.slice(..);
        let (tx, rx) = std::sync::mpsc::channel();
        slice.map_async(wgpu::MapMode::Read, move |result| {
            let _ = tx.send(result);
        });
        let _ = self.device.poll(wgpu::PollType::wait_indefinitely());
        rx.recv()
            .map_err(|error| HeadlessRendererError::MapFailed(error.to_string()))?
            .map_err(|error| HeadlessRendererError::MapFailed(error.to_string()))?;
        let mapped = slice.get_mapped_range();
        let rgba = strip_padded_rows(&mapped, width, height, padded_row);
        drop(mapped);
        staging.unmap();
        Ok(rgba)
    }
}

fn padded_sprite_upload_pixels(pixels: &[u8]) -> Vec<u8> {
    let tight_row = (SPRITE_SIZE * RGBA_BYTES_PER_PIXEL) as usize;
    let padded_row = wgpu::COPY_BYTES_PER_ROW_ALIGNMENT as usize;
    let mut padded = vec![0u8; padded_row * SPRITE_SIZE as usize];
    for row in 0..SPRITE_SIZE as usize {
        let tight_start = row * tight_row;
        let padded_start = row * padded_row;
        padded[padded_start..padded_start + tight_row]
            .copy_from_slice(&pixels[tight_start..tight_start + tight_row]);
    }
    padded
}

fn sorted_draw_indices(sprites: &[GpuSpriteCommand]) -> Vec<usize> {
    let mut indices = (0..sprites.len()).collect::<Vec<_>>();
    indices.sort_by_key(|index| sprites[*index].layer);
    indices
}

fn sprite_uniform(width: u32, height: u32, sprite: &GpuSpriteCommand) -> SpriteUniformRaw {
    let scale = [
        SPRITE_SIZE as f32 / width as f32,
        SPRITE_SIZE as f32 / height as f32,
    ];
    let offset = [
        -1.0 + ((sprite.x as f32 + SPRITE_SIZE as f32 / 2.0) * 2.0 / width as f32),
        1.0 - ((sprite.y as f32 + SPRITE_SIZE as f32 / 2.0) * 2.0 / height as f32),
    ];
    SpriteUniformRaw {
        offset,
        scale,
        layer: sprite.layer,
        _pad: [0; 3],
    }
}

fn host_wsl_without_render_node() -> bool {
    let Ok(version) = std::fs::read_to_string("/proc/version") else {
        return false;
    };
    let is_wsl = version.to_ascii_lowercase().contains("microsoft");
    is_wsl && !std::path::Path::new("/dev/dri").exists()
}

#[derive(Debug, Clone)]
pub struct GpuSpriteCommand {
    pub x: u32,
    pub y: u32,
    pub layer: u32,
    pub sprite_id: u32,
    pub pixels: Vec<u8>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn padded_bytes_per_row_aligns_to_wgpu_copy_pitch() {
        assert_eq!(padded_bytes_per_row(1), 256);
        assert_eq!(padded_bytes_per_row(32), 256);
        assert_eq!(padded_bytes_per_row(64), 256);
        assert_eq!(padded_bytes_per_row(65), 512);
    }

    #[test]
    fn stripped_readback_rows_remove_wgpu_padding() {
        let padded = 256usize;
        let width = 2u32;
        let height = 2u32;
        let mut input = vec![0u8; padded * height as usize];
        input[0..8].copy_from_slice(&[1, 2, 3, 4, 5, 6, 7, 8]);
        input[padded..padded + 8].copy_from_slice(&[9, 10, 11, 12, 13, 14, 15, 16]);

        assert_eq!(
            strip_padded_rows(&input, width, height, padded),
            vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        );
    }

    #[test]
    fn render_empty_frame_returns_clear_rgba() {
        let renderer = match HeadlessSpriteRenderer::new() {
            Ok(renderer) => renderer,
            Err(HeadlessRendererError::AdapterUnavailable) => return,
            Err(error) => panic!("unexpected renderer init error: {error:?}"),
        };

        let result = renderer.render_frame(4, 3, &[]).unwrap();

        assert_eq!(result.width, 4);
        assert_eq!(result.height, 3);
        assert_eq!(result.rendered_sprite_count, 0);
        assert_eq!(result.missing_sprite_count, 0);
        assert_eq!(result.rgba.len(), 4 * 3 * 4);
        assert!(result.rgba.chunks_exact(4).all(|pixel| pixel == CLEAR_RGBA));
    }

    #[test]
    fn padded_sprite_upload_pixels_aligns_each_row_to_wgpu_pitch() {
        let tight_row = (SPRITE_SIZE * RGBA_BYTES_PER_PIXEL) as usize;
        let padded_row = wgpu::COPY_BYTES_PER_ROW_ALIGNMENT as usize;
        let pixels = (0..SPRITE_SIZE * SPRITE_SIZE * RGBA_BYTES_PER_PIXEL)
            .map(|index| (index % 256) as u8)
            .collect::<Vec<_>>();

        let padded = padded_sprite_upload_pixels(&pixels);

        assert_eq!(padded.len(), padded_row * SPRITE_SIZE as usize);
        assert_eq!(&padded[0..tight_row], &pixels[0..tight_row]);
        assert!(padded[tight_row..padded_row].iter().all(|byte| *byte == 0));
        let source_second_row = tight_row..tight_row * 2;
        let padded_second_row = padded_row..padded_row + tight_row;
        assert_eq!(&padded[padded_second_row], &pixels[source_second_row]);
    }

    #[test]
    fn render_one_solid_sprite_writes_sprite_pixels() {
        let renderer = match HeadlessSpriteRenderer::new() {
            Ok(renderer) => renderer,
            Err(HeadlessRendererError::AdapterUnavailable) => return,
            Err(error) => panic!("unexpected renderer init error: {error:?}"),
        };
        let pixels = vec![255u8, 0, 0, 255].repeat((SPRITE_SIZE * SPRITE_SIZE) as usize);
        let sprite = GpuSpriteCommand {
            x: 0,
            y: 0,
            layer: 0,
            sprite_id: 55,
            pixels,
        };

        let result = renderer.render_frame(32, 32, &[sprite]).unwrap();

        assert_eq!(result.rendered_sprite_count, 1);
        assert_eq!(result.missing_sprite_count, 0);
        assert!(result
            .rgba
            .chunks_exact(4)
            .all(|pixel| pixel == [255, 0, 0, 255]));
    }

    #[test]
    fn sprite_draw_order_sorts_by_layer() {
        let sprites = vec![
            GpuSpriteCommand {
                x: 0,
                y: 0,
                layer: 3,
                sprite_id: 3,
                pixels: Vec::new(),
            },
            GpuSpriteCommand {
                x: 0,
                y: 0,
                layer: 1,
                sprite_id: 1,
                pixels: Vec::new(),
            },
            GpuSpriteCommand {
                x: 0,
                y: 0,
                layer: 2,
                sprite_id: 2,
                pixels: Vec::new(),
            },
        ];

        assert_eq!(sorted_draw_indices(&sprites), vec![1, 2, 0]);
    }

    #[test]
    fn higher_layer_draws_last_for_same_tile() {
        let renderer = match HeadlessSpriteRenderer::new() {
            Ok(renderer) => renderer,
            Err(HeadlessRendererError::AdapterUnavailable) => return,
            Err(error) => panic!("unexpected renderer init error: {error:?}"),
        };
        let red = vec![255u8, 0, 0, 255].repeat((SPRITE_SIZE * SPRITE_SIZE) as usize);
        let blue = vec![0u8, 0, 255, 255].repeat((SPRITE_SIZE * SPRITE_SIZE) as usize);
        let sprites = vec![
            GpuSpriteCommand {
                x: 0,
                y: 0,
                layer: 0,
                sprite_id: 55,
                pixels: red,
            },
            GpuSpriteCommand {
                x: 0,
                y: 0,
                layer: 1,
                sprite_id: 77,
                pixels: blue,
            },
        ];

        let result = renderer.render_frame(32, 32, &sprites).unwrap();

        assert!(result
            .rgba
            .chunks_exact(4)
            .all(|pixel| pixel == [0, 0, 255, 255]));
    }
}
