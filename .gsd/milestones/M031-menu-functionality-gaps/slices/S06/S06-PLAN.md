# M031/S06 - Map Cleanup Statistics

Plan source: `docs/superpowers/plans/2026-05-01-m031-menu-functionality-gaps.md`

## Scope

- Cleanup invalid tiles.
- Cleanup invalid zones.
- Statistics data bridge.
- Map Properties state persistence check.
- Town/House dialog regression check.
- Existing test hang: `map_statistics_action` opens a modal while legacy map test expects safe unavailable behavior.

## Tasks

- [ ] T01: failing tests for Map cleanup/statistics behavior.
- [ ] T02: add bridge surface for invalid tile/zone cleanup where core exposes data.
- [ ] T03: feed real map statistics into `MapStatisticsDialog`.
- [ ] T04: verify Map Properties, Town Manager, and House Manager remain wired.
- [ ] T05: closeout summary and state update.

## Files

- `pyrme/ui/main_window.py`
- `pyrme/core_bridge.py`
- `pyrme/ui/dialogs/map_statistics.py`
- `tests/python/test_legacy_map_menu.py`

## Verification

`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short`

## Stop Condition

S06 done when Map cleanup/statistics gaps are closed or documented with exact missing core data, and targeted Map tests pass.
