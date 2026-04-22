# S01 Summary - BRUSH-20-SHELL-COMMAND-WIRING

## Result

S01 materialized the pending shell command wiring that sat on top of M007:

- `FindBrushDialog` now provides a local palette/item brush search seam
- `MainWindow` routes jump actions, palette switching, and brush mode toolbar changes into `EditorSessionState` / `EditorModel`
- WSL preflight now launches through the repo-local Python helper and no longer depends on a repo-forced Windows npm script shell

## Verification

- `./.venv/bin/python3.12 -m ruff check pyrme/ui/main_window.py pyrme/ui/dialogs/find_brush.py pyrme/ui/dialogs/__init__.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_find_brush_tier2.py` - passed.
- `./.venv/bin/python3.12 -m mypy pyrme/ui/main_window.py pyrme/ui/dialogs/find_brush.py pyrme/ui/dialogs/__init__.py --ignore-missing-imports` - passed.
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_find_brush_tier2.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py` - passed, 17 tests.
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_editor_activation_backend.py tests/python/test_main_window_new_view.py tests/python/test_canvas_seam_m4.py` - passed, 36 tests.
- `./.venv/bin/python3.12 -m pytest tests/python/ -q -s --tb=short` - passed, 266 tests.
- `npm run preflight --silent` - passed.
- `env QT_QPA_PLATFORM=offscreen ./.venv/bin/python3.12 -m pyrme` - startup smoke reached the event loop, then timed out under the known offscreen `QOpenGLWidget` limitation.
- Qt signal/slot wiring was checked against official Qt 6 docs after Context7 MCP returned an invalid OAuth token in this session: `QAction::triggered(bool checked = false)`, `QLineEdit::textChanged(const QString &text)`, `QListWidget::itemSelectionChanged()`, and `QListWidget::itemDoubleClicked(QListWidgetItem *item)` match the new local connections used by the slice.

## Follow-up

Next step is scoped diff review and selective staging only; the surrounding worktree is still mixed and should not be staged file-wide.
