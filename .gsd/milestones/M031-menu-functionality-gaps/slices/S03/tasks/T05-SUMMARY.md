# T05 Summary - S03 Closeout

- S03 implements minimal in-memory Undo/Redo/Cut/Copy/Paste for `MapModel`.
- History covers drawing, erasing, cut, and paste tile changes.
- Clipboard copies selected existing tiles and pastes relative to the current cursor.
- Verification:
  - `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short` -> 7 passed.
  - `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_editor_activation_backend.py tests/python/test_canvas_seam_m4.py tests/python/test_legacy_edit_menu.py -q --tb=short` -> 38 passed.
  - `python3 -m ruff check pyrme/editor/model.py pyrme/ui/main_window.py tests/python/test_legacy_edit_menu.py` -> All checks passed.
  - `git diff --check` -> clean.
