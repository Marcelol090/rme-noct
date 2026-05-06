# M036/S01 - Command Stack Bridge

Design source: `docs/superpowers/specs/2026-05-05-command-stack-design.md`
Plan source: `docs/superpowers/plans/2026-05-05-command-stack.md`

## Scope

- Add Rust `CommandStack` for tile edit batches.
- Expose record/undo/redo/can-undo/can-redo through `EditorShellState`.
- Mirror behavior in Python fallback bridge.
- Route `EditorModel` tile history through bridge-backed command history.
- Preserve current Edit menu behavior and status text.

## Non-Goals

- no renderer changes
- no minimap changes
- no Search menu changes
- no clipboard redesign
- no file lifecycle command journal
- no full Rust `MapModel` ownership migration

## Tasks

- [x] T01: Add Rust command stack domain and tests.
- [x] T02: Expose PyO3/fallback command history bridge.
- [x] T03: Route Python `EditorModel` undo/redo through the bridge.
- [x] T04: Re-verify UI edit actions and close review gaps.

## Stop Condition

S01 done when Python edit operations still mutate `MapModel`, Rust/fallback command history owns undo/redo state, targeted Rust/Python tests pass, and caveman-review finds no gap.
