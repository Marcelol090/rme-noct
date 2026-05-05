# M032/S01 Shell Focus Tokens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add tested Noct focus tokens and wire active/inactive shell focus state to welcome lists and editor view tabs/canvases.

**Architecture:** Keep style logic in `pyrme/ui/styles/focus.py` and reuse existing theme tokens. Welcome lists receive focused-list QSS through `item_view_qss()`. Editor view canvases receive a dynamic `activeEditorView` property refreshed during tab setup and tab changes.

**Tech Stack:** Python 3, PyQt6 widgets/QSS, pytest-qt, existing Noct theme/style helpers.

---

## Files

- Create: `pyrme/ui/styles/focus.py`
- Create: `tests/python/test_focus_tokens.py`
- Modify: `pyrme/ui/styles/__init__.py`
- Modify: `pyrme/ui/styles/contracts.py`
- Modify: `pyrme/ui/dialogs/welcome_dialog.py`
- Modify: `pyrme/ui/main_window.py`
- Modify: `tests/python/test_welcome_dialog.py`
- Modify: `tests/python/test_main_window_new_view.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/T01-SUMMARY.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/T02-SUMMARY.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/T03-SUMMARY.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/T04-SUMMARY.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/T05-SUMMARY.md`
- Create: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/S01-SUMMARY.md`

## Task 1: Focus Token Tests

**Files:**
- Create: `tests/python/test_focus_tokens.py`

- [ ] **Step 1: Write failing tests**

```python
from pyrme.ui.styles.focus import FOCUS_TOKENS, focus_panel_qss
from pyrme.ui.styles.contracts import qss_color
from pyrme.ui.theme import THEME


def test_focus_tokens_use_noct_theme_colors() -> None:
    assert FOCUS_TOKENS.inactive_border == qss_color(THEME.ghost_border)
    assert FOCUS_TOKENS.active_border == qss_color(THEME.focus_border)
    assert FOCUS_TOKENS.active_background == qss_color(THEME.lifted_glass)


def test_focus_panel_qss_contains_active_and_inactive_rules() -> None:
    qss = focus_panel_qss("QWidget")

    assert 'QWidget[activeEditorView="false"]' in qss
    assert 'QWidget[activeEditorView="true"]' in qss
    assert f"border: 1px solid {FOCUS_TOKENS.inactive_border};" in qss
    assert f"border: 1px solid {FOCUS_TOKENS.active_border};" in qss
    assert f"background-color: {FOCUS_TOKENS.active_background};" in qss
```

- [ ] **Step 2: Verify RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_focus_tokens.py -q --tb=short
```

Expected: FAIL with `ModuleNotFoundError: No module named 'pyrme.ui.styles.focus'`.

## Task 2: Focus Token Seam

**Files:**
- Create: `pyrme/ui/styles/focus.py`
- Modify: `pyrme/ui/styles/__init__.py`

- [ ] **Step 1: Add minimal focus module**

Create `pyrme/ui/styles/focus.py`:

```python
"""Focus-state QSS helpers for Noct shell widgets."""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent

from pyrme.ui.styles.contracts import qss_color
from pyrme.ui.theme import THEME


@dataclass(frozen=True, slots=True)
class FocusTokens:
    inactive_border: str
    active_border: str
    active_background: str
    radius_px: int = 4


FOCUS_TOKENS = FocusTokens(
    inactive_border=qss_color(THEME.ghost_border),
    active_border=qss_color(THEME.focus_border),
    active_background=qss_color(THEME.lifted_glass),
)


def focus_panel_qss(selector: str) -> str:
    return dedent(
        f"""
        {selector}[activeEditorView="false"] {{
            border: 1px solid {FOCUS_TOKENS.inactive_border};
            border-radius: {FOCUS_TOKENS.radius_px}px;
        }}
        {selector}[activeEditorView="true"] {{
            border: 1px solid {FOCUS_TOKENS.active_border};
            border-radius: {FOCUS_TOKENS.radius_px}px;
            background-color: {FOCUS_TOKENS.active_background};
        }}
        """
    ).strip()
```

- [ ] **Step 2: Export focus seam**

Modify `pyrme/ui/styles/__init__.py`:

```python
from .focus import FOCUS_TOKENS, FocusTokens, focus_panel_qss
```

Add to `__all__`:

```python
    "FOCUS_TOKENS",
    "FocusTokens",
    "focus_panel_qss",
```

- [ ] **Step 3: Verify GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_focus_tokens.py -q --tb=short
```

Expected: `2 passed`.

## Task 3: Welcome List Focus Rules

**Files:**
- Modify: `pyrme/ui/styles/contracts.py`
- Modify: `pyrme/ui/dialogs/welcome_dialog.py`
- Modify: `tests/python/test_welcome_dialog.py`

- [ ] **Step 1: Write failing welcome tests**

Append to `tests/python/test_welcome_dialog.py`:

```python
class TestWelcomeFocusStyling:
    def test_recent_and_client_lists_have_stable_focus_object_names(self, dialog):
        assert dialog._recent_list.objectName() == "welcome_recent_maps_list"
        assert dialog._client_list.objectName() == "welcome_client_version_list"

    def test_lists_include_focus_border_rule(self, dialog):
        recent_qss = dialog._recent_list.styleSheet()
        client_qss = dialog._client_list.styleSheet()

        assert "QListWidget:focus" in recent_qss
        assert "QListWidget:focus" in client_qss
        assert "border: 1px solid rgba(124, 92, 252, 127)" in recent_qss
        assert "border: 1px solid rgba(124, 92, 252, 127)" in client_qss
