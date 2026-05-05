# M032/S02 Hyprland Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply visual-only Hyprland glass polish on top of M032/S01 without changing menu, search, or renderer behavior.

**Architecture:** Keep the design system API stable and update token values plus focused widget styling. Add offscreen-safe widget tests for the glass panel and QSS contracts, then reuse existing style helpers in dock widgets. Search behavior remains guarded by existing legacy search tests.

**Tech Stack:** Python 3.12, PyQt6, pytest-qt, ruff, GSD docs.

---

## File Structure

- Modify `pyrme/ui/theme.py`: change compatible token values to Arch-blue/Hyprland palette.
- Modify `pyrme/ui/styles/__init__.py`: export `dropdown_qss` and `input_field_qss`.
- Modify `pyrme/ui/components/glass.py`: add shadow and focus-rim behavior.
- Modify `pyrme/ui/docks/brush_palette.py`: replace inline search/list QSS with shared helpers.
- Modify `pyrme/ui/docks/minimap.py`: use `qss_color()` and theme-aware button colors.
- Modify `pyrme/ui/docks/properties.py`: use `section_heading_qss()` and `qss_color()`.
- Modify `pyrme/ui/dialogs/about.py`, `pyrme/ui/dialogs/preferences.py`, `pyrme/ui/dialogs/welcome_dialog.py`: update design-language wording only.
- Modify `pyrme/ui/styles/dark_theme.qss`: align static global palette with updated tokens.
- Modify `tests/python/test_focus_tokens.py`: add Hyprland token, style export, and glass-panel tests.
- Modify `tests/python/test_welcome_dialog.py`: make focus-border expectation token-based.
- Modify `GAP_ANALYSIS.md`: report visual polish only.
- Modify `.gsd/milestones/M032-ui-hyprland-integration/*`: open and close S02 docs.

## Task 1: Token and Glass Panel Contract

**Files:**
- Modify: `tests/python/test_focus_tokens.py`
- Modify: `pyrme/ui/theme.py`
- Modify: `pyrme/ui/components/glass.py`

- [ ] **Step 1: Write failing tests**

Add tests:

```python
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QFocusEvent
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from pyrme.ui.components.glass import GlassPanel
from pyrme.ui.styles.contracts import qss_color
from pyrme.ui.theme import THEME


def test_hyprland_tokens_use_arch_blue_accents() -> None:
    assert THEME.void_black == QColor("#1e2227")
    assert THEME.amethyst_core == QColor("#1793d1")
    assert THEME.deep_amethyst == QColor("#116b99")
    assert qss_color(THEME.focus_border) == "rgba(23, 147, 209, 204)"


def test_glass_panel_shadow_and_focus_contract(qtbot) -> None:
    panel = GlassPanel()
    qtbot.addWidget(panel)

    effect = panel.graphicsEffect()
    assert isinstance(effect, QGraphicsDropShadowEffect)
    assert effect.blurRadius() == 20
    assert effect.yOffset() == 4
    assert panel.focusPolicy() == Qt.FocusPolicy.ClickFocus
    assert panel._is_active is False

    panel.focusInEvent(QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.MouseFocusReason))
    assert panel._is_active is True

    panel.focusOutEvent(QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.MouseFocusReason))
    assert panel._is_active is False
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_focus_tokens.py -q --tb=short
```

Expected: FAIL because tokens are still purple and `GlassPanel` has no shadow/focus state.

- [ ] **Step 3: Implement minimal code**

Update token values and add `GlassPanel` focus/shadow support. Use `QGraphicsDropShadowEffect(self)`, `setBlurRadius(20)`, `setOffset(0, 4)`, `setFocusPolicy(Qt.FocusPolicy.ClickFocus)`, `_is_active`, `focusInEvent()`, and `focusOutEvent()`.

- [ ] **Step 4: Run GREEN**

Run the same test command. Expected: PASS.

## Task 2: Shared QSS Reuse in Docks

**Files:**
- Modify: `tests/python/test_focus_tokens.py`
- Modify: `pyrme/ui/styles/__init__.py`
- Modify: `pyrme/ui/docks/brush_palette.py`
- Modify: `pyrme/ui/docks/minimap.py`
- Modify: `pyrme/ui/docks/properties.py`

- [ ] **Step 1: Write failing tests**

Add tests:

