# M033 Roadmap - Brush Catalog UI Bridge

## S01 - BRUSH-CATALOG-UI-BRIDGE

Expose the M029 brush catalog contract through the PyQt shell:

- define Python brush catalog view-model entries
- replace placeholder Terrain/brush rows with real catalog rows
- emit catalog brush selection from `BrushPaletteDock`
- update `MainWindow` active brush state from catalog entries
- reuse the same catalog in `Jump to Brush`
- preserve Item palette and Search menu behavior

## Follow-up

- Ground/Wall brush apply can consume active catalog brush ids later.
- PyO3 can expose native `BrushCatalog` later.
- Autoborder preview stays out of scope for this milestone.
