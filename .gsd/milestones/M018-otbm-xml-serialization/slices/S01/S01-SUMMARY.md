# M018 S01: XML Writing Implementation Summary

## Status
Complete.

## Stop Condition
Met: Python `save_otbm` creates `.otbm`, `<map>-house.xml`, `<map>-spawn.xml`, and `<map>-waypoint.xml` sidecars with legacy RME tag and attribute shapes.

## Changes
- `crates/rme_core/src/map.rs`: added waypoints, spawns, creatures, and houses to `MapModel`.
- `crates/rme_core/src/io/xml.rs`: added legacy XML string builders and sidecar path writing.
- `crates/rme_core/src/io/xml.rs`: kept spawn creature emission inside the legacy radius scan window.
- `crates/rme_core/src/io/mod.rs`: exported the XML module.
- `crates/rme_core/src/editor.rs`: exposed minimal Python bridge mutators and wrote XML sidecars after OTBM save.
- `tests/python/test_rme_core_editor_shell.py`: added native bridge integration coverage for sidecar output.

## Verification
- `RUSTFLAGS='-C link-arg=/usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0' cargo test -p rme_core`
- `PYO3_PYTHON='./.venv/bin/python3.12' cargo build -p rme_core`
- `./.venv/bin/python3.12 -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short`
- `./.venv/bin/python3.12 -m pytest tests/python/ -q --tb=short`
- `npm run preflight`

## Follow-up
XML loading and UI/domain workflows that populate these collections are intentionally outside this slice.
