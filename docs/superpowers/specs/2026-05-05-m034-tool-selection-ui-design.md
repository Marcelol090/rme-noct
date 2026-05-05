# M034/S01 Tool Selection UI Design

## Decision

Build the next approved Phase 3 slice from GitHub issue #72 as a narrow PyQt shell slice: convert the existing Drawing Tools toolbar from two real mode actions plus three inert actions into five real, exclusive editor-mode actions.

## Scope

- Add `selection`, `drawing`, `erasing`, `fill`, and `move` to `MainWindow.brush_mode_actions`.
- Keep all five toolbar actions checkable and mutually exclusive through the existing `QActionGroup`.
- Route every toolbar action through `MainWindow._set_editor_mode()`.
- Keep `_ToolOptionsDock` synchronized with the active mode label.
- Keep canvas activation synchronized through `set_editor_mode()` when the canvas supports the activation protocol.
- Preserve current backend behavior: `selection`, `drawing`, and `erasing` can apply real backend actions; `fill` and `move` only select mode in this slice and remain no-op on apply until a later backend slice.

## Non-Goals

- No renderer, minimap, or Search menu changes.
- No new map mutation behavior for `fill` or `move`.
- No brush size model, brush shape model, keyboard shortcuts, icons, or visual redesign.
- No PyO3 or Rust brush export changes.
- No floating palette; this slice uses the existing toolbar and dock seams.

## Architecture

`MainWindow` already owns the canonical mode state, toolbar actions, `ToolOptionsDock`, and canvas sync. M034/S01 keeps that ownership and removes inert toolbar actions by creating all five actions from the same data list.

The mode data remains small and explicit inside `MainWindow`: internal mode id, display label, and toolbar order. `_normalized_editor_mode()` and `_mode_label_for()` continue to define valid modes and labels. This avoids a new abstraction before there is a larger tool model.

## UI Contract

- Toolbar order: `Select`, `Draw`, `Erase`, `Fill`, separator, `Move`.
- Default checked action remains `Draw`.
- Triggering any action updates `EditorContext.session.mode`.
- Triggering any action updates `_ToolOptionsDock._mode_label`.
- Triggering any action updates supported canvas hosts through `set_editor_mode()`.
- Invalid stored or injected mode still normalizes to `drawing` and checks `Draw`.

## Testing

Focused tests should cover:

- all five toolbar actions exist in `brush_mode_actions`;
- `Erase`, `Fill`, and `Move` are checkable/exclusive and update session/tool-options/status;
- canvas activation receives `erasing`, `fill`, and `move`;
- existing `Select`/`Draw` behavior remains green;
- backend apply remains unchanged for `fill` and `move` no-op paths.

Baseline already verified before this spec:

- `QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_main_window_commands_m5.py tests/python/test_canvas_seam_m4.py tests/python/test_main_window_new_view.py tests/python/test_editor_activation_backend.py -q --tb=short`
- Observed: `60 passed in 7.00s`

## Traceability

- Issue: https://github.com/Marcelol090/rme-noct/issues/72
- Prior merged slice: PR #84 `M033/S01 Brush Catalog UI Bridge`
- Worktree: `.worktrees/m034-tool-selection-ui-20260505`
- Branch: `gsd/M034/S01-tool-selection-ui`
