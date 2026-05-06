# M040 Core Map Merge Design

## Objective

Implement the first real import/merge primitive for maps in `rme_core`: copy tiles from one `MapModel` into another with an explicit offset and collision policy.

This slice replaces the earlier stub-shaped M040 idea. Success requires observable tile movement, collision handling, invalid-position discard reporting, and preservation of tile contents. `tileset export`, UI dialogs, file selection, and full legacy sidecar import remain separate follow-up slices.

## Legacy Contract

Legacy RME imports another map by loading it, applying an X/Y offset, and moving each imported tile into the current map. The relevant behavior lives in `remeres-map-editor-redux/source/editor/persistence/editor_persistence.cpp`:

- invalid destination positions are discarded
- out-of-bounds resize prompts exist in the UI layer
- imported tiles replace existing destination tiles through the map set-tile path
- houses, spawns, towns, waypoints, and teleport rewrites are extra import-domain behavior

M040 keeps only the core tile merge behavior. Sidecar/domain remapping is intentionally not included.

## Scope

Build `crates/rme_core/src/merger.rs` with:

- `CollisionPolicy::Replace` and `CollisionPolicy::Skip`
- `MapMergeOptions { offset_x, offset_y, offset_z, collision_policy }`
- `MergeReport { copied_tiles, replaced_tiles, skipped_existing_tiles, discarded_tiles }`
- `merge_map_tiles(target: &mut MapModel, source: &MapModel, options: MapMergeOptions) -> MergeReport`

The function must:

- iterate source tiles
- translate each tile position with X/Y/Z offsets
- discard destinations outside `0..=MAX_XY` and `0..=MAX_Z`
- clone tile contents into the translated destination position
- replace or skip collisions according to `CollisionPolicy`
- return counts precise enough for UI/file-import layers later

## Non-Goals

- No UI dialog.
- No `.otbm` path-based import API.
- No tileset export.
- No town, house, spawn, waypoint, or teleport remapping.
- No fake success API that can pass without moving tile data.

## Testing

Rust tests live next to the merger module and must prove:

- offset merge copies a tile to the translated position
- ground, stack items, flags, and house id are preserved
- replace policy overwrites an existing destination tile and increments `replaced_tiles`
- skip policy leaves an existing destination tile unchanged and increments `skipped_existing_tiles`
- invalid translated positions are discarded and counted

Verification command:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m040-core-map-merge-20260506" && export PYO3_PYTHON=/home/marcelo/.local/bin/python3.12 && export LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:${LD_LIBRARY_PATH:-} && cargo test -p rme_core merger --quiet'
```

If `rtk` becomes available, use the same command body through `rtk` as the bench wrapper. In the current environment `rtk` is not on `PATH`, so WSL explicit commands are the fallback.
