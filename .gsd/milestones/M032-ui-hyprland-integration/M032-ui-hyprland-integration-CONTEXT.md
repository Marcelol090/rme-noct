# M032 Context - UI Hyprland Integration

## Goal

Harden the Noct/Hyprland-style shell as a tested UI system, not scattered visual tweaks.

## Source Evidence

- `pyrme/ui/theme.py`
- `pyrme/ui/styles/contracts.py`
- `pyrme/ui/dialogs/welcome_dialog.py`
- `pyrme/ui/main_window.py`
- `tests/python/test_welcome_dialog.py`
- `tests/python/test_main_window_new_view.py`

## Boundaries

- No renderer rewrite.
- No broad restyling outside touched widgets.
- No new design language; preserve existing Noct shell direction.
- No runtime code before S01 plan approval.

## First Slice

`S01-shell-focus-tokens` adds tokenized active/inactive focus state for welcome lists and editor view tabs/canvases.
