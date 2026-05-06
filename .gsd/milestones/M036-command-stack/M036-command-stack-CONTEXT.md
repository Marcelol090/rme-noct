# M036 Command Stack Context

## Source

`GAP_ANALYSIS.md` tracks `COMMAND-STACK` as the next gap after M035. On `origin/main`, M031 already implemented working Python undo/redo and tile edit history; M036 upgrades ownership of that command journal to Rust.

## Current State

- `pyrme/editor/model.py` owns Python `_undo_stack` and `_redo_stack`.
- `pyrme/ui/main_window.py` already wires Edit Undo/Redo to `EditorModel`.
- `pyrme/core_bridge.py` already exposes native-or-fallback bridge methods for Rust services.
- `crates/rme_core/src/editor.rs` hosts the PyO3 `EditorShellState`.

## Slice Boundary

M036/S01 adds a Rust-backed tile command journal and routes existing Python edit history through it. It does not move map storage to Rust, redesign clipboard, touch renderer/minimap/Search menu, or expand unrelated legacy menu gaps.
