# M024/S01 Headless WGPU Sprite Renderer

## Goal

Render staged sprite payloads through a real headless WGPU path and expose RGBA output to Python.

## Plan

Detailed implementation plan: `docs/superpowers/plans/2026-05-06-m024-wgpu-sprite-renderer.md`

Design: `docs/superpowers/specs/2026-05-06-m024-wgpu-sprite-renderer-design.md`

## Tasks

- [ ] T01: Dependency and Python render submodule gate.
- [ ] T02: Headless renderer contract.
- [ ] T03: WGPU device and empty offscreen readback.
- [ ] T04: Textured sprite draw pass.
- [ ] T05: Layer ordering.
- [ ] T06: PyO3 headless bridge.
- [ ] T07: Verification and closeout.

## Stop Conditions

- Do not implement before PR #89 merges unless user explicitly approves stacking.
- Do not add CPU fallback.
- Do not change Qt canvas painting in this slice.
- Do not commit before clean caveman-review.
