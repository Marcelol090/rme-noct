# S01 Context - BRUSH-20-SHELL-COMMAND-WIRING

## Scope

Isolate the pending shell command wiring delta in `MainWindow`, its local dialog export/test seams, and the minimum WSL preflight fix needed to verify the slice honestly.

## Boundaries

- Include `package.json`, `.npmrc`, and `scripts/run-python.mjs` for launcher/preflight behavior only.
- Include `pyrme/ui/main_window.py`, `pyrme/ui/dialogs/find_brush.py`, `pyrme/ui/dialogs/__init__.py`, `tests/python/test_main_window_commands_m5.py`, `tests/python/test_main_window_editor_shell_actions.py`, and `tests/python/test_find_brush_tier2.py`.
- Do not include renderer draw behavior, new dock types, or unrelated legacy menu parity hunks.

## Gap Review

The local delta already contained the intended shell wiring. This slice records, verifies, and scopes that work without pretending the surrounding dirty worktree is clean.
