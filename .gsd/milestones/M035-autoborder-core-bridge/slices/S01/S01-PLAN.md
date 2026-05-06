# M035/S01 - Autoborder Core Bridge

Design source: `docs/superpowers/specs/2026-05-05-autoborder-core-design.md`
Plan source: `docs/superpowers/plans/2026-05-05-autoborder-core.md`

## Scope

- Expose existing Rust `AutoborderPlan` through `EditorShellState`.
- Add Python bridge method for autoborder item resolution.
- Add undoable `EditorModel` border item append mutation.
- Wire `Edit -> Border Options -> Borderize Selection/Map`.

## Non-Goals

- no renderer changes
- no minimap changes
- no Search menu changes
- no Randomize implementation
- no broad brush-system rewrite
- no legacy XML rule importer

## Tasks

- [x] T01: Rebase plan against existing M030 Rust autoborder core.
- [x] T02: Write RED tests for Rust/Python/UI bridge behavior.
- [x] T03: Implement native bridge, Python fallback/proxy, model mutation, and menu wiring.
- [x] T04: Run verification and caveman-review.

## Stop Condition

S01 done when Borderize Selection/Map consume real autoborder bridge output,
mutate `EditorModel` with undo support, keep Randomize explicit, and targeted
Rust/Python verification passes.
