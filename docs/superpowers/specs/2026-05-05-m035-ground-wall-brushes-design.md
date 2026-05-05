# M035 Ground and Wall Brushes Design

## Source

GitHub issue #72 lists `Ground/Wall Brushes` as the remaining approved Phase 3 brush/toolset task after Brush Engine Foundation, Autoborder Logic, and Tool Selection UI.

## Goal

Make selected catalog brushes apply to the active Python map model when the editor is in `drawing` mode.

## Current State

- M029 defines Rust brush catalog behavior: ground brushes resolve to `SetGround`, wall brushes resolve to `AddWall`.
- M030 defines pure autoborder plan output, but no map mutation.
- M033 exposes visible Python brush catalog entries with ids like `brush:ground:10` and `brush:wall:20`.
- M034 exposes real drawing toolbar modes.
- `EditorModel.apply_active_tool_at()` currently applies only item brushes through `active_item_id`.

## Design

Add a small Python brush lookup seam next to the existing UI catalog model. It maps active ids such as `brush:ground:10` and `brush:wall:20` to placement intent using the same default entries shown in the palette.

In `EditorModel.apply_active_tool_at()`:

- `selection` keeps selecting positions.
- `drawing` with `item:2148` keeps setting tile ground to that item.
- `drawing` with `brush:ground:10` sets the tile ground to the brush look item, preserving existing stack items.
- `drawing` with `brush:wall:20` appends the brush look item to the tile stack, preserving existing ground and stack order.
- `erasing` keeps removing the whole tile.
- `fill` and `move` keep no-op behavior.

`MainWindow` does not gain new UI controls. Brush palette selection already writes the active brush id into the shared editor session; this slice makes that active id meaningful during canvas apply.

## Scope

- Python editor model brush placement for default ground and wall catalog entries.
- Tests for backend apply behavior and canvas-driven apply behavior.
- GSD closeout docs for M035/S01.

## Non-Goals

- No Rust or PyO3 brush catalog export.
- No XML brush loader.
- No autoborder recalculation or neighbor wall alignment.
- No renderer or minimap changes.
- No Search menu changes.
- No new toolbar or palette visual design.

## Legacy Notes

Legacy `GroundBrush::draw()` places a selected ground item on the tile. Legacy `WallBrush::draw()` cleans matching wall state and adds a wall item, with later wall-border logic responsible for final shape. This slice implements only the safe first placement step already represented by M029: `SetGround` and `AddWall`.

## Acceptance

- Selecting `grass` then applying Draw sets ground item `4526`.
- Selecting `stone wall` then applying Draw appends wall item `3361`.
- Reapplying the same wall brush to the same tile is idempotent for this starter seam.
- Item brush, selection, erasing, fill, and move behavior remains unchanged.
- Focused Python tests and preflight pass.
