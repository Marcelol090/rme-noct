# M033 Context - Brush Catalog UI Bridge

## Why

M029 created the Rust brush catalog and deterministic placement commands. M030 created pure autoborder plan output. The PyQt shell still displays placeholder non-Item brush rows, so users cannot select real ground or wall brush definitions from the palette.

## Contract

- GitHub issue #72 remains the approved Phase 3 source.
- M029 `BrushCatalog` fields are mirrored in a Python UI view model until PyO3 exposes the native catalog.
- `BrushPaletteDock` non-Item tabs use real catalog entries, not generated placeholders.
- Catalog brush selection updates shell active brush state and canvas sync.
- Item palette behavior stays unchanged.
- `Jump to Brush` uses the same local catalog entries as the dock.

## Source Evidence

- `crates/rme_core/src/brushes.rs`
- `.gsd/milestones/M029-brush-engine-alpha/M029-brush-engine-alpha-CONTEXT.md`
- `.gsd/milestones/M030-autoborder-rules/M030-autoborder-rules-CONTEXT.md`
- `pyrme/ui/docks/brush_palette.py`
- `pyrme/ui/dialogs/find_brush.py`
- `pyrme/ui/main_window.py`
- `tests/python/test_item_palette_integration.py`
- `tests/python/test_find_brush_tier2.py`

## Non-Goals

- No renderer changes.
- No minimap generation.
- No Search menu changes.
- No PyO3 `BrushCatalog` export.
- No full XML brush loader.
- No map mutation when a catalog brush is selected.
- No autoborder preview or recalculation.
