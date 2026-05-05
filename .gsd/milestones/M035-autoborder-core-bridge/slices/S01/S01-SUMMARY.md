# M035/S01 Summary - Autoborder Core Bridge

## Result

- Added `EditorShellState.resolve_autoborder_items` as a PyO3 bridge over the
  existing M030 `resolve_autoborder_plan`.
- Added `EditorShellCoreBridge.resolve_autoborder_items` with deterministic
  fallback behavior for non-native test environments.
- Added undoable `EditorModel.append_border_items` mutation with duplicate
  suppression.
- Wired `Edit -> Border Options -> Borderize Selection/Map` to the bridge and
  kept Randomize actions explicitly deferred.
- Rebased the stale autoborder design/plan docs against live M030 state.

## Verification

- `rtk npm run preflight --silent` -> pass, `Validation: ok`.
- `rtk cargo fmt --check` -> pass.
- `rtk test .venv/bin/python -m ruff check pyrme/core_bridge.py pyrme/editor/model.py pyrme/ui/main_window.py tests/python/test_core_bridge.py tests/python/test_rme_core_editor_shell.py tests/python/test_legacy_edit_menu.py` -> pass.
- `rtk test .venv/bin/python -m pytest tests/python/test_rme_core_editor_shell.py::test_native_rme_core_exposes_autoborder_plan_bridge tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py -q --tb=short` -> 18 passed.
- `PYO3_PYTHON=$PWD/.venv/bin/python rtk cargo test -p rme_core autoborder` -> 9 passed.
- `PYO3_PYTHON=$PWD/.venv/bin/python rtk cargo test -p rme_core editor` -> 11 passed.

## Known External Blocker

Full `tests/python/` collection still fails outside this slice on missing sprite
rendering exports and missing `yaml` dependency:

- `SpriteDrawAssetInputs`
- `ClientSpriteAssetBundle`
- `SpriteAtlas`
- `pyrme.rme_core.render`
- `yaml`

## Review

`caveman-review`: clean after narrowing supported brush lookup to `look_id` only;
ground variants remain an explicit future catalog gap.
