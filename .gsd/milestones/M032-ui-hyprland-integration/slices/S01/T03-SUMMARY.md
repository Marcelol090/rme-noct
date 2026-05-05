# T03 Summary

Welcome recent-map and client-list widgets now have stable object names and focused-list border rules through `item_view_qss()`.

Evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_welcome_dialog.py::TestWelcomeFocusStyling -q --tb=short`
- RED failed before object names/QSS.
- GREEN result: 2 passed.
