---
name: pyrme-file-formats
description: Use when working with OTBM, OTB, DAT, SPR, or appearances.dat file parsing. Covers both ServerID (OTBM 1-4) and ClientID (OTBM 5/6) formats, sprite hash computation, and cross-instance clipboard serialization.
---

# PyRME File Format Skill

## Supported Formats

| Format | Versions | ID System | Purpose |
|--------|----------|-----------|---------|
| OTBM | v2, v3, v4 | ServerID | Traditional map format |
| OTBM | v5, v6 | ClientID | Modern map format (Canary) |
| OTB | items.otb | Both | Item definitions + ID mappings |
| DAT | Tibia.dat | ClientID | Client item/sprite metadata |
| SPR | Tibia.spr | Sprite index | Raw sprite pixel data |
| appearances.dat | Protobuf | ClientID | Modern client appearances |
| OTMM | minimap | N/A | Minimap export format |

## ID Systems

### ServerID (Traditional)
- Defined in `items.otb`
- Unique per-item on server
- Maps (OTBM 1-4) store ServerIDs
- Server translates to ClientID for client display

### ClientID (Modern)
- Defined in `Tibia.dat` / `appearances.dat`
- ID used by client for sprite rendering
- Maps (OTBM 5/6) store ClientIDs directly
- ClientID = ServerID (unified system)

### ID Translation Flow (from C++)

```
Loading OTBM 5/6: ClientID → ServerID via items.otb
Editing: Always use ServerIDs internally
Saving OTBM 5/6: ServerID → ClientID via items.otb
```

Key class: `ItemIdMapper` (builds bidirectional maps at startup)

## Sprite Hash Matching

```
Algorithm: FNV-1a 64-bit
Input: Raw RGBA pixel data from .spr
Output: u64 hash fingerprint

Match Results:
  EXACT_MATCH  → Same item ID, same sprite
  HASH_MATCH   → Different ID, same sprite pixels
  NO_MATCH     → Sprite not found in target
  COLLISION    → Multiple items share hash (rare)
```

## Reference Implementation

Legacy C++ files:
- `source/io/` — All file I/O parsers
- `source/item_definitions/` — OTB/item type handling
- `source/assets/` — SPR/DAT loading
- `source/editor/copybuffer.cpp` — Clipboard serialization

## Rust Implementation Target

```
crates/rme_core/src/
├── io/
│   ├── otbm.rs          # OTBM v2-v6 read/write
│   ├── otb.rs           # items.otb parser
│   ├── dat.rs           # Tibia.dat parser
│   ├── spr.rs           # Sprite pixel loader
│   ├── appearances.rs   # appearances.dat (protobuf)
│   └── minimap.rs       # OTMM export
├── game/
│   ├── item_id_mapper.rs # ServerID ↔ ClientID
│   └── sprite_hash.rs    # FNV-1a hash database
└── editor/
    └── clipboard.rs      # Cross-instance serialization
```
