# M024 WGPU Sprite Renderer Context

## Goal

Turn M023 staged sprite payloads into real WGPU-rendered RGBA output without changing Qt canvas painting.

## Inputs

- M023 staged `render.SpriteAtlas` frame commands.
- `crates/rme_core/src/render/sprite.wgsl`.
- WGPU 29.0.1 offscreen texture and readback APIs.

## Scope

- Rust headless WGPU renderer.
- PyO3 `render.SpriteAtlas.render_headless(width, height)` bridge.
- Focused Rust and Python tests.

## Stop Conditions

- Stop before implementation while PR #89 remains unmerged unless user approves stacking.
- Stop on any caveman-review gap before commit or PR.
- Stop if WGPU API shape differs from Context7 v29.0.1 docs and refresh Context7 before editing code.

## Out Of Scope

- Qt-native WGPU surface.
- Live canvas paint integration.
- Minimap.
- SPR decode.
- CPU fallback.
