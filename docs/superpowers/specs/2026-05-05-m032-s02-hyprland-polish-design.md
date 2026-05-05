# M032/S02 Hyprland Polish Design

## Goal

Apply the approved Hyprland-inspired glass polish on top of the already merged M032/S01 focus-token slice without changing menu behavior, renderer behavior, or search workflows.

## Current Evidence

- `origin/main` already contains M032/S01 focus-token docs, tests, and `activeEditorView` QSS state.
- The stale local M032 diff was saved outside the worktree as `.tmp-m032-s02-local-diff-reference.patch` and is reference-only.
- `pyrme/ui/styles/contracts.py` already owns `input_field_qss()`, `dropdown_qss()`, `item_view_qss()`, `section_heading_qss()`, and `qss_color()`.
- `BrushPaletteDock`, `MinimapDock`, and `PropertiesDock` still carry local inline QSS that can move to existing contracts without changing behavior.
- Qt/PyQt docs confirm `focusInEvent(QFocusEvent)`, `focusOutEvent(QFocusEvent)`, `QGraphicsDropShadowEffect`, and dynamic-property stylesheet refresh patterns.

## Design

Keep S02 visual-only. Move the shell palette from purple Noct accents to Arch-blue Hyprland accents using the existing token names, so call sites keep stable APIs. Keep semantic names like `amethyst_core` for compatibility in this slice; do not rename tokens across the repo.

Add active glass-panel polish to `GlassPanel`: a deep shadow effect, click focus policy, and an active top rim drawn only while the panel has keyboard focus. This stays offscreen-testable through widget properties and direct focus event calls; no screenshot or live compositor dependency.

Reuse shared QSS helpers in focused docks instead of repeating inline color strings. Export the already-present input/dropdown helpers from `pyrme.ui.styles`. Update dock/dialog text that names the design language where it is already visible or documented, but do not add explanatory in-app text.

Search menu and selection behavior are out of scope. Existing `tests/python/test_legacy_search_menu.py` must continue to prove Search on Map actions remain explicit safe gaps.

## Non-Goals

- No `MainWindow` search action rewiring.
- No renderer, minimap generation, or canvas behavior changes.
- No broad dialog rewrite.
- No token renaming migration.
- No screenshot-based acceptance gate.
- No Hyprland compositor integration claim.

## Acceptance

- New tests fail before implementation and pass after minimal code.
- Theme tokens serialize Arch-blue focus/accent colors through existing QSS contracts.
- `GlassPanel` installs a `QGraphicsDropShadowEffect`, accepts click focus, and toggles its active rim state on focus events.
- Brush palette, minimap, and properties docks consume shared QSS helpers while preserving widget structure.
- Existing focus, welcome, new-view, and legacy search tests stay green under `QT_QPA_PLATFORM=offscreen`.
- `GAP_ANALYSIS.md` reports the visual polish without claiming search/menu behavior changed.

