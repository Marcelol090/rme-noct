# T01 Summary - Edit History Clipboard RED

- Added RED coverage for `EditorModel` undo/redo after a tile edit.
- Added RED coverage for copy/cut/paste of selected in-memory map tiles.
- Added RED shell coverage for Edit action enablement and status messages.
- RED command: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short`
- RED result: 3 failed, 4 passed. Intended failures: missing `EditorModel`
  history/clipboard methods and Edit actions starting enabled/unwired.
