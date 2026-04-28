# M007 — Sprite Frame Metadata Roadmap

| Slice | Status | Goal |
|---|---|---|
| S01 — CANVAS-80-SPR-FRAME-METADATA | Complete | Attach SPR-like frame metadata to `SpriteCatalog` entries without parsing files or drawing sprites. |

## Stop Condition

Stop after tests prove SPR-like frame records attach deterministic metadata to matching catalog entries by `sprite_id`. Do not add SPR file parsing, texture atlas loading, real image drawing, screenshots, or `wgpu` work in this milestone.
