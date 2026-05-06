# Command Stack Design

## Goal

Move editor undo/redo history ownership out of Python-only `EditorModel` stacks and into the Rust core bridge, while keeping current Python map mutation behavior stable.

## Scope

M036/S01 implements a Rust-backed command journal for tile edit batches and routes existing `EditorModel` history operations through it. The first command family is the current tile edit batch surface: drawing, erasing, Cut/Paste tile changes, Replace Items, Remove Items by ID, and Borderize append changes.

## Current State

- `EditorModel` already builds `TileEditChange` batches and owns `_undo_stack` / `_redo_stack`.
- `MainWindow` already enables Undo/Redo from `editor.can_undo()` and `editor.can_redo()`.
- `EditorShellState` already exposes PyO3 methods for map-adjacent Rust services such as autoborder item resolution.
- `pyrme.core_bridge` already provides a native-or-fallback adapter shape.

## Architecture

Rust owns the command journal, not the Python map. Python still applies `TileState` mutations to its `MapModel` because the UI and renderer read that model today. `EditorModel` serializes each effective tile edit batch into simple Python values, records it through a command-history adapter, and applies returned replay batches on undo/redo.

Rust command batches store:

- command label
- ordered tile position
- optional before snapshot
- optional after snapshot

Undo returns the inverse replay batch. Redo returns the original replay batch. No-op batches are rejected and do not clear redo history.

## Non-Goals

- No clipboard format redesign.
- No file open/save command journal.
- No renderer, minimap, Search menu, or brush catalog changes.
- No migration of the whole Python `MapModel` into Rust.
- No broad legacy action parity expansion.

## Error Handling

Invalid command payloads raise `ValueError` at the PyO3 boundary. Python fallback mirrors native behavior so tests stay meaningful when `pyrme.rme_core` is not rebuilt.

## Acceptance

- Existing edit-menu tests still pass.
- New Rust tests prove command journal record, undo, redo, redo-clear, and no-op behavior.
- New bridge tests prove native/fallback command methods expose the same Python shape.
- `EditorModel` no longer owns `_undo_stack` / `_redo_stack`; it delegates history to the command bridge.
- Undo/Redo UI state remains correct after drawing, erasing, Replace Items, Remove Items, Cut/Paste, and Borderize.

## Verification

- `PATH="$HOME/.local/bin:$PATH" rtk cargo test -p rme_core command_stack`
- `PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py -q --tb=short`
- `PATH="$HOME/.local/bin:$PATH" rtk npm run preflight --silent`
