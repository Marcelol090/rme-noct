# T01 Summary: Write OTBM XML Sidecars

## Status
Complete.

## Work
- Added the missing sidecar data model to `MapModel`.
- Added XML builders for waypoints, spawns, and houses.
- Wired `EditorShellState.save_otbm()` to write sidecar XML files beside the `.otbm`.
- Added Python native bridge coverage for exact XML content.

## TDD Evidence
- RED: `EditorShellState` had no `add_waypoint`, so the new Python integration test failed before implementation.
- GREEN: Rust core tests passed after implementing domain records and XML builders.
- GREEN: Native Python bridge test passed after rebuilding `pyrme.rme_core`.

## Verification Commands
- `RUSTFLAGS='-C link-arg=/usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0' cargo test -p rme_core`
- `PYO3_PYTHON='./.venv/bin/python3.12' cargo build -p rme_core`
- `./.venv/bin/python3.12 -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short`
- `./.venv/bin/python3.12 -m pytest tests/python/ -q --tb=short`
- `npm run preflight`

## Result
M018/S01 stop condition satisfied.
