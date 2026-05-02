# M031/S05 - Selection Operations

Plan source: `docs/superpowers/plans/2026-05-01-m031-menu-functionality-gaps.md`

## Scope

- Replace Items on Selection.
- Find Item on Selection.
- Remove Item on Selection.
- Find Everything/Unique/Action/Container/Writeable on Selection.

## Tasks

- [ ] T01: failing tests for each Selection menu operation.
- [ ] T02: add selection-scoped item search helpers.
- [ ] T03: add selection-scoped replace/remove helpers.
- [ ] T04: wire Selection actions in `MainWindow`.
- [ ] T05: closeout summary and state update.

## Files

- `pyrme/editor/model.py`
- `pyrme/ui/main_window.py`
- `tests/python/test_legacy_selection_menu.py`

## Verification

`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short`

## Stop Condition

S05 done when Selection actions perform tested selected-area behavior and targeted Selection tests pass.
