# LEGACY-90-NAVIGATE + LEGACY-100-WINDOW Plan

> **Workflow:** use `superpowers:brainstorming` to confirm the slice, `superpowers:writing-plans` to keep the contract explicit, `superpowers:subagent-driven-development` for parallel workers, and `superpowers:requesting-code-review` before closeout.

**Goal:** implement the next legacy parity slice after `LEGACY-00-CONTRACT` by bringing `Navigate` and `Window` into parity with `remeres-map-editor-redux/data/menubar.xml`.

**Constraints:** keep the work faithful to the legacy C++ contract, keep the Python shell as the visual layer, and stay within the repo conventions already established for Python 3.12+, GSD 2, Codex orchestration, and Superpowers workflow discipline.

---

## File Structure

- Modify: `pyrme/ui/main_window.py`
  - Build the legacy `Navigate` and `Window` menu trees and wire them to the current shell seams.
- Modify: `pyrme/ui/dialogs/goto_position.py`
  - Reuse the existing dialog contract if any parity gap is exposed by the slice tests.
- Modify: `pyrme/ui/docks/minimap.py`
  - Ensure the minimap dock can be toggled through the legacy window action.
- Modify: `pyrme/ui/docks/brush_palette.py`
  - Preserve palette visibility and selection behavior where the legacy `Window` menu expects it.
- Modify: `pyrme/ui/docks/properties.py`
  - Preserve the tile properties visibility contract.
- Modify: `pyrme/ui/docks/waypoints.py`
  - Preserve any palette or dock hook needed by the legacy `Window` menu.
- Create: `tests/python/test_legacy_navigate_window_contract.py`
  - XML-backed contract test for the `Navigate` and `Window` menu surface.
- Create: `tests/python/test_legacy_navigate_window_shell.py`
  - Verifies the shell wiring for previous-position, goto-position, floor switching, and dock toggles.

This plan is intentionally narrow. It does not reopen `LEGACY-00-CONTRACT` and it does not expand into other menu families.

### Task 1: Freeze the `Navigate` and `Window` contract in tests

**Files:**
- Create: `tests/python/test_legacy_navigate_window_contract.py`

- [ ] Add a pure contract test that checks `menubar.xml` against the Python-facing menu metadata for:
  - `Go to Previous Position`
  - `Go to Position...`
  - `Jump to Brush...`
  - `Jump to Item...`
  - `Floor 0` through `Floor 15`
  - `Minimap`
  - `Tool Options`
  - `Tile Properties`
  - `In-game Preview`
  - `New Palette`
  - `Palette`
  - `Toolbars`
- [ ] Verify shortcuts and help text for the actions that define them in the XML.
- [ ] Run the contract test and confirm it fails before implementation.

### Task 2: Wire the `Navigate` menu to the existing shell state

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Create: `tests/python/test_legacy_navigate_window_shell.py`

- [ ] Add a failing shell test for previous-position restore and goto-position update flow.
- [ ] Add a failing shell test for the `Floor` submenu selecting floors 0 through 15.
- [ ] Wire the `Navigate` actions to the existing dialog and shell-state seams.
- [ ] Keep any missing behavior explicit instead of hiding it behind fake backends.
- [ ] Re-run the narrow navigation shell tests until they pass.

### Task 3: Wire the `Window` menu to the existing dock and toolbar surfaces

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Modify: `pyrme/ui/docks/minimap.py`
- Modify: `pyrme/ui/docks/brush_palette.py`
- Modify: `pyrme/ui/docks/properties.py`
- Modify: `pyrme/ui/docks/waypoints.py`

- [ ] Add failing tests for toggling the existing `Minimap`, `Tool Options`, `Tile Properties`, and `In-game Preview` surfaces.
- [ ] Preserve the `New Palette`, `Palette`, and `Toolbars` menu structure even where a surface is only a visibility toggle.
- [ ] Bind the menu actions to the current dock and toolbar objects rather than creating a second window model.
- [ ] Re-run the shell tests until the window surface matches the XML contract.

### Task 4: Audit the slice against the legacy XML

**Files:**
- Create: `tests/python/test_legacy_navigate_window_contract.py`

- [ ] Compare the Python menu tree with `remeres-map-editor-redux/data/menubar.xml`.
- [ ] Confirm the exact ordering of `Navigate` and `Window`.
- [ ] Confirm the slice only claims the actions it actually implements.
- [ ] Run the narrow verification set before closeout.

## Definition of Done

- `Navigate` and `Window` match the legacy C++ menu contract.
- The implemented actions use existing Python seams and remain testable.
- The slice keeps its scope narrow enough for code review and follow-on parity work.
- The docs and tests make the delta explicit instead of implying full editor parity.
