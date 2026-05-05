# T01 Summary - RED Map Tests

- Added tests for exact cleanup invalid tile/zone deferred messages.
- Added test for Map Statistics dialog factory seam receiving current editor map statistics.

RED evidence:
- `QT_QPA_PLATFORM=offscreen timeout 30s rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short` -> baseline timed out after 2 tests.
- After RED tests, target failed with missing exact cleanup messages and missing `map_statistics_dialog_factory`.
