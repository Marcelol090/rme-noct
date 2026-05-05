# S01 Summary - Ground and Wall Brushes

## Done

- Added shared Python editor brush placement data for default ground and wall catalog entries.
- Derived visible PyQt brush catalog rows from the shared editor placement data.
- Made `EditorModel.apply_active_tool_at()` apply selected ground and wall catalog brushes in `drawing` mode.
- Kept item brush, selection, erasing, fill, and move behavior unchanged.
- Kept renderer, minimap, Search menu, XML loading, autoborder mutation, wall alignment recalculation, and PyO3/Rust export out of scope.

## Verification

- `QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_editor_activation_backend.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_commands_m5.py -q --tb=short` -> 74 passed.
- `PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/editor/brushes.py pyrme/editor/model.py pyrme/ui/models/brush_catalog.py tests/python/test_editor_activation_backend.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_canvas_seam_m4.py` -> `All checks passed!`.
- `git diff --check` -> exit 0; Git Windows reported LF/CRLF conversion warnings only.
- `PATH="/home/marcelo/.local/bin:$PATH" rtk npm run preflight --silent` -> `Validation: ok`.
