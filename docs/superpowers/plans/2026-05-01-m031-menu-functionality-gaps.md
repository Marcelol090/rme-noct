# M031 Menu Functionality Gaps - Plan

## Milestone

Close File/Edit/Selection/Map menu behavior gaps that are currently safe status messages.

## Slices

1. `S01-FILE-LIFECYCLE-RECENTS`
   - New, Open, Save, Save As, Close, Exit, Recent Files.
   - Files: `pyrme/ui/main_window.py`, `pyrme/ui/editor_context.py`, `pyrme/core_bridge.py`, `tests/python/test_legacy_file_menu.py`.

2. `S02-FILE-IMPORT-EXPORT-DATA-REPORTS`
   - Import Map, Import Monsters/NPC, Export Minimap, Export Tilesets, Reload Data Files, Missing Items Report.
   - Files: `pyrme/ui/main_window.py`, `pyrme/rendering/client_asset_discovery.py`, `pyrme/core_bridge.py`, `tests/python/test_legacy_file_menu.py`.

3. `S03-EDIT-HISTORY-CLIPBOARD`
   - Undo, Redo, Cut, Copy, Paste with selection-dependent enablement.
   - Files: `pyrme/editor/model.py`, `pyrme/ui/main_window.py`, `tests/python/test_legacy_edit_menu.py`.

4. `S04-EDIT-MAP-TRANSFORMS`
   - Replace Items, Borderize Selection/Map, Randomize Selection/Map, Remove/Clear options.
   - Files: `pyrme/editor/model.py`, `pyrme/ui/main_window.py`, `crates/rme_core/src/autoborder.rs`, `tests/python/test_legacy_edit_menu.py`.

5. `S05-SELECTION-OPERATIONS`
   - Replace/Find/Remove Item on Selection and Find on Selection filters.
   - Files: `pyrme/editor/model.py`, `pyrme/ui/main_window.py`, `tests/python/test_legacy_selection_menu.py`.

6. `S06-MAP-CLEANUP-STATISTICS`
   - Cleanup invalid tiles/zones and statistics data bridge; keep Town/House dialogs green.
   - Files: `pyrme/ui/main_window.py`, `pyrme/core_bridge.py`, `pyrme/ui/dialogs/map_statistics.py`, `tests/python/test_legacy_map_menu.py`.

## Known Verification Gap

- `test_legacy_map_menu.py::test_map_backend_gap_actions_are_safe_until_backend_exists` currently hangs under `QT_QPA_PLATFORM=offscreen` because `map_statistics_action` opens `MapStatisticsDialog.exec()` while the test still expects a safe unavailable message.

## Verification

- Per slice: targeted test file first.
- Milestone closeout: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py tests/python/test_legacy_edit_menu.py tests/python/test_legacy_selection_menu.py tests/python/test_legacy_map_menu.py -q --tb=short`
- Before PR: `python3 -m pytest tests/python/ -q --tb=short`
