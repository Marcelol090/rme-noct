# T03 Summary - Map Statistics Bridge

- Added `MapStatisticsSnapshot`.
- Added `EditorModel.collect_statistics()`.
- `MapStatisticsDialog` now accepts explicit `statistics`.
- `MainWindow._show_map_statistics()` passes current editor statistics into the dialog.

Real values:
- `tile_count`
- `item_count`
- `walkable_tile_count` as current tile count
- `blocking_tile_count` as `0`

Unsupported sidecar/population values remain `0`.
