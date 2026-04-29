# M023: Sprite Rendering Parity — PLAN

## Milestone
**M023 — Sprite Rendering Parity**
Branch: `gsd/M023/S01`
Worktree: `.worktrees/m023-sprite-parity`

## Design System Reference
Tokens from `DESIGN.md` (ui-ux-pro-max output).

### UI/WGPU Tokens
- Canvas Background: Void Black `#0A0A12`
- Grid Lines: Amethyst Grid `rgba(124, 92, 252, 0.15)`
- Selection Overlay: `rgba(255, 255, 255, 0.2)`
- Invalid Tile: `rgba(224, 92, 92, 0.4)`
- Diagnostics Text: JetBrains Mono 10px, Moonstone White `#E8E6F0`, Drop shadow `rgba(0,0,0,0.8)`
- Interaction: cursor-pointer on tile selection, >4.5:1 contrast, reduced-motion.

---

## Tasks

### Phase 1: CPU-side sprite staging and shader validation (Rust)
#### T01 — CPU-side sprite staging contract (5 min)
- [x] RED: test mapping decoded sprite raw pixels into a CPU-side staging record.
- [x] GREEN: expose the PyO3 `render.SpriteAtlas` seam from `crates/rme_core/src/lib.rs`.
- [x] Scope Note: This milestone records CPU-side sprite staging only; the real WGPU renderer is deferred to M024.

#### T02 — WGPU Shader for Sprites (4 min)
- [x] RED: test WGSL validation with offset and layer uniforms.
- [x] GREEN: add WGSL validation through `naga = "29.0.1"` in `crates/rme_core/Cargo.toml` and `Cargo.lock`.
- [x] UI-UX Note: Keep Void Black `#0A0A12` documented for the future M024 clear color.

### Phase 2: Python / Rust Bridge
#### T03 — Frame Payload Serialization (5 min)
- [x] RED: test Python `SpriteResourceResolver` sending items array to Rust Core.
- [x] GREEN: implement PyO3 `render.SpriteAtlas` payload construction without drawing.

#### T04 — Qt dispatch seam (5 min)
- [x] RED: test `QOpenGLWidget` requests repaint and dispatches frame payload data to `rme_core`.
- [x] GREEN: implement the Qt dispatch seam that prepares sprite payloads for the Rust bridge.
- [x] UI-UX Note: Preserve Amethyst Grid `rgba(124, 92, 252, 0.15)` as an overlay contract for M024.

### Phase 3: Diagnostics & Selection Polish
#### T05 — Diagnostic Overlay (4 min)
- [x] RED: test diagnostic text (FPS, coordinates) renders.
- [x] GREEN: preserve the existing diagnostics overlay while reporting staged sprite payload state.
- [x] UI-UX Note: JetBrains Mono 10px, Moonstone White `#E8E6F0`, shadow `rgba(0,0,0,0.8)` (>4.5:1 contrast).

#### T06 — Invalid & Selected Tiles (3 min)
- [x] RED: test selected tile applies overlay.
- [x] GREEN: carry invalid and selected tile overlay intent through the staged frame payload.
- [x] UI-UX Note: Selection Overlay `rgba(255, 255, 255, 0.2)`, Invalid `rgba(224, 92, 92, 0.4)`.

---
## Stop Condition
M023 stops at CPU-side sprite staging, PyO3 `render.SpriteAtlas`, WGSL validation, and the Qt dispatch seam. The real WGPU renderer is deferred to M024/future work. Diagnostics remain readable and all scoped tests pass.
