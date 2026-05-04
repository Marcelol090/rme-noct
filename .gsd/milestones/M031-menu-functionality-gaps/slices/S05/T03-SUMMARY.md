# T03 Summary - Selection Replace/Remove

- Reused S04 `EditorModel.replace_item_id(..., positions=...)`.
- Reused S04 `EditorModel.remove_item_id(..., positions=...)`.
- Selection actions pass `editor.selection_positions`, so unselected tiles are untouched.

Verification:
- Covered by `test_selection_replace_and_remove_items_mutate_only_selected_tiles`.
