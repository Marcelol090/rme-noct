# M035 Ground and Wall Brushes Context

## Source

GitHub issue #72 lists `Ground/Wall Brushes` as an approved Phase 3 task.

## Current State

- M029 implemented Rust brush definitions and placement commands.
- M030 implemented pure autoborder rule resolution.
- M033 exposed default ground and wall brush catalog entries in PyQt.
- M034 exposed real editor mode actions in the Drawing Tools toolbar.
- Python `EditorModel` can mutate tiles for item draw and erase, but catalog brush ids do not apply to the map yet.

## Slice Boundary

M035/S01 applies default catalog ground and wall brush selections through the Python editor model only. It does not implement XML loading, autoborder mutation, wall alignment recalculation, renderer changes, Search menu changes, or PyO3 exports.
