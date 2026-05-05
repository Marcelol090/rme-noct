# M032/S01 Shell Focus Tokens Design

## Goal

Make active and inactive shell focus state explicit in the Noct UI system without broad restyling. This slice covers tokenized focus visuals for existing welcome lists and editor view tabs/canvases only.

## Current Evidence

- `pyrme/ui/theme.py` already exposes `ghost_border`, `active_border`, `focus_border`, and `lifted_glass`.
- `pyrme/ui/styles/contracts.py` already centralizes shared QSS helpers.
- `WelcomeDialog` applies `item_view_qss("QListWidget")` to recent-map and client lists.
- `MainWindow` owns `_view_tabs`, creates canvas tabs in `_setup_central_widget()` and `_new_view()`, and already reacts to `_on_view_tab_changed()`.
- Baseline target is green: `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py -q --tb=short` reports 33 passed.

## Design

Add a small focus-style contract under `pyrme/ui/styles/`. It exposes immutable focus token values and QSS helpers that reuse existing Noct theme colors. The helper must be deterministic and testable without rendering.

Apply the helper in two places:

- `WelcomeDialog` list widgets get stable object names and `item_view_qss()` gains a focused-list border rule.
- `MainWindow` view tabs get a stable object name and a tab/canvas focus stylesheet. Active canvas widgets receive `activeEditorView=true`; inactive canvas widgets receive `activeEditorView=false`.

The active canvas property is state-only, offscreen-safe, and does not require a live OpenGL context. It is refreshed after initial setup, new view creation, and tab changes.

## Non-Goals

- No renderer rewrite.
- No new visual language.
- No layout changes.
- No changes to menu behavior.
- No Hyprland window-manager integration claims.
- No broad restyling of every dialog or dock.

## Acceptance

- Tests fail before implementation and pass after minimal code.
- Focus token QSS references real Noct theme colors.
- Welcome recent/client lists expose stable object names and focused-list rules.
- MainWindow updates `activeEditorView` properties correctly across tab changes.
- Existing welcome and new-view tests remain green under `QT_QPA_PLATFORM=offscreen`.
