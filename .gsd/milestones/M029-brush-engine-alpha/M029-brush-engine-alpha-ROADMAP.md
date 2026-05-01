# M029 Roadmap - Brush engine alpha

## S01 - BRUSH-ENGINE-ALPHA-CONTRACT

Create the first Rust brush engine contract:

- replace placeholder `BrushCatalog` with validated ground/wall brush definitions
- add legacy brush enums needed for core behavior
- resolve brushes by name and id
- reject reserved names, duplicate names, and unknown brush kinds
- produce deterministic ground and wall placement commands
- apply commands to `MapModel` through a narrow editor-core seam
- preserve current Python activation behavior

## Follow-up

Next slices should stay explicit:

- `M030-autoborder-rules`: parse/configure border rules and calculate ground/wall neighbor alignment.
- Tool Selection UI: connect brush catalog and active tool controls after core behavior exists.
- Ground/Wall Brushes UI: expose usable terrain brushes once core placement and border rules are stable.
