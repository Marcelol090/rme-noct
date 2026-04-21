# T02 Summary - Resolve ground sprite resources from frame plan

## Result

Added pure frame-plan ground resource collection:

- `build_frame_sprite_resources()` walks `RenderFramePlan.tile_commands` in order.
- Non-null `ground_item_id` values resolve through `SpriteResourceResolver`.
- Ground resource records use `stack_layer=0`.
- Empty-ground commands are skipped for now; stack item resources remain T03 scope.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short` - passed, 3 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/rendering/frame_sprite_resources.py tests/python/test_frame_sprite_resources.py pyrme/rendering/__init__.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short` - passed, 20 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/rendering/frame_sprite_resources.py`
- `pyrme/rendering/__init__.py`
- `tests/python/test_frame_sprite_resources.py`
