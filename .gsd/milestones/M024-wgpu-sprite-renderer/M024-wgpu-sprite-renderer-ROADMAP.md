# M024 WGPU Sprite Renderer Roadmap

## S01: Headless WGPU Sprite Renderer

Render staged 32x32 RGBA sprite payloads through WGPU into tightly packed RGBA output bytes, exposed through PyO3.

## Later Slices

- UI canvas consumption of headless RGBA output.
- Atlas packing and texture reuse.
- Animation and lighting.
- Minimap renderer reuse.
