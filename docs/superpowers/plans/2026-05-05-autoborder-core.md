# Autoborder Core Bridge Implementation Plan

> Skill path: `superpowers:executing-plans`. Keep one slice, but verify each layer.

## Live Scope Rebase

`origin/main` already contains M030 pure Rust autoborder rules in
`crates/rme_core/src/autoborder.rs`. This slice must not recreate that engine.

**Goal:** consume existing `AutoborderPlan` from Python/UI and remove the
`Borderize Selection/Map` deferred gap by adding a real map mutation consumer.

**Non-goals:** renderer, minimap, Search menu, randomize, broad brush rewrite,
legacy XML rule import, or fake border output. `Randomize Selection/Map` remains
explicitly deferred until `TileState` has ground variant catalog data.

## Files

- Modify: `crates/rme_core/src/editor.rs`
- Modify: `pyrme/core_bridge.py`
- Modify: `pyrme/editor/model.py`
- Modify: `pyrme/ui/main_window.py`
- Modify: `tests/python/test_core_bridge.py`
- Modify: `tests/python/test_rme_core_editor_shell.py`
- Modify: `tests/python/test_legacy_edit_menu.py`
- Create: `.gsd/milestones/M035-autoborder-core-bridge/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M035-autoborder-core-bridge/slices/S01/S01-SUMMARY.md`
- Modify: `.gsd/STATE.md`

## Task 1: Rust Shell Export

- [ ] RED: add native test that `EditorShellState.resolve_autoborder_items(...)`
  returns deterministic item ids from existing `resolve_autoborder_plan`.
- [ ] GREEN: add a PyO3 method that accepts simple brush-neighbor/rule inputs and
  returns placement item ids. It must build `GroundBorderRule` and
  `AutoborderNeighborhood`, then call the existing resolver.
- [ ] Verify: `rtk cargo test -p rme_core autoborder editor`

## Task 2: Python Bridge And Model Mutation

- [ ] RED: add Python bridge test for `EditorShellCoreBridge.resolve_autoborder_items`.
- [ ] RED: add `EditorModel.append_border_items` history test.
- [ ] GREEN: proxy native shell method and keep fallback deterministic for tests.
- [ ] GREEN: apply border item additions through `_apply_changes` with undo/redo
  support and duplicate suppression.
- [ ] Verify:
  `rtk test .venv/bin/python -m pytest tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py -q --tb=short`

## Task 3: MainWindow Borderize Wiring

- [ ] RED: update edit-menu tests so `Borderize Selection` and `Borderize Map`
  mutate existing tiles and report counts.
- [ ] GREEN: route only Borderize actions to bridge/model. Keep Randomize and
  other unsupported actions deferred with exact evidence.
- [ ] Verify:
  `rtk test .venv/bin/python -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short`

## Task 4: GSD Closeout

- [ ] Add milestone/slice plan and summary.
- [ ] Update `.gsd/STATE.md`.
- [ ] Run targeted Rust/Python verification plus ruff.
- [ ] Run `caveman-review` on full diff before commit.

## Acceptance

- Borderize actions call a real Python bridge.
- Python bridge calls existing Rust autoborder plan logic when native core is present.
- Python map mutation is undoable and avoids duplicate border stack items.
- Randomize remains an explicit gap, not a stub.
- No unrelated UI/search/renderer changes.
