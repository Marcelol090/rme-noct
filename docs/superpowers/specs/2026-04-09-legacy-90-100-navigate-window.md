# LEGACY-90-NAVIGATE + LEGACY-100-WINDOW Spec

## Goal
Deliver the next legacy parity slice after `LEGACY-00-CONTRACT` by matching the `Navigate` and `Window` menu contract from the legacy redux C++ editor while keeping the Python shell conventions already established in this repo.

## Sources of Truth
- Legacy menu contract: `remeres-map-editor-redux/data/menubar.xml`
- Existing Python shell: `pyrme/ui/main_window.py`
- Existing navigation dialog seam: `pyrme/ui/dialogs/goto_position.py`
- Existing dock surfaces: `pyrme/ui/docks/*.py`
- Durable workflow state: `.gsd/`

## Scope
### `LEGACY-90-NAVIGATE`
- Match the legacy `Navigate` menu structure and order.
- Preserve the exact labels and shortcuts for:
  - `Go to Previous Position`
  - `Go to Position...`
  - `Jump to Brush...`
  - `Jump to Item...`
- Preserve the legacy `Floor` submenu with `Floor 0` through `Floor 15`.
- Wire `Go to Previous Position` and `Go to Position...` to the existing shell-state and dialog seams rather than inventing new navigation behavior.

### `LEGACY-100-WINDOW`
- Match the legacy `Window` menu structure and order.
- Preserve the exact labels and shortcuts for:
  - `Minimap`
  - `Tool Options`
  - `Tile Properties`
  - `In-game Preview`
  - `New Palette`
- Preserve the legacy `Palette` submenu and `Toolbars` submenu.
- Bind window actions to the existing dock and toolbar surfaces already present in the Python shell.

## Non-Goals
- Do not expand into `Editor`, `Search`, `Map`, `Selection`, `View`, `Show`, `Experimental`, `Scripts`, or `About`.
- Do not redesign the legacy menu taxonomy.
- Do not invent new dock windows or palette categories that are not in `menubar.xml`.
- Do not change the legacy contract just because a backend is incomplete; if a surface is missing, document that gap explicitly.

## Reuse Policy
- Reuse the `LEGACY-00-CONTRACT` menu contract foundation.
- Reuse the existing `GotoPositionDialog` seam and shell-state persistence.
- Reuse the current `minimap`, `brush palette`, `properties`, and `waypoints` dock modules where they already match the legacy window model.
- Keep the Python shell as the visual layer and preserve the legacy C++ behavior as the functional reference.

## Orchestration Model
- Codex remains the orchestrator.
- Superpowers provides the workflow discipline for `brainstorming`, `writing-plans`, `subagent-driven-development`, and `requesting-code-review`.
- GSD 2 provides the durable slice tracking and isolated worktree execution model.
- Multi-agent execution should split cleanly by file path so each worker can own one explicit write set.

## Behavior Contract
### Navigate
- `Go to Previous Position` returns to the last stored screen center when one exists.
- `Go to Position...` opens the existing position dialog and updates shell state on accept.
- `Jump to Brush...` and `Jump to Item...` remain wired to their existing shell entry points.
- `Floor` submenu entries switch floors exactly as the legacy menu names indicate.

### Window
- `Minimap` toggles the existing minimap dock.
- `Tool Options`, `Tile Properties`, and `In-game Preview` map to the corresponding existing dock or window surfaces.
- `New Palette` and the `Palette` submenu preserve the legacy palette selection contract.
- `Toolbars` submenu preserves the legacy toolbar visibility contract.

## Acceptance Criteria
- The Python menu tree matches the legacy `Navigate` and `Window` structure from `menubar.xml`.
- The covered actions expose the legacy labels, order, and shortcuts.
- The window and navigation actions are wired to existing shell seams instead of placeholder-only stubs.
- The slice can be validated with narrow tests that compare the Python surface to the XML contract.
