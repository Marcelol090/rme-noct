# S01 Summary - Sprite Draw Plan Integration

## Done

- Restored sprite draw asset and command exports from `pyrme.rendering`.
- Restored explicit `SpriteDrawPlan` diagnostics on canvas hosts.
- Restored live catalog/atlas and asset-provider sprite draw plan refresh through current frame sync.
- Kept renderer honest: no sprite pixels, no atlas loading, no minimap, no Search menu, no Rust/PyO3 change.

## Verification

- `QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_sprite_draw_commands.py tests/python/test_sprite_asset_provider.py tests/python/test_client_asset_discovery.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_frame_sprite_resources.py -q --tb=short` - 44 passed.
- `PATH="$HOME/.local/bin:$PATH" rtk python3 -m ruff check pyrme/rendering/__init__.py pyrme/ui/canvas_host.py tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_client_asset_discovery.py` - All checks passed.
- `git diff --check` - exit 0, CRLF warnings only.
- `PATH="$HOME/.local/bin:$PATH" rtk npm run preflight --silent` - Validation: ok.
