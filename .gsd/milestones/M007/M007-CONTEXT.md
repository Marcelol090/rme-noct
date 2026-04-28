# M007 — Sprite Frame Metadata Context

## Goal

Attach SPR-like frame metadata to `SpriteCatalog` entries through the existing adapter seam.

## Current State

- `CANVAS-60-SPRITE-CATALOG-SEAM` provides `SpriteCatalog` and `build_sprite_frame`.
- `CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` converts DAT-like item records into catalog entries.
- No real SPR file parser, pixel decoder, atlas loader, or tile sprite draw path exists yet.

## Boundary

`S01 / CANVAS-80-SPR-FRAME-METADATA` adds in-memory SPR-like frame records and deterministic metadata attachment by `sprite_id`. It does not load binary SPR files or image bytes.

## Decisions

- SPR metadata remains adapter-owned.
- Metadata stores frame dimensions, offsets, and frame indexes only.
- Atlas placement and real draw commands remain separate follow-on work.
