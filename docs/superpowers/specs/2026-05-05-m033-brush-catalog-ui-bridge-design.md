# M033 Brush Catalog UI Bridge Design

## Problem

GitHub issue #72 keeps Phase 3 focused on brush engine and toolset work. M029 added the Rust brush catalog contract and M030 added pure autoborder planning, but the PyQt shell still shows placeholder brush names in non-Item palette tabs. Users cannot select a real terrain or wall brush through the palette, and `Jump to Brush` still mixes palette-page shortcuts with item-backed results only.

## Approved Scope

Create the first UI bridge from the existing brush catalog contract to the shell. This slice makes brush catalog entries visible and selectable in the `BrushPaletteDock`, updates active brush/session/canvas state when a catalog brush is selected, and lets `Jump to Brush` reuse the same local catalog source.

## Architecture

Add a small Python-side catalog view model under `pyrme/ui/models/brush_catalog.py`. It mirrors the stable subset from `crates/rme_core/src/brushes.rs` until the native PyO3 catalog is exposed, keeping fields explicit: `brush_id`, `name`, `kind`, `palette_name`, `look_id`, `related_item_ids`, `visible_in_palette`, and `active_brush_id`.

`BrushPaletteDock` will load non-Item tabs from `BrushPaletteEntry` values instead of generated placeholders. The dock emits a new `brush_selected` signal for catalog brushes while keeping `item_selected` unchanged for the Item tab.

`MainWindow` will connect `brush_selected` to the existing active brush state and canvas sync path. This slice activates the brush but does not apply brush placement commands to the map; map mutation stays in a later Ground/Wall Brushes apply slice.

`FindBrushDialog` will reuse the same default brush entries so search results and palette tabs do not diverge.

## Data Flow

1. `default_brush_palette_entries()` returns deterministic Terrain and Wall entries from the M029 brush contract fixtures.
2. `BrushPaletteDock` groups visible entries by `palette_name` and loads each group into its `VirtualBrushModel`.
3. Selecting a non-Item row emits `BrushPaletteEntry`.
4. `MainWindow._handle_brush_palette_selection()` sets `_active_brush_name`, `_active_brush_id`, clears `_active_item_id`, updates `EditorContext.session.active_brush_id`, and calls `_sync_canvas_shell_state()`.
5. `FindBrushDialog` maps each entry to `FindBrushResult(kind="brush", palette_name=..., brush_id=...)`.

## Non-Goals

- No renderer or sprite drawing changes.
- No minimap generation.
- No Search menu changes.
- No full XML brush loader.
- No PyO3 export of `BrushCatalog`.
- No map mutation for catalog brush placement.
- No autoborder preview or recalculation.

## Testing

- Unit tests for `BrushPaletteEntry`, default catalog grouping, search text, and active id format.
- Dock tests proving Terrain/Wall tabs use catalog names, no placeholder names remain, search filters catalog entries, and selection emits `brush_selected`.
- MainWindow tests proving catalog brush selection drives active shell/canvas state without setting `active_item_id`.
- FindBrushDialog tests proving dialog results include catalog brush entries and preserve existing item/palette behavior.
- Guard tests for existing Item palette, Jump to Item, and legacy Search menu.

## Verification Commands

Use WSL/rtk:

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py tests/python/test_item_palette_integration.py tests/python/test_find_brush_tier2.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_legacy_search_menu.py -q --tb=short
PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/models/brush_catalog.py pyrme/ui/docks/brush_palette.py pyrme/ui/dialogs/find_brush.py pyrme/ui/main_window.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_find_brush_tier2.py tests/python/test_item_palette_integration.py
git diff --check
PATH="/home/marcelo/.local/bin:$PATH" rtk npm run preflight --silent
```

Rust baseline stays useful but this UI slice should not require Rust code changes:

```bash
PY312="/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu"
PYO3_PYTHON="$PY312/bin/python3.12" LD_LIBRARY_PATH="$PY312/lib:${LD_LIBRARY_PATH:-}" RUSTFLAGS="-L native=$PY312/lib -l dylib=python3.12" PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core brushes --quiet
```
