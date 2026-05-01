# T04 Summary - M029/S01 Brush Engine Alpha

## Scope

- Added Rust brush catalog definitions for ground and wall brush metadata.
- Added catalog validation for reserved names, duplicate names, and duplicate ids.
- Added deterministic placement command resolution.
- Added `MapModel::apply_brush_command` for ground and wall placement.
- Preserved current Python activation behavior.

## Legacy Evidence

- `remeres-map-editor-redux/source/brushes/brush.h`
- `remeres-map-editor-redux/source/brushes/brush.cpp`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush.cpp`
- `remeres-map-editor-redux/source/brushes/wall/wall_brush.cpp`

## Verification

- `cargo test -p rme_core brushes --quiet` with PyO3 Python 3.12 env: 8 passed.
- `cargo test -p rme_core brush_command_tests --quiet` with PyO3 Python 3.12 env: 4 passed.
- `cargo test -p rme_core editor::tests --quiet` with PyO3 Python 3.12 env: 10 passed.
- `cargo test -p rme_core map::tests --quiet` with PyO3 Python 3.12 env: 28 passed.
- `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/python/test_editor_activation_backend.py tests/python/test_rme_core_editor_shell.py -q --tb=short`: 14 passed.
- `npm run preflight`: Validation ok.

## Follow-up

- M030 owns autoborder parsing and neighbor alignment.
- UI tool palette integration remains out of M029/S01.
