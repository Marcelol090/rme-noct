# M006 — Sprite Catalog DAT Adapter Context

## Goal

Add the first adapter seam that can feed DAT-like item sprite records into the renderer-facing `SpriteCatalog`.

## Current State

- `CANVAS-60-SPRITE-CATALOG-SEAM` defines `SpriteCatalog`, `SpriteCatalogEntry`, and `build_sprite_frame`.
- The renderer can distinguish resolved and unresolved item ids.
- No real DAT parser, SPR parser, atlas loader, or sprite painting exists in this slice.

## Boundary

`S01 / CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` converts in-memory DAT-like records into `SpriteCatalog` entries. It does not parse files or connect real client asset archives.

## Decisions

- The adapter owns DAT-facing record metadata.
- Renderer frame planning must not import DAT adapter modules.
- Metadata is allowed on catalog entries, but `build_sprite_frame` remains metadata-agnostic.
