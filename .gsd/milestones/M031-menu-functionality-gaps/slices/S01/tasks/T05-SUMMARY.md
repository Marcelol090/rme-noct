# T05 Summary - S01 Closeout

- File New/Open/Save/Save As/Close/Exit actions are wired away from `_show_unavailable`.
- File lifecycle seam now receives/applies active `EditorContext`; failed/raised load/save does not mutate path, dirty state, or recent files.
- Recent files are settings-backed, deduped, capped, reordered on use, and routed through the same open path.
- Core bridge load/save wrappers return failure instead of surfacing native persistence exceptions into UI actions.
- Verification:
  - `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py -q --tb=short` -> 12 passed.
  - `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_welcome_dialog_integration.py -q --tb=short` -> 4 passed.
  - `python3 -m ruff check pyrme/ui/main_window.py pyrme/ui/editor_context.py pyrme/core_bridge.py tests/python/test_legacy_file_menu.py` -> All checks passed.
- Review:
  - Spec compliance PASS.
  - Code quality PASS.
