# M019 - DAT item metadata

## Intent

Continue the sprite asset bundle path after M014 signature reads by parsing DAT item metadata from discovered client files.

M019 does not decode SPR pixels, build atlas textures, paint sprites, or use `grounds.xml`. The DAT file is the source that maps Tibia client item ids to sprite ids and item flags.

## Legacy reference

- `remeres-map-editor-redux/source/item_definitions/formats/dat/dat_item_parser.cpp`
- `remeres-map-editor-redux/source/item_definitions/formats/dat/dat_catalog.h`
- `remeres-map-editor-redux/source/app/client_version.h`
- `remeres-map-editor-redux/source/item_definitions/asset_bundle_loader.cpp`

Legacy flow:

1. Read DAT signature and counts.
2. Parse item and creature entries from client id `100` through `item_count + creature_count`.
3. Keep item entries `100..item_count` for item definitions.
4. Use DAT format to decide compact (`u16`) or extended (`u32`) sprite id width.
5. Load SPR separately using the DAT catalog extended flag.

## Scope

In scope:

- Pure Python parser for DAT header and item sprite metadata.
- Compact and extended sprite id widths.
- Deterministic parse errors for invalid or truncated DAT data.
- `DatSpriteRecord` output compatible with `sprite_catalog_adapter.py`.
- Minimal flag support needed for safe metadata: ground flag and no-payload flags as named flags where possible.

Out of scope:

- Real client-version detection.
- Frame duration and frame group animation metadata.
- SPR archive decoding.
- Atlas texture construction.
- UI rendering or palette behavior.
- `grounds.xml` brush/material parsing.
