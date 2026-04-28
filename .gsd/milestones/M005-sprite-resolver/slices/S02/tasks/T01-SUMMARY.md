# T01 Summary - Define frame sprite resource records

## Result

Added the first frame-resource record contract:

- `FrameSpriteResource` is immutable and carries tile position, item id, stack layer, and `SpriteResourceResult`.
- `pyrme.rendering` exports `FrameSpriteResource` for upcoming frame-plan resource collection.
- Renderer host drawing remains unchanged.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short` - passed, 2 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/rendering/frame_sprite_resources.py tests/python/test_frame_sprite_resources.py pyrme/rendering/__init__.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short` - passed, 19 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/rendering/frame_sprite_resources.py`
- `pyrme/rendering/__init__.py`
- `tests/python/test_frame_sprite_resources.py`
