# M035/S01 - Ground and Wall Brushes

Design source: `docs/superpowers/specs/2026-05-05-m035-ground-wall-brushes-design.md`
Plan source: `docs/superpowers/plans/2026-05-05-m035-ground-wall-brushes.md`

## Scope

- Apply selected default ground catalog brushes in `drawing` mode
- Apply selected default wall catalog brushes in `drawing` mode
- Preserve item brush, selection, erase, fill, and move behavior
- Keep canvas-driven active tool application synced

## Non-Goals

- no renderer changes
- no minimap changes
- no Search menu changes
- no XML brush loader
- no autoborder mutation
- no wall alignment recalculation
- no PyO3/Rust export changes

## Tasks

- [x] T01: Write implementation plan after design review.
- [ ] T02: Execute TDD implementation.
- [ ] T03: Closeout docs, caveman-review, and verification.

## Stop Condition

S01 done when selected ground and wall catalog brushes mutate the Python map model through the active drawing tool, focused tests pass, and all non-goals remain untouched.