```

- [ ] **Step 2: Verify RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_welcome_dialog.py::TestWelcomeFocusStyling -q --tb=short
```

Expected: FAIL because object names and `QListWidget:focus` rule are missing.

- [ ] **Step 3: Add focus rule to item view QSS**

In `pyrme/ui/styles/contracts.py`, inside `item_view_qss()` base block after the widget selector rule, add:

```python
        {widget_selector}:focus {{
            border: 1px solid {qss_color(THEME.focus_border)};
            background-color: {qss_color(THEME.lifted_glass)};
        }}
```

- [ ] **Step 4: Add welcome object names**

In `WelcomeDialog._build_interface()`, after each list is created:

```python
self._recent_list.setObjectName("welcome_recent_maps_list")
```

and:

```python
self._client_list.setObjectName("welcome_client_version_list")
```

- [ ] **Step 5: Verify GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_welcome_dialog.py::TestWelcomeFocusStyling -q --tb=short
```

Expected: `2 passed`.

## Task 4: Editor View Focus Tests

**Files:**
- Modify: `tests/python/test_main_window_new_view.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/python/test_main_window_new_view.py`:

```python
def test_editor_view_tabs_have_focus_object_name_and_qss(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view-focus-qss.ini"),
        canvas_factory=_FakeCanvasWidget,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert window._view_tabs.objectName() == "editor_view_tabs"
    assert "QTabWidget#editor_view_tabs::pane" in window._view_tabs.styleSheet()
    assert "QWidget[activeEditorView=\"true\"]" in window._view_tabs.styleSheet()


def test_active_editor_view_property_tracks_current_tab(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view-focus-state.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert canvases[0].property("activeEditorView") is True

    window.editor_new_view_action.trigger()

    assert canvases[0].property("activeEditorView") is False
    assert canvases[1].property("activeEditorView") is True

    window._view_tabs.setCurrentIndex(0)

    assert canvases[0].property("activeEditorView") is True
    assert canvases[1].property("activeEditorView") is False
```

- [ ] **Step 2: Verify RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_main_window_new_view.py::test_editor_view_tabs_have_focus_object_name_and_qss tests/python/test_main_window_new_view.py::test_active_editor_view_property_tracks_current_tab -q --tb=short
```

Expected: FAIL because `_view_tabs` object name/style and `activeEditorView` properties are missing.

## Task 5: Editor View Focus Wiring and Closeout

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/S01-PLAN.md`
- Create summaries under `.gsd/milestones/M032-ui-hyprland-integration/slices/S01/`

- [ ] **Step 1: Import focus helper**

In `pyrme/ui/main_window.py`, add:

```python
from pyrme.ui.styles import focus_panel_qss
```

- [ ] **Step 2: Style editor view tabs**

In `_setup_central_widget()`, after `self._view_tabs = QTabWidget(self)`, add:

```python
self._view_tabs.setObjectName("editor_view_tabs")
self._view_tabs.setStyleSheet(
    f"""
    QTabWidget#editor_view_tabs::pane {{
        border: 1px solid {qss_color(THEME.ghost_border)};
        border-radius: 4px;
    }}
    QTabBar::tab:selected {{
        border-bottom: 2px solid {qss_color(THEME.focus_border)};
    }}
    {focus_panel_qss("QWidget")}
    """
)
```

- [ ] **Step 3: Add active-view refresh helper**

Add method near `_active_view()`:

```python
def _refresh_editor_view_focus_state(self) -> None:
    if not hasattr(self, "_view_tabs"):
        return
    active_index = self._view_tabs.currentIndex()
    for index, view in enumerate(self._views):
        widget = cast("QWidget", view.canvas)
        widget.setProperty("activeEditorView", index == active_index)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
```

- [ ] **Step 4: Call refresh helper**

Call `self._refresh_editor_view_focus_state()`:

```python
# in _setup_central_widget(), after setCentralWidget
self._refresh_editor_view_focus_state()

# in _new_view(), after setCurrentIndex
self._refresh_editor_view_focus_state()

# in _on_view_tab_changed(), before _sync_canvas_shell_state()
self._refresh_editor_view_focus_state()
```

- [ ] **Step 5: Verify slice tests**

Run:

```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py -q --tb=short
```

Expected: all tests pass.

- [ ] **Step 6: Verify lint and diff**

Run:

```bash
rtk python3 -m ruff check pyrme/ui/styles/focus.py pyrme/ui/styles/__init__.py pyrme/ui/styles/contracts.py pyrme/ui/dialogs/welcome_dialog.py pyrme/ui/main_window.py tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py
rtk git diff --check
```

Expected: both pass.

- [ ] **Step 7: Write closeout docs**

Update:

```markdown
# S01 Summary

M032/S01 added tokenized Noct focus state for welcome lists and editor view canvases.

Verification:
- QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py -q --tb=short
- rtk python3 -m ruff check pyrme/ui/styles/focus.py pyrme/ui/styles/__init__.py pyrme/ui/styles/contracts.py pyrme/ui/dialogs/welcome_dialog.py pyrme/ui/main_window.py tests/python/test_focus_tokens.py tests/python/test_welcome_dialog.py tests/python/test_main_window_new_view.py
- rtk git diff --check
```

Mark all S01 tasks `[x]` only after verification passes.

## Plan Self-Review

- Spec coverage: covered token seam, welcome lists, editor view active state, tests, and offscreen verification.
- Placeholder scan: no unresolved placeholder markers.
- Type consistency: `FocusTokens`, `FOCUS_TOKENS`, `focus_panel_qss`, and `activeEditorView` names match across tasks.
