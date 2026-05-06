# Autoborder Core Bridge Design

## Goal

Bridge the existing Rust autoborder rule output into the Python shell so
`Borderize Selection` and `Borderize Map` stop being deferred gaps.

## Why

M030 already implemented pure `rme_core` autoborder rules and deterministic
`AutoborderPlan` output. M031 kept the Edit menu Borderize actions deferred
because no Python bridge or map mutation consumer existed. The next narrow slice
is therefore not a new rule engine; it is the bridge from plan output to
undoable `EditorModel` tile mutation.

## Sources of Truth

- `GAP_ANALYSIS.md`
- `.gsd/milestones/M030-autoborder-rules/`
- `.gsd/milestones/M031-menu-functionality-gaps/slices/S04/T03-SUMMARY.md`
- `crates/rme_core/src/autoborder.rs`
- `pyrme/ui/main_window.py`
- `pyrme/editor/model.py`
- `tests/python/test_legacy_edit_menu.py`

## Scope

- Add a small PyO3 shell method that consumes simple neighborhood/rule inputs
  and calls the existing Rust `resolve_autoborder_plan`.
- Add a Python bridge method that proxies native output and keeps fallback
  behavior deterministic for non-native test environments.
- Add undoable map mutation for border item stack additions in `EditorModel`.
- Wire only `Edit -> Border Options -> Borderize Selection/Map`.
- Keep unsupported rule/catalog families explicit.

## Non-Goals

- No renderer changes.
- No minimap work.
- No Search menu changes.
- No Randomize implementation.
- No item palette redesign.
- No broad brush-system rewrite.
- No full legacy XML autoborder rule importer.

## Architecture

### Rust

Rust remains the owner of autoborder decision logic. The new shell method should
adapt Python-friendly inputs into `GroundBorderRule` and `AutoborderNeighborhood`,
then return item ids from `AutoborderPlan`.

### Python Bridge

`EditorShellCoreBridge` owns call normalization. It exposes one stable Python
method for callers and hides the native PyO3 argument order. Fallback mode may
only return deterministic supported output; it must not claim broad parity.

### Model Mutation

`EditorModel` owns tile mutation and undo/redo history. Borderize appends border
items to existing tile stacks, suppresses duplicates, and records normal
`TileEditChange` entries.

### UI Wiring

`MainWindow` stays a thin action router. It derives supported starter brush data
from the shared Python brush catalog, builds eight-neighbor inputs, calls the
bridge, and applies returned items through `EditorModel`.

## Acceptance Criteria

- `Borderize Selection` mutates selected supported ground tiles.
- `Borderize Map` mutates supported map tiles.
- Mutations are undoable and avoid duplicate border stack items.
- Native bridge uses existing `resolve_autoborder_plan`.
- `Randomize Selection/Map` remain explicit catalog gaps.
- Targeted Rust/Python tests and ruff pass.
