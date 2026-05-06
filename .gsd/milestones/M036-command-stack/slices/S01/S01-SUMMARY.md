# M036/S01 Summary - Command Stack Bridge

## Done

- Added Rust `CommandStack` for reversible tile edit command batches.
- Added command-history coordinates that preserve Python map bounds up to `65535`.
- Exposed command history through native `EditorShellState`.
- Mirrored command history in the Python fallback bridge.
- Routed `EditorModel` Undo/Redo through bridge-backed command history.
- Removed Python `_undo_stack` and `_redo_stack` ownership from `EditorModel`.
- Preserved current Edit menu behavior for Draw, Erase, Cut, Paste, Replace Items, Remove Items, and Borderize.

## Verification

- `PATH="$HOME/.local/bin:$PATH" PYO3_PYTHON="$PY312" LD_LIBRARY_PATH="$LIBDIR:${LD_LIBRARY_PATH:-}" RUSTFLAGS="-L native=$LIBDIR" rtk cargo test -p rme_core command_stack` -> `3 passed, 99 filtered out`
- `PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py tests/python/test_rme_core_editor_shell.py -q --tb=short` -> `21 passed`
- `PATH="$HOME/.local/bin:$PATH" rtk ruff check pyrme/core_bridge.py pyrme/editor/command_history.py pyrme/editor/model.py pyrme/editor/__init__.py tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py tests/python/test_rme_core_editor_shell.py` -> `No issues found`
- `git diff --check` -> exit 0
- `PATH="$HOME/.local/bin:$PATH" rtk npm run preflight --silent` -> `Validation: ok`

## Notes

- WSL default `python3` is 3.10 and lacks the needed `libpython3.10`; Rust verification used the uv Python 3.12 interpreter for PyO3 linking.
- The initial Rust RED compiled as a rustc ICE because `CommandStack` was intentionally missing. Implementation removed the ICE and made the intended command-stack tests pass.
- Caveman-review caught a coordinate clamp risk before commit; Rust command history now uses its own `CommandPosition` instead of map-storage `MapPosition`.

## Out of Scope

- Clipboard format redesign.
- File lifecycle command journal.
- Renderer, minimap, Search menu.
- Full Rust map ownership migration.
