# M027/S01/T01 Summary

## Done

- Added native `EditorShellState` waypoint list/update/remove bridge.
- Added native house list/update/remove bridge while preserving existing house size on update.
- Added Python bridge/fallback waypoint and house methods.
- Bound `WaypointsDock` to the editor bridge with local fallback behavior preserved.
- Covered `HouseManagerDialog` bridge add/update/remove and native XML sidecar save path.

## Verification

- `npm run preflight --silent` passed.
- `cargo test -p rme_core editor` passed: 10 tests.
- `.venv/bin/python -m pytest tests/python/test_core_bridge.py tests/python/test_waypoints_layers_tier2.py tests/python/test_house_manager_dialog.py tests/python/test_rme_core_editor_shell.py -q --tb=short` passed: 13 tests.
- `.venv/bin/python -m ruff check ... --ignore A002` passed for touched Python files.
- `cargo fmt --check -p rme_core` passed.

## Notes

- Full `ruff check` on `pyrme/core_bridge.py` still reports pre-existing `A002` `id` argument names in town methods; not changed in this slice.
