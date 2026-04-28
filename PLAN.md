# Item Palette Implementation Plan

## Slice Goal

Materialize a real `Item` palette inside the brush palette dock using a model/view approach that scales to large catalogs and prioritizes instant search.

## Working Strategy

Implement this as one focused vertical slice:
- keep the existing dock shell
- replace only the `Item` tab internals
- introduce a clean catalog/model/query seam
- leave other palette tabs untouched for now

Do not start by styling. Start by fixing structure and data flow.

## Assumptions

- We can add small new modules under `pyrme/ui/docks/` and `pyrme/ui/models/`.
- A local/static catalog fixture is acceptable for the first integrated slice if the real backend is not yet available.
- The active-item selection can initially terminate at an honest seam in the dock/main-window layer if the full editor brush backend is not ready.

## Non-Goals For This Plan

- Full icon/sprite rendering
- Full legacy parity for all palette types
- Replacing `Find Item` dialog
- Deep map/editor backend integration beyond a clean selection seam

## File Targets

Likely files to touch:
- `pyrme/ui/docks/brush_palette.py`
- `pyrme/ui/main_window.py`

Likely files to add:
- `pyrme/ui/docks/item_palette.py`
- `pyrme/ui/models/item_palette_types.py`
- `pyrme/ui/models/item_palette_model.py`
- `pyrme/ui/models/item_category_model.py`

Likely tests to add:
- `tests/python/test_item_palette_model.py`
- `tests/python/test_item_palette_dock.py`

Possible existing tests to update:
- `tests/python/test_legacy_navigate_window_shell.py`

## Task Breakdown

### T01 - Audit current dock contract
Time: 2-5 min

- Read `pyrme/ui/docks/brush_palette.py`
- Confirm current public contract that must remain stable:
  - `palette_names()`
  - `select_palette()`
  - `current_palette()`
- Note where the `Item` tab can be swapped without breaking the rest of the dock

Output:
- stable dock contract identified
- tab replacement boundary confirmed

### T02 - Define item palette data shapes
Time: 2-5 min

- Create plan-level schema for:
  - item entry
  - category node reference
  - query object
  - cache key
- Keep fields minimal and explicit

Likely file:
- `pyrme/ui/models/item_palette_types.py`

Output:
- lightweight immutable data contract for palette logic

### T03 - Design category/result layout
Time: 2-5 min

- Lock the UI structure before code:
  - search-first header
  - left category rail
  - right result list
- Decide what is visible immediately vs deferred
- Confirm spacing rhythm and 14px-equivalent typography use

Likely file:
- `pyrme/ui/docks/item_palette.py`

Output:
- final widget hierarchy for the `Item` tab

### T04 - Build catalog/index layer
Time: 2-5 min

- Add a catalog object that owns the full dataset
- Precompute normalized search text
- Precompute category membership
- Keep this layer Qt-light or Qt-free where practical

Likely file:
- `pyrme/ui/models/item_palette_model.py`

Output:
- reusable catalog/index primitive ready for filtering

### T05 - Add query key + result cache
Time: 2-5 min

- Define normalized cache keys from:
  - search text
  - category selection
  - optional mode/filter bits
- Cache filtered row ids or entry refs
- Keep cache invalidation simple: clear on catalog replacement

Likely file:
- `pyrme/ui/models/item_palette_model.py`

Output:
- repeated queries avoid redundant recomputation

### T06 - Implement result list model
Time: 2-5 min

- Create a `QAbstractListModel`-based result model
- Feed it filtered entry refs rather than widget items
- Support the display roles required by the view

Likely file:
- `pyrme/ui/models/item_palette_model.py`

Output:
- virtualized result model for `QListView`

### T07 - Implement category model
Time: 2-5 min

- Create the category model for the left rail
- Support parent/child category drill-down or compact hierarchy
- Keep category selection secondary to search

Likely file:
- `pyrme/ui/models/item_category_model.py`

Output:
- browsable category structure with stable ids

### T08 - Add item palette widget shell
Time: 2-5 min

- Build the dedicated `ItemPaletteWidget`
- Add:
  - search field
  - result count
  - category view
  - result list view
  - empty-state label/surface
- Use 8pt spacing and 14pt-primary typography decisions consistently

Likely file:
- `pyrme/ui/docks/item_palette.py`

Output:
- real widget shell with clear hierarchy

### T09 - Wire query interactions
Time: 2-5 min

