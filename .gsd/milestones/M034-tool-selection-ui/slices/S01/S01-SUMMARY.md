# S01 Summary - Tool Selection UI

## Done

- Converted Drawing Tools toolbar into real exclusive Select/Draw/Erase/Fill/Move mode actions.
- Kept Tool Options label synchronized with active editor mode.
- Kept canvas activation synchronized through `set_editor_mode()`.
- Preserved Fill/Move backend no-op behavior.
- Kept renderer, minimap, Search menu, PyO3, and new map mutation out of scope.

## Verification

- `QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py::test_main_window_drawing_toolbar_exposes_all_editor_modes tests/python/test_main_window_commands_m5.py::test_main_window_drawing_toolbar_orders_tool_modes -q --tb=short` -> 6 passed.
- `QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_seam_m4.py::test_main_window_extended_tool_modes_update_canvas_activation -q --tb=short` -> 1 passed.
- `QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_new_view.py tests/python/test_editor_activation_backend.py -q --tb=short` -> 67 passed.
- `PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/main_window.py tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py` -> `All checks passed!`.
- `git diff --check` with Windows Git -> exit 0; CRLF warnings only.
- `PATH="/home/marcelo/.local/bin:$PATH" rtk npm run preflight --silent` -> `Validation: ok`.
