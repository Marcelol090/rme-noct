# M031/S01 - File Lifecycle Recents

Plan source: `docs/superpowers/plans/2026-05-01-m031-menu-functionality-gaps.md`

## Scope

- New map action creates a fresh editor context.
- Open action uses an injectable file path seam and loads through existing bridge where available.
- Save and Save As use existing save bridge where available.
- Close clears current document with dirty-state guard.
- Exit routes through the same close guard.
- Recent Files submenu is populated from settings and can trigger open.

## Tasks

- [x] T01: failing tests for File New/Open/Save/Save As/Close/Exit/Recent Files behavior.
- [x] T02: minimal file-service seam for dialogs and paths.
- [x] T03: wire File lifecycle actions in `MainWindow`.
- [x] T04: populate and trigger Recent Files.
- [x] T05: closeout summary and state update.

## Files

- `pyrme/ui/main_window.py`
- `pyrme/ui/editor_context.py`
- `pyrme/core_bridge.py`
- `tests/python/test_legacy_file_menu.py`

## Verification

`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_legacy_file_menu.py -q --tb=short`

## Stop Condition

S01 done when lifecycle actions no longer use `_show_unavailable`, recent files are tested, and targeted File menu tests pass.
