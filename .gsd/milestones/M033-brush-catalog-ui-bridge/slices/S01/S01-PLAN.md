# M033/S01 - Brush Catalog UI Bridge

Plan source: `docs/superpowers/plans/2026-05-05-m033-brush-catalog-ui-bridge.md`

## Scope

- Python brush catalog view model
- Brush Palette non-Item tabs backed by catalog entries
- catalog brush selection signal
- MainWindow active brush state wiring
- Jump to Brush catalog reuse

## Non-Goals

- no renderer changes
- no minimap generation
- no Search menu changes
- no PyO3 brush export
- no map mutation for catalog brush apply
- no autoborder preview

## Tasks

- [ ] T01: Add brush catalog view-model tests and implementation.
- [ ] T02: Load Brush Palette non-Item tabs from catalog entries.
- [ ] T03: Wire catalog brush selection into MainWindow active brush state.
- [ ] T04: Reuse catalog entries in Jump to Brush.
- [ ] T05: Closeout docs, caveman-review, and verification.

## Verification

```bash
QT_QPA_PLATFORM=offscreen PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_brush_catalog_ui_bridge.py tests/python/test_item_palette_integration.py tests/python/test_find_brush_tier2.py tests/python/test_main_window_editor_shell_actions.py tests/python/test_legacy_search_menu.py -q --tb=short
PATH="/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/models/brush_catalog.py pyrme/ui/docks/brush_palette.py pyrme/ui/dialogs/find_brush.py pyrme/ui/main_window.py tests/python/test_brush_catalog_ui_bridge.py tests/python/test_find_brush_tier2.py tests/python/test_item_palette_integration.py
PY312="/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu"
PYO3_PYTHON="$PY312/bin/python3.12" LD_LIBRARY_PATH="$PY312/lib:${LD_LIBRARY_PATH:-}" RUSTFLAGS="-L native=$PY312/lib -l dylib=python3.12" PATH="/home/marcelo/.local/bin:$PATH" rtk cargo test -p rme_core brushes --quiet
git diff --check
PATH="/home/marcelo/.local/bin:$PATH" rtk npm run preflight --silent
```

## Stop Condition

S01 done when catalog brush entries appear in the dock and Jump to Brush, selecting one updates shell active brush state, all focused tests pass, and Search/menu/renderer/minimap remain untouched.
