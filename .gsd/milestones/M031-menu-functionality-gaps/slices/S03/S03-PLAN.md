# M031/S03 - Edit History Clipboard

Plan source: `docs/superpowers/plans/2026-05-01-m031-menu-functionality-gaps.md`

## Scope

- Undo and Redo.
- Cut, Copy, Paste.
- Selection-dependent enablement.
- Minimal in-memory copy buffer for current `MapModel`.

## Tasks

- [x] T01: failing tests for undo/redo stack and clipboard action state.
- [x] T02: add minimal command history to `EditorModel`.
- [x] T03: add minimal copy buffer operations for selected positions.
- [x] T04: wire Edit actions in `MainWindow`.
- [x] T05: closeout summary and state update.

## Files

- `pyrme/editor/model.py`
- `pyrme/ui/main_window.py`
- `tests/python/test_legacy_edit_menu.py`

## Verification

`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short`

## Stop Condition

S03 done when Undo/Redo/Cut/Copy/Paste no longer report unavailable for supported in-memory map operations and targeted Edit tests pass.
