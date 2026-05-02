# T04 Summary - Recent Files

- Stored `recent_files_menu` on `MainWindow`.
- Recent files load from `QSettings` key `file/recent_files`, dedupe, cap at 10, and persist after successful open/save.
- Recent menu actions trigger the same `_open_map_file` path as File Open and reorder the selected path to the top.
- Correction: failed or raised Open/Save does not mutate recent files.
