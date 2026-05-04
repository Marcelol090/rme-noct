# T01 Summary - Transform Tests

- Added failing tests for `EditorModel` item replacement/removal history.
- Added failing tests for injected Replace Items and Remove Items by ID UI seams.
- Added failing tests for Clear Modified State and exact unsupported-transform evidence.

RED evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short` -> 4 failed, 7 passed before implementation.
