# M008 Context - Brush shell wiring

## Why

M007 closed the backend activation contract, but the local worktree still held the pending shell wiring that proves palette, dialog, and toolbar commands actually drive that contract from `MainWindow`.

## Contract

- `MainWindow` remains a shell sync layer over `EditorSessionState` and `EditorModel`.
- `Jump to Brush` can select either a palette page or an item-backed brush through a local dialog seam.
- `Jump to Item` can activate an item brush or report the map-search gap honestly.
- Palette switching clears stale shared search state and stale item activation when needed.
- Brush mode toolbar state and the Tool Options dock label come from the same session mode.
- WSL preflight must use the repo-local Python launcher and the platform-default npm script shell instead of hardcoded Windows-only assumptions.

## Non-Goals

- No renderer draw behavior changes.
- No new dock types or palette taxonomy.
- No publish/merge automation in this milestone.