- Connect search changes to model query updates
- Connect category selection to query updates
- Ensure result count and empty state refresh correctly
- Keep the update pipeline deterministic and cheap

Likely file:
- `pyrme/ui/docks/item_palette.py`

Output:
- working query flow from controls to results

### T10 - Add selection seam
Time: 2-5 min

- Define what happens when a result is selected
- Route it through an explicit seam instead of hidden widget state
- Keep the seam honest if backend brush activation is not ready

Likely files:
- `pyrme/ui/docks/item_palette.py`
- `pyrme/ui/docks/brush_palette.py`
- `pyrme/ui/main_window.py`

Output:
- selection path ready for later editor integration

### T11 - Replace only the Item tab internals
Time: 2-5 min

- Keep existing `QTabWidget` outer shell for now
- Swap the current mock `Item` page for the new widget
- Leave Terrain/Doodad/etc. unchanged in this slice

Likely file:
- `pyrme/ui/docks/brush_palette.py`

Output:
- narrow integration with low regression risk

### T12 - Add model tests
Time: 2-5 min

- Test query matching
- Test category narrowing
- Test cache hit behavior for repeated queries
- Test empty-result behavior

Likely file:
- `tests/python/test_item_palette_model.py`

Output:
- logic coverage independent of widget layer

### T13 - Add widget/dock tests
Time: 2-5 min

- Test that the `Item` tab mounts the new palette widget
- Test search field updates visible results
- Test category click narrows results
- Test selection seam fires
- Test empty state appears correctly

Likely file:
- `tests/python/test_item_palette_dock.py`

Output:
- UI contract coverage for the new palette

### T14 - Update existing shell test expectations
Time: 2-5 min

- Confirm current window/dock tests still pass
- Adjust only expectations that depended on the old mock list behavior
- Preserve existing dock visibility/tab switching contract

Likely file:
- `tests/python/test_legacy_navigate_window_shell.py`

Output:
- no accidental regression in existing dock/menu shell tests

### T15 - Validate performance assumptions
Status: done
Time: 2-5 min

- Use a large synthetic dataset in tests or a local harness
- Confirm search updates stay responsive in the expected path
- If needed, tighten the cache/index strategy before adding more UI features

Validated:
- `load_items()` 50k: `5.165 ms` measured in direct API path
- `set_search_text()` worst-case: `3.020 ms`
- category switch: `0.581 ms`
- repeated cache hit: `0.002 ms`
- verification: `pytest tests/python/test_item_palette_perf.py -v --tb=short`

Likely files:
- `tests/python/test_item_palette_model.py`

Output:
- evidence that the slice is viable for `50k+` scale

## Test Strategy

### Unit/model tests
Focus on:
- search normalization
- cache keys
- repeated query reuse
- category narrowing
- empty results

### Widget tests
Focus on:
- dominant search control exists
- result view is model-based
- category rail is secondary but functional
- selection works via seam
- no `QListWidget` rebuild path in the new `Item` palette

### Regression tests
Confirm:
- brush palette dock still mounts from `MainWindow`
- tab switching still works
- legacy menu/window shell behavior is preserved

## Context7 Verification Checklist

Read root `AGENTS.md` before implementation; it is the repo contract that scopes the slice.
Use Context7 during implementation if needed for:
- `QAbstractListModel` best practices in PyQt6
- `QSortFilterProxyModel` tradeoffs vs custom filtering model
- `QListView` performance-related properties:
  - `uniformItemSizes`
  - delegate cost
  - update patterns
- any model/view caveat that affects `50k+` rows

This is verification work, not a blocker to starting the slice.

## Execution Order Recommendation

1. Lock data/query shapes
2. Build catalog + cache
3. Build result model
4. Build widget shell
5. Wire interactions
6. Integrate into `BrushPaletteDock`
7. Add tests
8. Validate with large synthetic dataset

## Done Criteria

The slice is done when:
- `Item` tab uses a real model/view palette
- search is primary and instant-feeling
- categories are progressive disclosure, not dominant clutter
- repeated queries are cached
- tests cover logic and dock integration
- existing brush palette shell behavior remains intact

## Follow-up Slice

The next slice is `brush activation backend`.

Scope:
- consume `EditorContext.session.mode`
- consume `EditorContext.session.active_item_id`
- consume `EditorContext.session.active_brush_id`
- route shell-selected brush state into real canvas/editor activation seams

Non-goals:
- fake drawing behavior
- hidden mirror state outside `EditorContext.session`
- UI redesign of the palette or toolbars
