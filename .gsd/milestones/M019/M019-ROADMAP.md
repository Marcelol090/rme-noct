# M019 Roadmap - DAT item metadata

## Goal

Parse item-to-sprite metadata from DAT files so discovered client asset bundles can produce sprite catalog records before any SPR pixel decoding work starts.

## Slices

### S01 - Parser and catalog records

Build a narrow, tested Python parser that reads DAT bytes or a DAT path and emits `DatSpriteRecord` rows for item client ids.

Acceptance:

- Header counts and signature are exposed.
- Item ids start at `100` and stop at `item_count`.
- Creature entries are consumed for stream alignment but excluded from item records by default.
- Compact and extended sprite id widths are supported.
- Ground flag payload is skipped and represented as a record flag.
- Invalid counts, short data, zero dimensions, and excessive sprite counts fail with deterministic errors.

Deferred:

- Automatic DAT format detection.
- SPR validation against parsed sprite ids.
- Pixel/atlas/render integration.
