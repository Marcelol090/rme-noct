# T02 Summary - Selection Search Helper

- Added `EditorModel.selection_item_counts()`.
- Counts ground and stack item occurrences only for selected tiles.

GREEN evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py::test_editor_model_counts_selected_item_occurrences -q --tb=short` -> 1 passed.
