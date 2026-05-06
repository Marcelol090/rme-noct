# M037 Sprite Draw Plan Integration Design

## Source

Current `origin/main` has sprite draw planning tests and rendering-layer primitives, but `pyrme/ui/canvas_host.py` no longer exposes the canvas sprite draw plan seam those tests require.

## Problem

`tests/python/test_canvas_sprite_draw_diagnostics.py` fails during collection because `pyrme.rendering` does not export `SpriteDrawAssetInputs`. After that export is restored, the same test file expects canvas hosts to support:

- `set_sprite_draw_plan(plan)`
- `set_sprite_draw_inputs(catalog, atlas)`
- `set_sprite_asset_provider(provider)`
- `sprite_draw_command_count()`
- `unresolved_sprite_ids()`
- sprite draw diagnostics in `diagnostic_text()`

## Goal

Reconnect existing `CanvasFrame -> RenderFramePlan -> SpriteFrame -> SpriteDrawPlan` diagnostics into `PlaceholderCanvasWidget` and `RendererHostCanvasWidget` without painting sprite pixels.

## Non-Goals

- no atlas loading
- no SPR decoding
- no texture upload
- no real QPainter/GPU sprite blit
- no minimap
- no Search menu
- no Rust/PyO3 change

## Acceptance

- Existing sprite draw diagnostics tests collect and pass.
- Existing renderer frame/resource diagnostics stay green.
- Empty/default canvas reports zero sprite draw commands.
- Live frame changes refresh live/provider-derived sprite draw plans.
- Explicit `set_sprite_draw_plan()` remains override and disables live/provider regeneration.
- Provider failures clear stale commands and keep frame diagnostics honest.

