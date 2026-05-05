# T04 Summary

Added RED tests for editor view tab object name, focus QSS, and `activeEditorView` property transitions.

Evidence:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_main_window_new_view.py::test_editor_view_tabs_have_focus_object_name_and_qss tests/python/test_main_window_new_view.py::test_active_editor_view_property_tracks_current_tab -q --tb=short`
- RED failed because `_view_tabs` object name/style and `activeEditorView` properties were missing.
