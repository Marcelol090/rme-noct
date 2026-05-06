# M041 Import File Bridge Design

## Objective

Expose M040 map-tile merge through the editor core bridge so Python/UI code can import another `.otbm` map into the current editor state without replacing the active map.

This slice turns the pure Rust merge primitive into a path-based bridge. It loads a source `.otbm`, applies explicit X/Y/Z offsets, merges source tiles into the current `EditorShellState` map, and returns M040 merge counts to the caller.

## Context

M040 added `crates/rme_core/src/merger.rs`:

- `CollisionPolicy::Replace`
- `CollisionPolicy::Skip`
- `MapMergeOptions { offset_x, offset_y, offset_z, collision_policy }`
- `MergeReport { copied_tiles, replaced_tiles, skipped_existing_tiles, discarded_tiles }`
- `merge_map_tiles(target, source, options)`

Existing OTBM bridge methods live on `EditorShellState` in `crates/rme_core/src/editor.rs`:

- `load_otbm(path)` replaces the active map and loads XML sidecars.
- `save_otbm(path)` saves the active map and writes XML sidecars.

Existing Python adapter behavior lives in `pyrme/core_bridge.py`, where `EditorShellCoreBridge` wraps native methods and falls back honestly when the native module is stale or missing.

## Legacy Contract

Legacy RME imports another map by loading it, applying an offset, and moving imported tiles into the current map. M040 already captured the core tile movement behavior. M041 only connects that behavior to a file path and Python-facing bridge.

Legacy import also has wider domain behavior for resize prompts, houses, spawns, towns, waypoints, and teleport rewrites. Those remain out of scope for this bridge slice because M040 intentionally kept sidecar/domain remapping separate.

## Scope

Add a native method:

```text
EditorShellState.import_otbm(path, offset_x=0, offset_y=0, offset_z=0, collision_policy="replace")
    -> (copied_tiles, replaced_tiles, skipped_existing_tiles, discarded_tiles)
```

The method must:

- read the source `.otbm` from `path`
- parse it with `crate::io::otbm::load_otbm`
- convert `collision_policy` from `"replace"` or `"skip"` into M040 `CollisionPolicy`
- call `merge_map_tiles(&mut self.map, &source_map, options)`
- rely on `MapModel` tile mutation generation to advance when `report.copied_tiles > 0`
- return exact M040 report counts as a Python tuple
- raise `PyValueError` for file read, parse, or unsupported policy errors

Add a Python adapter report:

```python
@dataclass(frozen=True)
class ImportMapReport:
    copied_tiles: int
    replaced_tiles: int
    skipped_existing_tiles: int
    discarded_tiles: int
```

Add a Python bridge method:

```text
EditorShellCoreBridge.import_otbm(path, offset_x=0, offset_y=0, offset_z=0, collision_policy="replace")
    -> ImportMapReport | None
```

The adapter returns `None` when the native method is unavailable or raises, matching current honest bridge behavior for stale native modules. It must not fake a successful import in the Python fallback.

## Non-Goals

- No File menu wiring.
- No Qt dialog.
- No Search menu changes.
- No tileset export.
- No map resize prompt.
- No import of waypoint, spawn, house, town, or teleport sidecar/domain records.
- No fake fallback merge in Python.

## Design Skill Note

Skill search found `anthropics/skills@frontend-design` as a strong design skill candidate for future UI slices. M041 is non-UI core bridge work, so this slice continues with Superpowers brainstorming/spec workflow only. Use the frontend design skill later when the import dialog or file menu UX is planned.

## Testing

Rust tests should cover:

- importing a saved source `.otbm` copies an offset tile into the active map
- `"replace"` overwrites an existing destination tile and increments `replaced_tiles`
- `"skip"` leaves an existing destination tile unchanged and increments `skipped_existing_tiles`
- an out-of-bounds offset increments `discarded_tiles`
- a copied import advances `map_generation` while the metadata-only dirty flag remains unchanged
- unsupported collision policy raises `PyValueError`
- missing or invalid source path raises `PyValueError`

Python tests should cover:

- `EditorShellCoreBridge.import_otbm()` converts a native 4-value tuple into `ImportMapReport`
- missing native method returns `None`
- native exception returns `None`
- native test is skipped when `pyrme.rme_core` is stale, matching existing native bridge tests

## Verification

Expected implementation verification:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && export PYO3_PYTHON=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin/python3.12 && export LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:${LD_LIBRARY_PATH:-} && export RUSTFLAGS="-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l dylib=python3.12" && cargo test -p rme_core editor_import --quiet'
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && python3 -m pytest tests/python/test_core_bridge.py tests/python/test_rme_core_editor_shell.py -q --tb=short'
```

Use `rtk` as the terminal wrapper when it gives concise output without hiding failure details. Keep Windows Git for gitdir-sensitive staging and commits in this Windows worktree.
