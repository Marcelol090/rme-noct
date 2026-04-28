# M006 Context - Item palette

## Why

The brush palette `Item` tab was still a placeholder list. The editor needs a search-first, model/view item palette that can scale to large catalogs without blocking the UI.

## Contract

- Keep the existing `BrushPaletteDock` shell and public palette navigation methods stable.
- Replace only the `Item` tab internals with a real widget backed by Qt models.
- Keep item selection as an honest shell seam through `EditorContext.session.active_item_id`.
- Do not claim sprite rendering, full item database loading, or full brush backend activation in this milestone.

## Source Docs

- `SPEC.md`
- `PLAN.md`
- `AGENTS.md`
