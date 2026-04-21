# M006 Summary - Item palette model/view seam

## Result

M006 replaced the placeholder `Item` tab with a search-first model/view palette:

- `ItemCatalog`, `QueryKey`, and Qt list models provide cached filtering and category narrowing.
- `ItemPaletteWidget` owns the Item tab internals and exposes an explicit `item_selected` signal.
- `BrushPaletteDock` keeps the outer tab shell stable while delegating search into the Item palette.
- Selection flows through the dock/main-window seam without claiming full brush backend activation.

## Verification

- `.\.venv\Scripts\python.exe -m ruff check pyrme/ui/docks/brush_palette.py pyrme/ui/docks/item_palette.py pyrme/ui/models/item_palette_types.py pyrme/ui/models/item_palette_model.py pyrme/ui/models/item_category_model.py tests/python/test_item_palette_model.py tests/python/test_item_palette_dock.py tests/python/test_item_palette_integration.py tests/python/test_item_palette_perf.py tests/python/test_brush_palette_perf.py` - passed.
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_item_palette_model.py tests/python/test_item_palette_dock.py tests/python/test_item_palette_integration.py tests/python/test_item_palette_perf.py tests/python/test_brush_palette_perf.py -q --tb=short` - passed, 49 tests.
- `.\.venv\Scripts\python.exe -m pytest tests/python/ -q --tb=short` - passed, 261 tests.
- `npm run preflight --silent` - passed.
- `npm run gsd:status --silent` - passed in degraded filesystem mode.
- Superpowers progress score - green, `Progressing well`.

## Blockers

- Publish/rebase remains blocked by dirty divergent branch state. Stage only M006 scope before committing.
