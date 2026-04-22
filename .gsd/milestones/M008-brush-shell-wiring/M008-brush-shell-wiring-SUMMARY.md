# M008 Summary - Brush shell wiring

## Result

M008 closed the pending shell command wiring as a narrow vertical slice:

- local `FindBrushDialog` search results now cover palette and item-backed brush selection
- `MainWindow` routes `Jump to Brush`, `Jump to Item`, palette switching, and brush mode toolbar state into `EditorSessionState` / `EditorModel`
- zoom, screenshot-safe-gap behavior, and new-view shell regressions remain covered
- WSL preflight now uses a repo-local Python launcher and the platform-default npm script shell instead of hardcoded Windows `py -3` / `cmd.exe`

## Verification

- `./.venv/bin/python3.12 -m ruff check pyrme/ui/main_window.py pyrme/ui/dialogs/find_brush.py pyrme/ui/dialogs/__init__.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_find_brush_tier2.py` - passed.
- `./.venv/bin/python3.12 -m mypy pyrme/ui/main_window.py pyrme/ui/dialogs/find_brush.py pyrme/ui/dialogs/__init__.py --ignore-missing-imports` - passed.
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_find_brush_tier2.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py` - passed, 17 tests.
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_editor_activation_backend.py tests/python/test_main_window_new_view.py tests/python/test_canvas_seam_m4.py` - passed, 36 tests.
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_find_brush_tier2.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_editor_activation_backend.py tests/python/test_main_window_new_view.py tests/python/test_canvas_seam_m4.py` - passed, 53 tests.
- `./.venv/bin/python3.12 -m pytest tests/python/ -q -s --tb=short` - passed, 266 tests.
- `npm run preflight --silent` - passed.
- `env QT_QPA_PLATFORM=offscreen ./.venv/bin/python3.12 -m pyrme` - launch smoke reached app startup, then timed out in the event loop with the known `QOpenGLWidget is not supported on this platform.` offscreen limitation.

## Follow-up

- The repo still needs scoped staging and diff review before any commit because the surrounding worktree remains mixed.
- `pyrme --dev` is not a supported CLI flag; `pyrme/ui/AGENTS.md` now points manual smoke at `python3 -m pyrme`.
