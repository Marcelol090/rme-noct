# M031/S06 Summary - Map Cleanup Statistics

## Done

- Added `MapStatisticsSnapshot` and `EditorModel.collect_statistics()`.
- Fed current `EditorModel` statistics into `MapStatisticsDialog` through an injectable dialog factory.
- Fixed the offscreen Map Statistics test hang by using the dialog seam in tests.
- Kept Cleanup invalid tiles/zones as exact deferred gaps because current `TileState` has no invalid item, unresolved item, invalid zone, or opaque OTBM fragment fields.
- Verified Map Properties, Town Manager, and House Manager still route through existing seams.

## Verification

- `QT_QPA_PLATFORM=offscreen timeout 30s rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short` -> baseline timed out after 2 tests before implementation.
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short` -> 7 passed.
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py tests/python/test_legacy_edit_menu.py tests/python/test_legacy_selection_menu.py -q --tb=short` -> 27 passed.
- `rtk python3 -m ruff check pyrme/editor/model.py pyrme/editor/__init__.py pyrme/ui/main_window.py pyrme/ui/dialogs/map_statistics.py tests/python/test_legacy_map_menu.py` -> passed.
- `rtk git diff --check` -> passed.

## Remaining Evidence Gaps

- Cleanup invalid tiles needs invalid item or unresolved item flags.
- Cleanup invalid zones needs invalid zone fields or opaque OTBM fragment state.
- Blocking/walkability statistics need tile property metadata; this slice reports current in-memory tiles as walkable and blocking as `0`.
