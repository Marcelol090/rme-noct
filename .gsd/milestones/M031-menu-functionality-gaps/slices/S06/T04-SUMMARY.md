# T04 Summary - Dialog Regression Check

- Existing Map Properties seam still opens injected dialog.
- Existing Town Manager action still opens the town manager dialog.
- Existing House Manager action still opens the house manager dialog.

Verification:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short` -> 7 passed.
