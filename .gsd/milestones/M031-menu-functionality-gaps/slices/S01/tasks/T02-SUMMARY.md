# T02 Summary - File Lifecycle Seam

- Added injectable `FileLifecycleService` protocol and Qt default service.
- Tests inject `_FakeFileLifecycleService`, so no modal dialogs open in File lifecycle tests.
- Context7 PyQt6 evidence used: `QFileDialog.getOpenFileName` returns an empty path on cancel; `QSettings.setValue` persists key-value settings; `QMessageBox` supports Save/Discard/Cancel guard decisions.
- Correction: `load_map` and `save_map` now receive the active `EditorContext`; load returns a context to bind, and save receives the active context instead of relying on detached private state.
