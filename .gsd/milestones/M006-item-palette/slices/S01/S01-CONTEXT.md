# S01 Context - ITEM-10-MODEL-VIEW-PALETTE

## Scope

Replace the mock `Item` tab internals with a real model/view palette while preserving the existing brush palette dock shell.

## Non-Goals

- No full item database loading.
- No sprite/icon rendering.
- No backend brush activation beyond explicit shell state.
- No changes to Terrain, Doodads, Creature, or RAW beyond keeping their list behavior stable.

## Review Notes

- Gap review found one widget polish issue: empty-state label alignment was a no-op. A RED test was added and the label now uses `Qt.AlignmentFlag.AlignCenter`.
- `main_window.py` contains unrelated legacy-shell dirty work in the current worktree, so commit staging must avoid file-wide staging unless the selected hunks are reviewed.
