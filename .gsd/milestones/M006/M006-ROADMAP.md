# M006 — Sprite Catalog DAT Adapter Roadmap

| Slice | Status | Goal |
|---|---|---|
| S01 — CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER | Complete | Convert DAT-like item sprite records into `SpriteCatalog` entries without importing DAT concerns into frame planning. |

## Stop Condition

Stop after tests prove DAT-like records produce usable `SpriteCatalog` entries and unresolved IDs still flow through `build_sprite_frame`. Do not add DAT/SPR file parsing, atlas loading, real image drawing, screenshots, or `wgpu` work in this milestone.
