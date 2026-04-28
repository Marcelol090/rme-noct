# M018: OTBM XML Serialization Summary

## Status
Complete.

## Result
`EditorShellState.save_otbm()` now writes the binary `.otbm` file and the legacy XML sidecars:

- `<map>-waypoint.xml`
- `<map>-spawn.xml`
- `<map>-house.xml`

## Scope Delivered
- Added `Waypoint`, `Creature`, `Spawn`, and `House` domain records to `MapModel`.
- Added `rme_core::io::xml` string builders for waypoints, spawns, and houses.
- Added sidecar file writing next to the target `.otbm` path.
- Exposed Python bridge helpers for tests and early editor integration.
- Covered XML escaping, legacy tag/attribute names, NPC/monster spawn rows, house metadata, and save-time sidecar creation.
- Matched legacy spawn radius scanning: radius `0` is valid, and creatures outside `[-radius, radius]` are not emitted.

## Legacy Reference
Behavior was matched against `remeres-map-editor-redux/source/io/map_xml_io.cpp`.

## Verification
- RED: `./.venv/bin/python3.12 -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short` failed before implementation because `EditorShellState` lacked `add_waypoint`.
- GREEN: `RUSTFLAGS='-C link-arg=/usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0' cargo test -p rme_core` passed with 66 tests.
- GREEN: `PYO3_PYTHON='./.venv/bin/python3.12' cargo build -p rme_core` passed.
- GREEN: `./.venv/bin/python3.12 -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short` passed with 3 tests.
- GREEN: `./.venv/bin/python3.12 -m pytest tests/python/ -q --tb=short` passed with 270 tests.
- GREEN: `npm run preflight` passed.

## Notes
- No third-party API was added for XML formatting; this slice uses Rust `String` builders and `std::fs::write`.
- XML readback remains future scope.
