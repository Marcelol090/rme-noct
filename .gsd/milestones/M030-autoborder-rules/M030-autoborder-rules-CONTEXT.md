# M030 Context - Autoborder rules

## Why

M029 closed brush catalog and deterministic brush placement. Next safe slice is legacy autoborder: edge-name mapping, 8-neighbour classification, and stable placement plan output. This gate stays pure Rust and stops before Qt, preview, or map mutation.

## Contract

- `AutoBorder::edgeNameToID` mapping stays exact for `n`, `w`, `s`, `e`, `cnw`, `cne`, `csw`, `cse`, `dnw`, `dne`, `dsw`, `dse`.
- Rule engine is deterministic for the same 8-neighbour input.
- `optional`, `group`, and `to=all|none` stay represented.
- Validation fails on duplicate ids, duplicate names, or unknown edge names.
- No preview widgets, no map mutation, no wall rewrite in this gate.

## Source Evidence

- `remeres-map-editor-redux/source/brushes/ground/auto_border.h`
- `remeres-map-editor-redux/source/brushes/ground/auto_border.cpp`
- `remeres-map-editor-redux/source/brushes/ground/ground_border_calculator.cpp`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush.h`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush_loader.cpp`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush_arrays.cpp`
- `remeres-map-editor-redux/source/brushes/brush_enums.h`

## Non-Goals

- No Qt widgets.
- No `Gui::UpdateAutoborderPreview`.
- No `TileOperations::borderize` or direct tile mutation.
- No wall brush rewrite.
- No renderer changes.
