# T03 Summary - In-Memory Clipboard

- Added selection-based copy buffer to `EditorModel`.
- `copy_selection` stores selected existing tiles with relative offsets.
- `cut_selection` copies then removes selected tiles as an undoable edit.
- `paste_clipboard_at` writes buffered tiles at the current map position.
