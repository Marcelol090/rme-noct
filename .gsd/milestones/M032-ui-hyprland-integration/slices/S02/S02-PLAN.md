# M032/S02 - Hyprland Visual Polish

## Scope

- Arch-blue Hyprland visual token polish.
- GlassPanel shadow and focus-rim state.
- Shared QSS helper reuse in selected docks.
- Dialog/design wording alignment.
- Guardrail: Search menu behavior remains unchanged.

## Tasks

- [x] T01: Add failing token/glass-panel tests and implement token/shadow/focus state.
- [x] T02: Add failing shared-QSS dock tests and reuse existing QSS helpers.
- [x] T03: Update wording/static QSS/GAP docs and verify Search guardrails.

## Files

- `pyrme/ui/theme.py`
- `pyrme/ui/components/glass.py`
- `pyrme/ui/styles/__init__.py`
- `pyrme/ui/styles/dark_theme.qss`
- `pyrme/ui/docks/brush_palette.py`
- `pyrme/ui/docks/minimap.py`
- `pyrme/ui/docks/properties.py`
- `pyrme/ui/dialogs/about.py`
- `pyrme/ui/dialogs/preferences.py`
- `pyrme/ui/dialogs/welcome_dialog.py`
- `tests/python/test_focus_tokens.py`
- `tests/python/test_welcome_dialog.py`
- `GAP_ANALYSIS.md`

## Verification

```bash
QT_QPA_PLATFORM=offscreen PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py tests/python/test_legacy_search_menu.py -q --tb=short
PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/theme.py pyrme/ui/components/glass.py pyrme/ui/styles/__init__.py pyrme/ui/docks/brush_palette.py pyrme/ui/docks/minimap.py pyrme/ui/docks/properties.py pyrme/ui/dialogs/about.py pyrme/ui/dialogs/preferences.py pyrme/ui/dialogs/welcome_dialog.py tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py
rtk git diff --check
```

## Stop Condition

S02 done when visual polish is implemented with focused tests, Search menu guard tests still pass, and no behavior-only Search/Menu changes are in the diff.
