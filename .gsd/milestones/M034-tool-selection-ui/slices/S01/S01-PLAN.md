# M034/S01 - Tool Selection UI

Design source: `docs/superpowers/specs/2026-05-05-m034-tool-selection-ui-design.md`
Plan source: `docs/superpowers/plans/2026-05-05-m034-tool-selection-ui.md`

## Scope

- Real Select/Draw/Erase/Fill/Move toolbar actions
- Exclusive checked mode group
- Tool Options label sync
- Canvas activation sync

## Non-Goals

- no renderer changes
- no minimap changes
- no Search menu changes
- no new Fill/Move map mutation
- no PyO3/Rust changes

## Tasks

- [x] T01: Write implementation plan after design review.
- [x] T02: Execute TDD implementation.
- [x] T03: Closeout docs, caveman-review, and verification.

## Stop Condition

S01 done when all five toolbar modes are real checkable actions, session/tool-options/canvas sync stays correct, focused tests pass, and Fill/Move remain documented no-op backend behavior.
