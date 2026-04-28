# S01: ITEM-10-MODEL-VIEW-PALETTE

**Goal:** Replace the placeholder `Item` palette tab with a search-first model/view palette that scales to large catalogs and exposes an honest selection seam.

**Demo:** Opening the brush palette, selecting `Item`, typing in the dock search box, and selecting a row filters model-backed results and updates the shell active item state.

## Must-Haves

- Keep `palette_names()`, `select_palette()`, and `current_palette()` stable.
- Add immutable item/category/query data contracts.
- Cache repeated catalog queries and clear cache on catalog replacement.
- Use model/view widgets for result and category lists.
- Route selected items through an explicit dock signal.
- Cover model, widget, dock integration, and performance assumptions in tests.

## Non Goals

- No real sprite drawing or icons.
- No DAT/SPR catalog loading.
- No full brush activation backend.
- No UI redesign of other palette tabs.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_item_palette_model.py tests/python/test_item_palette_dock.py tests/python/test_item_palette_integration.py tests/python/test_item_palette_perf.py tests/python/test_brush_palette_perf.py -q --tb=short`
- `.\.venv\Scripts\python.exe -m ruff check pyrme/ui/docks/brush_palette.py pyrme/ui/docks/item_palette.py pyrme/ui/models/item_palette_types.py pyrme/ui/models/item_palette_model.py pyrme/ui/models/item_category_model.py tests/python/test_item_palette_model.py tests/python/test_item_palette_dock.py tests/python/test_item_palette_integration.py tests/python/test_item_palette_perf.py tests/python/test_brush_palette_perf.py`
- `npm run preflight --silent`

## Tasks

- [x] **T01: Define item palette data/model seam** `est:20m`
  - Files: `pyrme/ui/models/item_palette_types.py`, `pyrme/ui/models/item_palette_model.py`, `pyrme/ui/models/item_category_model.py`, `tests/python/test_item_palette_model.py`
  - Done when: query matching, category narrowing, cache hits, and empty results are covered.

- [x] **T02: Build ItemPaletteWidget** `est:20m`
  - Files: `pyrme/ui/docks/item_palette.py`, `tests/python/test_item_palette_dock.py`
  - Done when: widget loads items, filters via public search API, narrows by category, emits selected item, and shows empty state.

- [x] **T03: Integrate BrushPaletteDock seam** `est:20m`
  - Files: `pyrme/ui/docks/brush_palette.py`, `tests/python/test_item_palette_integration.py`
  - Done when: Item tab mounts the new widget, dock search delegates to it, selection is re-emitted, and other tabs remain reachable.

- [x] **T04: Validate scale and shell regressions** `est:20m`
  - Files: `tests/python/test_item_palette_perf.py`, `tests/python/test_brush_palette_perf.py`
  - Done when: 50k load/search/category/cache assumptions and adjacent brush-palette behavior pass.

- [x] **T05: Gap fix and closeout** `est:10m`
  - Files: `pyrme/ui/docks/item_palette.py`, `tests/python/test_item_palette_dock.py`, `.gsd/milestones/M006-item-palette/slices/S01/S01-SUMMARY.md`
  - Done when: caveman-review gap is fixed, score is green, and summary records real verification.

## Closeout

S01 is complete when the Item tab is model-backed, search-first, cached, tested, and still honest about remaining backend/rendering gaps.
