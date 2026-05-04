# T02 Summary - Pure EditorModel Operations

- Added `EditorModel.replace_item_id(old_item_id, new_item_id, positions=None)`.
- Added `EditorModel.remove_item_id(item_id, positions=None)`.
- Added `EditorModel.clear_modified_state()`.
- Replace/remove operations use existing `TileEditChange` history and skip no-op changes.

GREEN evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short` -> 11 passed.
