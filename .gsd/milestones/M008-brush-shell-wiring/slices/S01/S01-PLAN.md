# S01: BRUSH-20-SHELL-COMMAND-WIRING

**Goal:** Isolate and verify the pending `MainWindow` shell wiring so palette, dialog, and toolbar commands drive the canonical brush backend honestly in WSL.

**Demo:** `Jump to Brush` or `Jump to Item` selects a palette or item-backed brush, palette switching clears stale state, toolbar mode changes update the backend and Tool Options label, and WSL preflight passes with the repo-local Python launcher.

## Must-Haves

- Export `FindBrushDialog` and `FindBrushResult` from `pyrme.ui.dialogs`.
- Keep `MainWindow` dialog factories injectable for jump/find flows.
- `Jump to Brush` handles palette and item results.
- `Jump to Item` handles accepted item activation and the rejected search-on-map gap honestly.
- Palette switching clears stale shared search and stale item activation when required.
- Brush mode toolbar syncs `EditorSessionState.mode` and Tool Options label from one source of truth.
- `npm run preflight --silent` passes in WSL.

## Non Goals

- No renderer draw behavior changes.
- No new palette taxonomy or dock redesign.
- No file-wide staging of `main_window.py`.

## Verification

- `./.venv/bin/python3.12 -m ruff check pyrme/ui/main_window.py pyrme/ui/dialogs/find_brush.py pyrme/ui/dialogs/__init__.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_find_brush_tier2.py`
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_find_brush_tier2.py tests/python/test_main_window_commands_m5.py tests/python/test_main_window_editor_shell_actions.py`
- `./.venv/bin/python3.12 -m pytest -q -s --tb=short tests/python/test_editor_activation_backend.py tests/python/test_main_window_new_view.py tests/python/test_canvas_seam_m4.py`
- `npm run preflight --silent`
- `env QT_QPA_PLATFORM=offscreen ./.venv/bin/python3.12 -m pyrme`

## Tasks

- [x] **T01: Restore WSL preflight launcher** `est:15m`
  - Files: `package.json`, `.npmrc`, `scripts/run-python.mjs`
  - Done when: npm scripts no longer depend on Windows `py -3` or forced `cmd.exe`, and `npm run preflight --silent` passes in WSL.

- [x] **T02: Add local Jump to Brush dialog/export seam** `est:15m`
  - Files: `pyrme/ui/dialogs/find_brush.py`, `pyrme/ui/dialogs/__init__.py`, `tests/python/test_find_brush_tier2.py`
  - Done when: local brush search can return palette and item results and the dialog/export seam is covered by focused tests.

- [x] **T03: Wire shell brush commands into backend state** `est:25m`
  - Files: `pyrme/ui/main_window.py`, `tests/python/test_main_window_commands_m5.py`, `tests/python/test_main_window_editor_shell_actions.py`
  - Done when: jump actions, palette switching, brush mode toolbar, zoom, screenshot safe gap, and new-view shell flows are covered without adding a second source of truth.

- [x] **T04: Prove adjacent regressions stay green** `est:15m`
  - Files: `tests/python/test_editor_activation_backend.py`, `tests/python/test_main_window_new_view.py`, `tests/python/test_canvas_seam_m4.py`
  - Done when: activation backend, new view, and canvas seam regressions pass alongside the new shell wiring tests.

- [x] **T05: Record M008 closeout and workflow notes** `est:15m`
  - Files: `.gsd/milestones/M008-brush-shell-wiring/`, `.gsd/STATE.md`, `.gsd/PROJECT.md`, `.gsd/REQUIREMENTS.md`, `.gsd/DECISIONS.md`, `.gsd/task-registry.json`, `pyrme/ui/AGENTS.md`
  - Done when: the slice is summarized with real verification output, the smoke command drift is documented, and the next action stays scoped to review/staging only.

## Closeout

S01 is complete when WSL preflight passes, shell commands drive backend state through focused tests, and M008 is recorded without mixing unrelated worktree changes.
