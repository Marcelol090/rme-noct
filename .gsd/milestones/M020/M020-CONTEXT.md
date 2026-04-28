# M020 - SPR frame table metadata

## Intent

Continue the sprite asset path after M019 DAT item metadata by parsing the SPR archive header and sprite offset table into renderer-facing frame metadata.

M020 does not decode compressed SPR pixel payloads, build atlas textures, upload textures, paint sprites, or auto-detect client versions. It records which sprite ids have archive offsets so later pixel decoding can read payloads through a tested seam.

## Legacy reference

- `remeres-map-editor-redux/source/rendering/core/sprite_archive.cpp`
- `remeres-map-editor-redux/source/rendering/core/sprite_archive.h`
- `remeres-map-editor-redux/source/rendering/core/game_sprite.cpp`
- `remeres-map-editor-redux/source/rendering/core/game_sprite.h`

Legacy flow:

1. Read SPR signature.
2. Read sprite count as compact `u16` or extended `u32`.
3. Read one `u32` archive offset for each sprite id starting at 1.
4. Treat zero offsets as missing/empty sprites.
5. Defer compressed payload reads until a later `readCompressed()`-style path.

## Scope

In scope:

- Pure Python parser for SPR signature, count, and offset table.
- Compact and extended sprite count widths.
- `SprFrameRecord` output compatible with `sprite_catalog_adapter.py`.
- `archive_offset` metadata retained on sprite frame records.
- Deterministic parse errors for excessive counts and truncated offset tables.

Out of scope:

- Compressed pixel payload reads.
- Transparent-color headers and decompression.
- Atlas texture construction.
- UI rendering or sprite painting.
- Automatic client-version detection.
