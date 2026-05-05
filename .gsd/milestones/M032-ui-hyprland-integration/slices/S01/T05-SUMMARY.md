# T05 Summary

Editor view tabs now use focus QSS and canvas widgets receive refreshed `activeEditorView` state after setup, new view creation, and tab changes.

Evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_main_window_new_view.py::test_editor_view_tabs_have_focus_object_name_and_qss tests/python/test_main_window_new_view.py::test_active_editor_view_property_tracks_current_tab -q --tb=short`
- Result: 2 passed.
