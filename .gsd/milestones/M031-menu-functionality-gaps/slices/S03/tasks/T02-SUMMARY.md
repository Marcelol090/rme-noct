# T02 Summary - EditorModel History

- Added `TileEditChange` records for before/after tile mutation.
- Drawing and erasing now record undoable tile changes.
- Added `can_undo`, `can_redo`, `undo`, and `redo` to `EditorModel`.
- Redo stack clears on new recorded edits.
