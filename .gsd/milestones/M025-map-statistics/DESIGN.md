# M025 Map Statistics Design

## Goal

Replace the legacy safe gap behind `Map -> Statistics` with a real, read-only
statistics dialog fed by the Rust map model.

## Scope

- Count map-domain data already owned by `rme_core::map::MapModel`.
- Expose a narrow Python bridge method, `collect_statistics()`.
- Open a PyQt6 `MapStatisticsDialog` from the existing `Map -> Statistics`
  action.
- Keep fallback shell behavior honest: no native map data means no fake stats.

## Non-Goals

- No map mutation.
- No cleanup action implementation.
- No town manager domain model beyond counting distinct `house.townid()`.
- No async worker or long-running progress UI in this slice.
- No renderer, sprite, or viewport behavior changes.

## Approach Options

### A. Rust-first aggregation

`MapModel` owns a `MapStatistics` value object and aggregates tiles, items,
spawns, creatures, houses, towns, and waypoints in Rust. Python only displays
the result.

Pros: one source of truth, easy Rust tests, future native file-loaded maps can
reuse the same method. Cons: PyO3 export needed.

### B. Python-only dialog aggregation

The dialog reads Python-side shell state and computes counts in UI code.

Pros: fast to wire. Cons: duplicates domain logic, cannot see native-only map
data cleanly, encourages fake fallback data.

### C. Placeholder UI now, backend later

Keep `Map -> Statistics` opening a visual dialog with zeros until map APIs grow.

Pros: minimal code. Cons: violates no-stub rule and repeats current safe gap.

## Decision

Use Option A. Map statistics are domain facts, so the Rust `MapModel` should
own aggregation. The UI remains a read-only presenter.

## Data Contract

`MapStatistics` fields:

- `tile_count`
- `blocking_tile_count`
- `walkable_tile_count`
- `item_count`
- `spawn_count`
- `creature_count`
- `house_count`
- `total_house_sqm`
- `town_count`
- `waypoint_count`

`item_count` counts ground plus stack items. `walkable_tile_count` is the number
of stored tiles that are not marked blocking. `blocking_tile_count` follows
legacy `TILESTATE_BLOCKING = 0x0004`. `town_count` is derived from unique house
`townid` values until a separate town domain exists.

## UI Contract

`MapStatisticsDialog` is read-only and opens from `Map -> Statistics`.

It groups values into small sections:

- Environment: tiles, items, blocking, walkable
- Population: spawns, creatures, waypoints
- Housing: houses, total house sqm, towns
- Ratios: pathable percent, average sqm per house

If the shell has no `collect_statistics()` provider or returns `None`, labels
stay at `0` and the dialog still opens. This keeps fallback behavior honest.

## Testing

- Rust unit test proves `MapModel::collect_statistics()` counts tiles,
  blocking flags, items, spawns, creatures, houses, towns, and waypoints.
- Python dialog test proves all exposed fields render correctly and derived
  ratios handle normal values.
- MainWindow menu test proves `Map -> Statistics` uses a dialog seam and passes
  shell state.
- Existing map-menu gap test keeps cleanup actions as safe gaps while removing
  Statistics from the gap list.

## Verification

- `npm run preflight --silent`
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/python/test_map_statistics_dialog.py tests/python/test_legacy_map_menu.py -q --tb=short`
- `cargo test -p rme_core map_model_collects_statistics_from_tiles_and_sidecars`
- `python -m ruff check pyrme/core_bridge.py pyrme/ui/dialogs/__init__.py pyrme/ui/dialogs/map_statistics.py pyrme/ui/main_window.py tests/python/test_legacy_map_menu.py tests/python/test_map_statistics_dialog.py`
- `rustfmt --check --edition 2021 crates/rme_core/src/editor.rs crates/rme_core/src/lib.rs crates/rme_core/src/map.rs`
- `git diff --check`

## Stop Conditions

- Do not implement before this design is approved.
- Do not commit while branch is based on stale root checkout.
- Do not widen into cleanup handlers, town editing, renderer work, or readback
  persistence.
