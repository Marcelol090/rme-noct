# T02 Summary - Add diagnostic summary text contract

## Result

Added stable summary text for sprite resource diagnostics:

- Empty resource sets report `Sprite Resources: 0 total (none requested)`.
- Non-empty resource sets report total, resolved, missing-item, and missing-sprite counts.
- Summary remains pure and independent of Qt.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py -q --tb=short` - passed, 5 tests.
- `.\.venv\Scripts\python.exe -m ruff check pyrme/rendering/sprite_resource_diagnostics.py tests/python/test_sprite_resource_diagnostics.py pyrme/rendering/__init__.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py -q --tb=short` - passed, 20 tests.
- `npm run preflight --silent` - passed.
- Superpowers progress score - green, `Progressing well`.

## Files

- `pyrme/rendering/sprite_resource_diagnostics.py`
- `tests/python/test_sprite_resource_diagnostics.py`
