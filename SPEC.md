# Instant Item Palette Spec

## Summary

Replace the current mock `Item` tab in the brush palette dock with a real, model-based item palette optimized for fast selection from a large catalog.

The palette should make the primary task obvious: find and select an item quickly. Category navigation and advanced filtering are secondary and should be progressively disclosed rather than competing with search.

This slice is planning-only. No code is included here.

## Problem

The current brush palette in `pyrme/ui/docks/brush_palette.py` is still a placeholder:
- `QTabWidget` with one `QListWidget` per palette
- mock entries only
- no instant search
- no virtualization
- no category structure beyond top-level tabs

That shape will not scale to `50k+` items and does not align with the actual editor need: fast item lookup with low cognitive load.

There is useful prior art in `pyrme/ui/dialogs/find_item.py`:
- local search/query objects
- result-mode patterns
- filter vocabulary
- consistent spacing/layout language

But that dialog still uses `QListWidget` rebuilds, which is acceptable for a dialog seam but not for a persistent high-volume dock.

## User Goal

Select an item as quickly as possible, usually by typing part of its name or narrowing to a category.

## Fastest Path

1. Focus the `Item` palette.
2. Type in the search field.
3. See results update immediately without UI hitching.
4. Confirm the intended item visually/textually.
5. Select it and make it the active brush/item.

## UI Intent

Apply `ui-system-discipline` directly:

- Primary:
  - search input
  - result list/view
  - current result count
- Secondary:
  - category tree / category chips / category selector
  - optional result mode control if justified
- Tertiary:
  - advanced filters
  - metadata/details preview
  - low-frequency controls

The dock should not look like a generic tab full of controls. Search must dominate the scan path. Categories should help when needed, not compete with search.

## Scope

### In scope

- Materialize a real `Item` palette inside the existing brush palette dock.
- Replace the current mock item list with a model/view implementation.
- Add instant text search that does not freeze the UI on large catalogs.
- Add category drill-down with progressive disclosure.
- Add result caching for repeated queries.
- Keep spacing/token discipline consistent with the repo direction:
  - spacing based on 8pt rhythm
  - primary text at 14 where appropriate
- Add tests for model behavior, dock behavior, and search interaction seams.
- Keep integration narrow enough to fit the current repo slice style.

### Out of scope

- Full item sprite rendering pipeline.
- Server-backed or on-disk item database loading if the repo does not already have it.
- Full advanced filter parity with every legacy item property in the first slice.
- Heavy editor-side behavior beyond item selection seams.
- Reworking the entire palette system for Terrain, Doodad, Creature, etc.
- Replacing the existing `Find Item` dialog in this slice.

## Non-Goals

- Do not implement all palette tabs with the new architecture in one pass.
- Do not introduce a custom paint-heavy widget unless the default Qt model/view path proves insufficient.
- Do not keep the current "tab with a plain list and lots of visible controls" structure for the `Item` tab.
- Do not rebuild all results into `QListWidgetItem`s on every keystroke.

## Proposed UX

## Item Palette Structure

Within the `Item` tab, the dock should be split into two functional areas:

### 1. Search-first header

Visible immediately at the top:
- search field
- result count
- optional small mode toggle only if justified

This is the dominant action area.

### 2. Body with progressive disclosure

Two-pane structure preferred:

- left: compact category tree/filter rail
- right: virtualized result view

Behavior:
- when search is empty, categories are the main narrowing mechanism
- when search has text, result view becomes dominant and category context is secondary
- categories stay available but visually demoted

This matches the editor need: quick lookup first, browse second.

## View Choice

Preferred structure:
- `QTreeView` for categories
- `QListView` for results
- model-based approach for both

Why:
- `QListView` is the cleaner fit for a flat result set with a large backing model
- categories are structurally different from results and should not be forced into a single noisy tree
- this keeps the primary action obvious

Alternative acceptable fallback:
- a single `QTreeView` with collapsible categories and leaf items

This fallback is simpler but weaker for search-first UX because search results and hierarchy compete in the same surface.

Recommendation:
- category tree + result list as the main design

## Performance Requirements

For `50k+` items:
- typing in search must not visibly freeze the UI
- no full widget recreation per keystroke
- filtering must operate on model data, not per-item widgets
- repeated identical queries should reuse cached result sets
- search updates should be debounced lightly if needed, but should still feel instant

