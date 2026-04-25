# M021 - SPR compressed payload metadata

## Intent

Continue the sprite asset path after M020 SPR frame table metadata by reading raw compressed sprite payload bytes from archived SPR offsets.

M021 does not decompress the payload, interpret alpha, build atlas textures, upload textures, paint sprites, or auto-detect client versions. It proves the legacy `SpriteArchive::readCompressed()` boundary in Python: seek to the archived sprite payload location, skip the legacy 3-byte sprite data header, read the compressed payload size, and return the raw compressed bytes through a tested seam.

## Legacy reference

- `remeres-map-editor-redux/source/rendering/core/sprite_archive.cpp`
- `remeres-map-editor-redux/source/rendering/core/sprite_archive.h`
- `remeres-map-editor-redux/source/rendering/core/game_sprite.cpp`
- `remeres-map-editor-redux/source/rendering/core/game_sprite.h`

Legacy payload-read flow:

1. Reset target and size before reading.
2. Treat sprite id `0` as a successful empty read.
3. Treat offset `0` as a successful empty read.
4. Reject out-of-range sprite ids at the archive layer.
5. Seek to `archive_offset + 3`.
6. Read little-endian `u16` compressed payload size.
7. Read exactly that many raw compressed bytes.
8. Leave RLE decompression to `GameSprite::Decompress()`.

## Scope

In scope:

- Pure Python reader for compressed SPR payload bytes from an existing `SprFrameRecord`.
- `archive_offset + 3` seek behavior.
- Little-endian `u16` compressed payload size.
- Explicit empty outcome for sprite id `0` or offset `0`.
- Deterministic parse errors for negative offsets, offset past end, truncated size, and truncated payload bytes.

Out of scope:

- RLE decompression.
- Alpha or transparency interpretation.
- Atlas texture construction.
- UI rendering or sprite painting.
- Automatic client-version detection.
