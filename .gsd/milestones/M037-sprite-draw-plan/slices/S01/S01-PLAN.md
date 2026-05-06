# M037/S01 - Sprite Draw Plan Integration

Design source: `docs/superpowers/specs/2026-05-06-m037-sprite-draw-plan-integration-design.md`
Plan source: `docs/superpowers/plans/2026-05-06-m037-sprite-draw-plan-integration.md`

## Scope

- Export existing sprite draw contracts from `pyrme.rendering`.
- Restore canvas host explicit `SpriteDrawPlan` diagnostics.
- Restore live catalog/atlas and provider-derived draw plan refresh.
- Keep diagnostics honest and pixel-free.

## Non-Goals

- no atlas loading
- no SPR decode
- no GPU/QPainter sprite blit
- no minimap
- no Search menu
- no Rust/PyO3 changes

## Tasks

- [x] T01: Restore rendering exports.
- [x] T02: Restore explicit sprite draw plan diagnostics.
- [x] T03: Restore live/provider draw plan refresh.
- [x] T04: Closeout docs, caveman-review, and verification.

## Stop Condition

S01 done when existing sprite draw diagnostics tests pass, focused renderer regressions pass, preflight passes, and final diff has no pixel drawing or asset-loading claim.
