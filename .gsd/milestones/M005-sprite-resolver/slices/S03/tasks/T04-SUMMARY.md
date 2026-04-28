# T04 Summary - Collect frame sprite diagnostics during canvas sync

## Result

Renderer host diagnostics now reflect visible frame sprite resources:

- Canvas host owns an explicit `SpriteResourceResolver` seam.
- Default resolver is empty, so visible item ids report honest missing-item diagnostics until DAT/SPR sources are wired.
- Injected resolver can report resolved resources in integration tests.
- Diagnostics are recomputed during canvas frame sync.
- Tile primitive drawing remains unchanged.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_renderer_frame_plan_integration.py -q --tb=short` - passed, 4 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/ui/canvas_host.py tests/python/test_renderer_frame_plan_integration.py pyrme/rendering/frame_sprite_resources.py pyrme/rendering/sprite_resource_diagnostics.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_renderer_frame_plan_integration.py tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resource_diagnostics.py tests/python/test_canvas_seam_m4.py -q --tb=short` - passed, 36 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/ui/canvas_host.py`
- `tests/python/test_renderer_frame_plan_integration.py`
