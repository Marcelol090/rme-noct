# M031/S05 Summary - Selection Operations

## Done

- Added selected-item occurrence counting in `EditorModel`.
- Wired Selection Replace Items, Find Item, Remove Item, Find Everything, and Find Unique actions.
- Scoped mutations/searches to `selection_positions`; unselected tiles stay unchanged.
- Kept Find Action/Container/Writeable as exact deferred gaps because `TileState` has no item type flags.

## Verification

- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short` -> 9 passed.
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py tests/python/test_legacy_edit_menu.py tests/python/test_editor_activation_backend.py -q --tb=short` -> 29 passed.
- `rtk python3 -m ruff check pyrme/editor/model.py pyrme/ui/main_window.py tests/python/test_legacy_selection_menu.py` -> passed.
- `rtk git diff --check` -> passed.

## Remaining Evidence Gaps

- Find Action/Container/Writeable on Selection need item type flags or catalog metadata; `TileState` currently stores only item IDs.
