# T04 Summary - Preserve missing resource outcomes

## Result

Added regression coverage for honest missing-resource propagation:

- Missing item ids remain in the frame resource list with `MISSING_ITEM`.
- Missing sprite payloads remain in the frame resource list with `MISSING_SPRITE`.
- No production code change was needed; the builder already preserves resolver results without filtering by availability.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py -q --tb=short` - passed, 15 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/rendering/frame_sprite_resources.py tests/python/test_frame_sprite_resources.py pyrme/rendering/__init__.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short` - passed, 22 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `tests/python/test_frame_sprite_resources.py`
