# M024/S01 Summary

## Implemented

- Added WGPU 29.0.1 headless renderer dependency and direct Naga shader validation dependency.
- Exposed `pyrme.rme_core.render.SpriteAtlas` through an explicit PyO3 `render` submodule.
- Added `HeadlessSpriteRenderer` with offscreen `Rgba8Unorm` render target and tightly packed RGBA readback.
- Added WGPU sprite texture array upload, WGSL textured quad draw pass, nearest sampling, and layer-sorted draw order.
- Exposed `SpriteAtlas.render_headless(width, height)` returning `width`, `height`, `rgba`, `rendered_sprite_count`, and `missing_sprite_count`.

## Verification

- `cargo fmt --all --check`: pass.
- `cargo test -p rme_core`: 114 passed.
- `python -m pytest tests/python/test_sprite_rendering.py tests/python/test_frame_payload.py tests/python/test_wgpu_sprite_renderer.py -q --tb=short`: 7 passed, 2 skipped.
- `npm run preflight`: `Validation: ok`.

## Environment Notes

- Local WSL has `/dev/dxg` but no `/dev/dri`; WGPU adapter init segfaulted before returning a normal error.
- The renderer now reports `WGPU renderer unavailable: no compatible adapter` for WSL hosts without `/dev/dri`.
- This is not a CPU fallback; GPU pixel tests skip only at the explicit unavailable-adapter gate.

## Scope Notes

- No Qt-native WGPU surface was added.
- No live canvas paint integration was added.
- No minimap, SPR decode, lighting, animation, or CPU renderer fallback was added.
