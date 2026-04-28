# T01 Summary - Define pure sprite resource diagnostics summary

## Result

Added pure sprite resource diagnostic counts:

- `SpriteResourceDiagnostics` is immutable and stores total, resolved, missing-item, and missing-sprite counts.
- `build_sprite_resource_diagnostics()` counts outcomes from `FrameSpriteResource` records.
- `pyrme.rendering` exports the diagnostics contract for upcoming canvas host wiring.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py -q --tb=short` - passed, 2 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/rendering/sprite_resource_diagnostics.py tests/python/test_sprite_resource_diagnostics.py pyrme/rendering/__init__.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py -q --tb=short` - passed, 17 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/rendering/sprite_resource_diagnostics.py`
- `pyrme/rendering/__init__.py`
- `tests/python/test_sprite_resource_diagnostics.py`
