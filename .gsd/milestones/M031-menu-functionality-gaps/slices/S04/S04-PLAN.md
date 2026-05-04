# M031/S04 - Edit Map Transforms

Plan source: `docs/superpowers/plans/2026-05-01-m031-menu-functionality-gaps.md`

## Scope

- Replace Items.
- Borderize Selection/Map.
- Randomize Selection/Map.
- Remove Items by ID.
- Remove all Corpses.
- Remove all Unreachable Tiles.
- Clear Invalid Houses.
- Clear Modified State.

## Tasks

- [x] T01: failing tests for transformation actions and confirmation seams.
- [x] T02: add pure `EditorModel` operations where current map data supports them.
- [x] T03: consume M030 autoborder plan for borderize actions where available.
- [x] T04: keep unsupported corpse/unreachable/house cleanup explicit with evidence if required data is absent.
- [x] T05: closeout summary and state update.

## Files

- `pyrme/editor/model.py`
- `pyrme/ui/main_window.py`
- `crates/rme_core/src/autoborder.rs`
- `tests/python/test_legacy_edit_menu.py`

## Verification

`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short`

## Stop Condition

S04 done when supported transformations mutate map state with tests, and unsupported transformations have exact missing-data evidence.
