---
name: legacy-reference
description: Use when implementing any feature that has a C++ equivalent in remeres-map-editor-redux. Maps legacy C++ source files to their Python/Rust equivalents.
---

# Legacy C++ Reference Lookup

## How to Use

When implementing any feature for PyRME:
1. Find the corresponding C++ file in `remeres-map-editor-redux/source/`
2. Read the C++ header (.h) to understand the interface
3. Read the C++ implementation (.cpp) for behavior details
4. Port to Rust (performance) or Python (UI/logic)

## Legacy Source Map

### Core Data Structures → Rust (`crates/rme_core/src/`)

| C++ Path | Rust Target | Notes |
|----------|-------------|-------|
| `map/position.h` | `map/position.rs` | x,y,z with floor (0-15) |
| `map/tile.h` | `map/tile.rs` | Item stack, ground, creatures |
| `map/tile_operations.h/cpp` | `map/tile_ops.rs` | Tile manipulation |
| `map/tileset.h/cpp` | `map/tileset.rs` | Tile categories |
| `map/spatial_hash_grid.h` | `map/spatial_hash_grid.rs` | 64-tile cells, sorted vec |
| `map/basemap.h/cpp` | `map/base_map.rs` | Map container |
| `map/map.h/cpp` | `map/mod.rs` | Full map with metadata |
| `map/map_region.h/cpp` | `map/region.rs` | Region selection |
| `map/map_search.h/cpp` | `map/search.rs` | Item/tile search |
| `map/map_converter.h/cpp` | `map/converter.rs` | Format conversion |

### Editor Logic → Rust (`crates/rme_core/src/editor/`)

| C++ Path | Rust Target | Notes |
|----------|-------------|-------|
| `editor/selection.h/cpp` | `editor/selection.rs` | Session-based, sorted vec |
| `editor/copybuffer.h/cpp` | `editor/copy_buffer.rs` | Clipboard with BaseMap |
| `editor/action.h/cpp` | `editor/action.rs` | Undo/redo actions |
| `editor/action_queue.h/cpp` | `editor/action_queue.rs` | Batch action processing |
| `editor/editor.h/cpp` | `editor/mod.rs` | Editor state machine |

### File I/O → Rust (`crates/rme_core/src/io/`)

| C++ Path | Rust Target | Notes |
|----------|-------------|-------|
| `io/` directory | `io/otbm.rs` | OTBM v2-v6 parser |
| `item_definitions/` | `io/otb.rs` | items.otb parser |
| `assets/` | `io/dat.rs`, `io/spr.rs` | DAT/SPR loaders |

### Brushes → Rust (`crates/rme_core/src/brushes/`)

| C++ Path | Rust Target | Notes |
|----------|-------------|-------|
| `brushes/` directory | `brushes/mod.rs` | All brush types |

### UI → Python (`pyrme/ui/`)

| C++ Path | Python Target | Notes |
|----------|---------------|-------|
| `ui/` directory | `pyrme/ui/` | PyQt6 equivalents |
| `palette/` | `pyrme/ui/docks/` | Brush palettes |

### Rendering → Rust (`crates/rme_core/src/rendering/`)

| C++ Path | Rust Target | Notes |
|----------|-------------|-------|
| `rendering/` | `rendering/mod.rs` | wgpu renderer |

### Live Editing → Python + Rust

| C++ Path | Target | Notes |
|----------|--------|-------|
| `live/` | `pyrme/live/` + Rust | Multi-user collaboration |
| `net/` | `pyrme/net/` | Network layer |
