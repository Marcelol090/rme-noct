# T01 Summary - Lock resolver result contract

## Result

Added the first sprite resolver contract surface:

- `SpriteLookupStatus` exposes `resolved`, `missing_item`, and `missing_sprite` outcomes.
- `SpriteResourceResult` is immutable and carries item id, optional sprite id, optional pixel payload, status, availability, and reason text.
- `pyrme.rendering` exports the new contract types for later frame-resource integration.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py -q --tb=short` - passed, 4 tests.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py tests/python/test_rust_io.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short` - passed, 14 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/rendering/sprite_resolver.py`
- `pyrme/rendering/__init__.py`
- `tests/python/test_sprite_resolver.py`
