# T01 Summary - File Lifecycle RED

- Added failing File menu tests for New, Open, Save, Save As, Close, Exit, and Recent Files.
- RED command: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py -q --tb=short`
- RED result: 5 failed, 3 passed. Intended failure: `MainWindow.__init__()` did not accept `file_lifecycle_service`.
- Correction RED command: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py -q --tb=short`
- Correction RED result: 8 failed, 4 passed, 7 errors. Intended failures: File service did not receive active `EditorContext`, loaded context was not applied, persistence exceptions crashed actions, and bridge wrappers raised native failures.
