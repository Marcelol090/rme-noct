# S01 Summary

M032/S01 added tokenized Noct focus state for welcome lists and editor view canvases.

Changed:
- Added `pyrme/ui/styles/focus.py`.
- Exported focus tokens from `pyrme/ui/styles`.
- Added focused-list border rules to `item_view_qss()`.
- Added stable welcome list object names.
- Added `editor_view_tabs` QSS and `activeEditorView` state refresh in `MainWindow`.

Verification:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py -q --tb=short` -> 39 passed.
- `rtk python3 -m ruff check pyrme/ui/styles/focus.py pyrme/ui/styles/__init__.py pyrme/ui/styles/contracts.py pyrme/ui/dialogs/welcome_dialog.py pyrme/ui/main_window.py tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py` -> passed.
- `rtk git diff --check` -> passed.