Target implementation characteristics:
- normalized search index precomputed once
- filter pipeline works on immutable/lightweight row records
- result cache keyed by normalized query + category selection
- view only asks the model for visible rows

## Data Model Proposal

Introduce a dedicated item palette catalog layer separate from the widget layer.

Suggested data objects:
- `ItemPaletteEntry`
  - stable id
  - name
  - normalized_name
  - category path / category id
  - optional client/server ids
  - optional flags/metadata
- `ItemPaletteQuery`
  - search_text
  - selected_category
  - optional mode/filter flags

Suggested components:
- `ItemPaletteCatalog`
  - owns full immutable dataset
  - builds normalized search/index data
- `ItemPaletteResultCache`
  - caches row id lists for query keys
- `ItemPaletteListModel`
  - serves visible results to `QListView`
- `ItemCategoryTreeModel`
  - serves category hierarchy
- optional controller/presenter seam to bind query state to models

## Interaction Requirements

- Search updates as the user types.
- Empty search shows category-driven browsing.
- Non-empty search shows filtered results immediately.
- Clicking a category narrows browse mode and search scope.
- Selecting a result updates the current palette selection seam.
- Keyboard-first path must work:
  - focus search
  - type
  - arrow down
  - enter/select

## Empty / Loading / Disabled States

Even if the first slice uses a local/static catalog, the UI contract should still define these states:

- Empty:
  - no results for current query
  - clear message with current search/category context
- Loading:
  - if catalog population becomes async later, preserve layout and show a lightweight loading state
- Disabled:
  - if item catalog unavailable, show a disabled palette message instead of a broken blank list

## Visual Rules

Use the existing dock shell and make the internal hierarchy clearer.

- spacing:
  - outer margins: 8
  - vertical rhythm: 8
  - section separation: 16
- typography:
  - search/result primary labels: 14
  - secondary metadata/count labels: smaller, visually demoted
- states:
  - hover
  - selected
  - focus
  - disabled
- structure before decoration:
  - do not add visual chrome to compensate for unclear grouping

## Integration Notes

Likely integration point:
- `pyrme/ui/docks/brush_palette.py`

Likely supporting modules to introduce:
- `pyrme/ui/docks/item_palette.py`
- `pyrme/ui/models/item_palette_model.py`
- `pyrme/ui/models/item_category_model.py`
- `pyrme/ui/models/item_palette_types.py`

These names are suggestions, not mandates. The key requirement is to separate:
- catalog/index/query logic
- Qt models
- widget composition

`MainWindow` should remain a light mount point:
- still constructs `BrushPaletteDock`
- item selection should flow through an explicit seam rather than hidden widget-only state

## Repo-Specific Assumptions

- `BrushPaletteDock` will remain the mounted dock from `pyrme/ui/main_window.py`.
- The first implemented real palette is `Item`; other tabs can remain stubbed for now.
- Existing `FindItemResult` / query vocabulary may be partially reusable conceptually, but not copied blindly if it would drag `QListWidget` assumptions into the dock.
- There is no existing virtualized item palette implementation in the repo yet.
- Tests should follow the current repo pattern under `tests/python/`.

## Risks

- Reusing too much of `FindItemDialog` could lock the dock into non-scalable widget patterns.
- A naive `QSortFilterProxyModel` over expensive string operations may still be too slow at `50k+` rows if normalization/indexing is not precomputed.
- If category counts are recomputed on every keystroke without care, the left rail may become the actual performance bottleneck.
- If the result view includes heavy delegates or real-time icon work too early, it will undermine the search performance target.

## What Should Be Verified With Context7

Not blocking for planning, but should be verified before implementation if uncertainty remains:

- best-fit Qt model/view API choice for large flat searchable datasets:
  - `QAbstractListModel` vs `QStandardItemModel`
- whether `QSortFilterProxyModel` is sufficient here or whether a custom filtered model is safer for caching/query control
- recommended Qt patterns for incremental filtering / large model responsiveness in PyQt6
- any caveats around `QListView` performance with custom delegates and `uniformItemSizes`

## Acceptance Criteria

- `Item` tab is no longer a mock `QListWidget`.
- Search is the dominant control in the `Item` palette.
- Results are backed by a model/view implementation.
- Filtering large catalogs does not freeze the UI in normal use.
- Categories are available but secondary to search.
- Query results are cached and reused for repeated searches.
- Tests cover:
  - query matching / caching behavior
  - category narrowing behavior
  - dock-level interaction and selection seam
  - empty-state behavior
