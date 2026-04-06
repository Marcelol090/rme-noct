---
name: pyrme-rust-core
description: Use when working on Rust core (rme_core) – PyO3 bindings, data structures, spatial hash, FNV hashing, OTBM parsing. Guides implementation following the legacy C++ architecture from remeres-map-editor-redux.
---

# PyRME Rust Core Development

## Principles

1. **Always reference the legacy C++ implementation** at `remeres-map-editor-redux/source/` before writing Rust code
2. **Use PyO3 Bound API** (latest) — never the deprecated GIL-ref API
3. **Zero-copy where possible** — use `PyBuffer`, shared references via `Arc`
4. **FNV hasher** for all hash maps (game data is integer-keyed, no DoS risk)
5. **Rayon** for parallel operations (sprite hashing, large map ops)
6. **Serde** for clipboard serialization (cross-instance support)

## Key Architecture Mappings (C++ → Rust)

| C++ (source/) | Rust (crates/rme_core/src/) |
|---------------|------------------------------|
| `map/position.h` | `map/position.rs` |
| `map/tile.h` | `map/tile.rs` |
| `map/spatial_hash_grid.h` | `map/spatial_hash_grid.rs` |
| `map/basemap.h` | `map/base_map.rs` |
| `editor/copybuffer.h` | `editor/copy_buffer.rs` |
| `editor/selection.h` | `editor/selection.rs` |
| `editor/action.h` | `editor/action.rs` |
| `io/` | `io/` (OTBM, OTB, DAT, SPR) |
| `brushes/` | `brushes/` |
| `game/` | `game/` (items, creatures, spawns) |

## SpatialHashGrid Design (from C++)

```
CELL_SHIFT = 6 → 64-tile cells
NODE_SHIFT = 2 → 4x4 tiles per node
Sorted Vec<CellEntry> (cache-friendly binary search)
Key: u64 packed from (cx, cy) with XOR bias
1-element cache for locality
visitLeaves() with row-based binary search
```

## Cross-Instance Clipboard (FNV-1a)

```rust
use fnv::FnvHasher;
use std::hash::Hasher;

fn sprite_hash(pixel_data: &[u8]) -> u64 {
    let mut hasher = FnvHasher::default();
    hasher.write(pixel_data);
    hasher.finish()
}
```

## Verification

After any Rust change:
```bash
cargo test --manifest-path crates/rme_core/Cargo.toml
maturin develop
pytest tests/ -v --tb=short
```