```python
def test_styles_exports_input_and_dropdown_helpers() -> None:
    from pyrme.ui.styles import dropdown_qss, input_field_qss

    assert "QLineEdit:focus" in input_field_qss("QLineEdit")
    assert "QComboBox:focus" in dropdown_qss("QComboBox")


def test_brush_palette_uses_shared_focus_qss(qtbot) -> None:
    from pyrme.ui.docks.brush_palette import BrushPaletteDock

    dock = BrushPaletteDock()
    qtbot.addWidget(dock)

    assert "QLineEdit:focus" in dock._search_bar.styleSheet()
    assert "QListView:focus" in dock._views["Terrain"].styleSheet()
    assert qss_color(THEME.focus_border) in dock._search_bar.styleSheet()


def test_minimap_and_properties_use_theme_qss_contracts(qtbot) -> None:
    from pyrme.ui.docks.minimap import MinimapDock
    from pyrme.ui.docks.properties import PropertiesDock

    minimap = MinimapDock()
    properties = PropertiesDock()
    qtbot.addWidget(minimap)
    qtbot.addWidget(properties)

    assert qss_color(THEME.ghost_border) in minimap.map_view.styleSheet()
    assert qss_color(THEME.moonstone_white) in minimap.pos_label.styleSheet()
    assert qss_color(THEME.active_border) in minimap.z_up_btn.styleSheet()

    heading = properties.content_widget().layout().itemAt(0).widget()
    assert heading.text() == "SELECTION PROPERTIES"
    assert "font-size: 11px" in heading.styleSheet()
    assert qss_color(THEME.ash_lavender) in heading.styleSheet()
```

- [ ] **Step 2: Run RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_focus_tokens.py -q --tb=short
```

Expected: FAIL because exports and dock QSS reuse are incomplete.

- [ ] **Step 3: Implement minimal code**

Export `dropdown_qss` and `input_field_qss`. Replace inline QSS in brush palette list/search widgets with `input_field_qss("QLineEdit")` and `item_view_qss("QListView")`. Update minimap/properties QSS to use `qss_color()` and `section_heading_qss()`.

- [ ] **Step 4: Run GREEN**

Run the same test command. Expected: PASS.

## Task 3: Wording, Static QSS, Guardrails, and Closeout

**Files:**
- Modify: `tests/python/test_welcome_dialog.py`
- Modify: `pyrme/ui/dialogs/about.py`
- Modify: `pyrme/ui/dialogs/preferences.py`
- Modify: `pyrme/ui/dialogs/welcome_dialog.py`
- Modify: `pyrme/ui/styles/dark_theme.qss`
- Modify: `GAP_ANALYSIS.md`
- Modify: `.gsd/milestones/M032-ui-hyprland-integration/M032-ui-hyprland-integration-ROADMAP.md`
- Modify: `.gsd/milestones/M032-ui-hyprland-integration/M032-ui-hyprland-integration-META.json`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S02/S02-SUMMARY.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S02/tasks/T01-SUMMARY.md`

- [ ] **Step 1: Write failing/guard tests**

Update the welcome focus test:

```python
    def test_lists_include_focus_border_rule(self, dialog):
        recent_qss = dialog._recent_list.styleSheet()
        client_qss = dialog._client_list.styleSheet()
        expected_focus_border = qss_color(THEME.focus_border)

        assert "QListWidget:focus" in recent_qss
        assert "QListWidget:focus" in client_qss
        assert f"border: 1px solid {expected_focus_border}" in recent_qss
        assert f"border: 1px solid {expected_focus_border}" in client_qss
```

Add imports near the top of `tests/python/test_welcome_dialog.py`:

```python
from pyrme.ui.styles.contracts import qss_color
from pyrme.ui.theme import THEME
```

Run Search guard:

```bash
QT_QPA_PLATFORM=offscreen PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_legacy_search_menu.py -q --tb=short
```

Expected before implementation: welcome token expectation may fail after Task 1 until updated; search test must pass and remain unchanged.

- [ ] **Step 2: Implement wording/static QSS/docs**

Update design wording to Hyprland Glassmorphism, global QSS accent literals to Arch blue, and GSD docs to mark S02 complete. Do not touch `MainWindow` search wiring.

- [ ] **Step 3: Run final focused verification**

Run:

```bash
QT_QPA_PLATFORM=offscreen PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py tests/python/test_legacy_search_menu.py -q --tb=short
PATH="$PWD/.venv/bin:/home/marcelo/.local/bin:$PATH" rtk python3 -m ruff check pyrme/ui/theme.py pyrme/ui/components/glass.py pyrme/ui/styles/__init__.py pyrme/ui/docks/brush_palette.py pyrme/ui/docks/minimap.py pyrme/ui/docks/properties.py pyrme/ui/dialogs/about.py pyrme/ui/dialogs/preferences.py pyrme/ui/dialogs/welcome_dialog.py tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py
rtk git diff --check
```

Expected: all commands pass.
