# M006 Roadmap - Item palette

## S01 - ITEM-10-MODEL-VIEW-PALETTE

Materialize the search-first Item palette inside `BrushPaletteDock`:

- immutable item/category/query data contracts
- cached item catalog and result model
- category rail model
- `ItemPaletteWidget` with result count, empty state, category rail, and result list view
- dock search delegation and selection seam
- tests for model, dock, integration, and 50k-item performance assumptions

## Follow-up

Next slice should target brush activation backend:

- consume `EditorContext.session.mode`
- consume `EditorContext.session.active_item_id`
- route selected item state into canvas/editor activation seams

Non-goals remain real draw behavior, sprite rendering in the palette, and UI redesign of unrelated tabs.
