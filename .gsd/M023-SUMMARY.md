# M023: Sprite Rendering Parity — SUMMARY

## Work Completed
- Added CPU-side sprite staging in Rust through PyO3 `render.SpriteAtlas`.
- Added WGSL sprite shader validation with `naga = "29.0.1"` and a tracked root `Cargo.lock` for `--locked` checks.
- Wired `RendererHostCanvasWidget.paintGL()` to dispatch resolved sprite payloads through an injectable render dispatcher.
- Preserved existing sprite draw-plan diagnostics, selected/invalid tile overlays, and readable diagnostic text.
- Kept the real WGPU renderer, texture upload, and GPU draw pass deferred to M024.

## Validation
- `npm run preflight --silent`
- `cargo fmt --manifest-path crates/rme_core/Cargo.toml -- --check`
- `cargo clippy --manifest-path crates/rme_core/Cargo.toml --locked -- -D warnings`
- `python3.12 -m ruff check ...`
- `python3.12 -m mypy pyrme/rendering pyrme/ui/canvas_host.py --ignore-missing-imports`
- `cargo test --manifest-path crates/rme_core/Cargo.toml --locked --quiet` — 22 passed
- `QT_QPA_PLATFORM=offscreen python3.12 -m pytest tests/python/ -q --tb=short` — 432 passed

## Next Actions
- Use M024 to plan and implement real WGPU texture upload and sprite draw passes from the staged payload seam.
