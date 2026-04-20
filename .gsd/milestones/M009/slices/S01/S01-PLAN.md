# S01 — CANVAS-100-SPRITE-DRAW-DIAGNOSTICS

## Summary

Expose pure sprite draw plan diagnostics on the canvas host without changing the pixel paint path.

## Must-Haves

- Add a canvas protocol seam for accepting `SpriteDrawPlan` values.
- Initialize deterministic empty sprite draw diagnostics.
- Report sprite draw command counts in `diagnostic_text()`.
- Report unresolved sprite ids deterministically, using `none` when empty.
- Keep `PlaceholderCanvasWidget` and `RendererHostCanvasWidget` behavior aligned.
- Do not add live catalog/atlas generation, GL uploads, sprite painting, screenshots, lighting, or `wgpu` work.

## Tasks

- [x] T01 — Add failing canvas-host sprite draw diagnostic tests.
- [x] T02 — Add sprite draw plan protocol and type guard.
- [x] T03 — Store and report sprite draw plan command/unresolved diagnostics.
- [x] T04 — Verify, summarize, and decide the next renderer slice.

## Verification

```bash
python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py -q -s --tb=short
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
    '-s',
    '--tb=short',
]))
PY
python3 -m ruff check pyrme/rendering pyrme/ui/canvas_host.py tests/python/test_canvas_sprite_draw_diagnostics.py
git diff --check
```

## Out Of Scope

- Live sprite-frame generation from the active canvas frame.
- Real atlas texture loading.
- Sprite pixel extraction.
- Renderer host sprite painting.
- Screenshot capture.
- Lighting.
- `QOpenGLWidget` validity under offscreen CI.
