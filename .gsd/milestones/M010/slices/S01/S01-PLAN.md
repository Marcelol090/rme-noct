# S01 - CANVAS-110-LIVE-SPRITE-DRAW-PLAN

## Summary

Connect live canvas frame data to the existing sprite draw command planner through fixture catalog and atlas inputs.

## Must-Haves

- Canvas hosts expose a `set_sprite_draw_inputs(catalog, atlas)` seam.
- Live inputs regenerate `SpriteDrawPlan` from the current `CanvasFrame`.
- Frame changes refresh sprite draw command diagnostics.
- Explicit `set_sprite_draw_plan()` remains supported as a manual override.
- The paint path stays diagnostic-only.

## Tasks

- [x] T01 - Add failing live sprite draw diagnostics tests.
- [x] T02 - Add live sprite draw input storage and generation.
- [x] T03 - Preserve explicit draw-plan override behavior.
- [x] T04 - Verify and summarize the slice.

## Verification

```bash
python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py -q --tb=short
python3 - <<'PY'
import enum
import pytest
if not hasattr(enum, 'StrEnum'):
    class StrEnum(str, enum.Enum):
        pass
    enum.StrEnum = StrEnum
raise SystemExit(pytest.main([
    'tests/python/test_canvas_sprite_draw_diagnostics.py',
    'tests/python/test_canvas_seam_m4.py',
    'tests/python/test_renderer_frame_plan_integration.py',
    'tests/python/test_sprite_draw_commands.py',
    'tests/python/test_sprite_catalog_adapter.py',
    'tests/python/test_sprite_frame.py',
    'tests/python/test_render_frame_plan.py',
    'tests/python/test_diagnostic_tile_primitives.py',
    '-q',
    '--tb=short',
]))
PY
python3 -m ruff check pyrme/ui/canvas_host.py tests/python/test_canvas_sprite_draw_diagnostics.py
git diff --check
```

## Out Of Scope

- Real DAT/SPR file loading.
- Real atlas texture construction.
- OpenGL sprite drawing.
- Screenshot capture.
- Lighting.
- `wgpu`.
