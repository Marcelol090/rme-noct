# T03 Summary - Resolve stack item sprite resources in order

## Result

Extended frame sprite resource collection to include stack items:

- Ground item records stay first for each tile with `stack_layer=0`.
- `RenderTileCommand.item_ids` append after ground in tuple order.
- Stack item records use `stack_layer=1..N`.
- Stack-only tiles still produce resource records.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short` - passed, 4 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/rendering/frame_sprite_resources.py tests/python/test_frame_sprite_resources.py pyrme/rendering/__init__.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short` - passed, 21 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/rendering/frame_sprite_resources.py`
- `tests/python/test_frame_sprite_resources.py`
