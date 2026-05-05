# M032/S01 - Shell Focus Tokens

## Scope

- Active/inactive shell focus visual state.
- Reusable token/constants seam for focus rings and panel state.
- Tests for focus transitions on supported widgets.

## Tasks

- [ ] T01: Add failing focus-token and welcome-list tests.
- [ ] T02: Add minimal focus token QSS seam.
- [ ] T03: Wire welcome lists to stable object names and focus QSS.
- [ ] T04: Add failing editor-view focus state tests.
- [ ] T05: Wire editor view tabs/canvas active state and closeout docs.

## Files

- `pyrme/ui/styles/focus.py`
- `pyrme/ui/styles/__init__.py`
- `pyrme/ui/styles/contracts.py`
- `pyrme/ui/dialogs/welcome_dialog.py`
- `pyrme/ui/main_window.py`
- `tests/python/test_focus_tokens.py`
- `tests/python/test_welcome_dialog.py`
- `tests/python/test_main_window_new_view.py`

## Verification

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py -q --tb=short
rtk python3 -m ruff check pyrme/ui/styles/focus.py pyrme/ui/styles/__init__.py pyrme/ui/styles/contracts.py pyrme/ui/dialogs/welcome_dialog.py pyrme/ui/main_window.py tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py
rtk git diff --check
```
