# T01 Summary - Selection RED Tests

- Added failing tests for selected-area replace, remove, item search, all-item summary, unique item summary, and unsupported type filters.

RED evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short` -> 5 failed, 4 passed before implementation.
