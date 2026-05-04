# M031/S02 - File Import Export Data Reports

Plan source: `docs/superpowers/plans/2026-05-01-m031-menu-functionality-gaps.md`

## Scope

- Import Map.
- Import Monsters/NPC.
- Export Minimap.
- Export Tilesets.
- Reload Data Files.
- Missing Items Report.

## Tasks

- [x] T01: failing tests for each remaining File gap.
- [x] T02: define injectable service seams for import/export/reload/report operations.
- [x] T03: implement behavior only where repo backend exists.
- [x] T04: document any still-deferred backend with exact missing dependency.
- [x] T05: closeout summary and state update.

## Files

- `pyrme/ui/main_window.py`
- `pyrme/rendering/client_asset_discovery.py`
- `pyrme/core_bridge.py`
- `tests/python/test_legacy_file_menu.py`

## Verification

`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py -q --tb=short`

## Stop Condition

S02 done when File data actions are tested as real behavior or explicitly documented with missing backend evidence.
