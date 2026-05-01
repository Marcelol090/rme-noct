# M029 Context - Brush engine alpha

## Why

Issue #72 moves the project into Phase 3 editing behavior. The current editor has Python-side item activation and tile mutation seams, but Rust `BrushCatalog` is still a placeholder. The next safe parity step is to define the Rust brush domain before adding autoborder or UI tooling.

## Contract

- Legacy `remeres-map-editor-redux` brush behavior is source of truth.
- `BrushCatalog` owns validated brush definitions and lookup.
- Rust brush application returns explicit changed/no-op outcomes.
- Ground brush placement sets configured ground item ids.
- Wall brush placement adds configured wall item ids without claiming neighbor border recalculation.
- Autoborder remains a later milestone.

## Source Evidence

- `remeres-map-editor-redux/source/brushes/brush.h`
- `remeres-map-editor-redux/source/brushes/brush.cpp`
- `remeres-map-editor-redux/source/brushes/brush_enums.h`
- `remeres-map-editor-redux/source/brushes/managers/brush_manager.h`
- `remeres-map-editor-redux/source/brushes/managers/brush_manager.cpp`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush.h`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush.cpp`
- `remeres-map-editor-redux/source/brushes/wall/wall_brush.h`
- `remeres-map-editor-redux/source/brushes/wall/wall_brush.cpp`
- `remeres-map-editor-redux/source/brushes/ground/auto_border.h`

## Non-Goals

- No full XML brush loader.
- No `borders.xml` parser.
- No autoborder calculation.
- No wall neighbor alignment recalculation.
- No floating tool palette or visual redesign.
- No sprite rendering changes.
