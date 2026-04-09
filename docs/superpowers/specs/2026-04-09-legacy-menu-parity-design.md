# Legacy Menu Parity Design

## Goal
Bring the Python editor shell to verified menu and command parity with the legacy C++ editor, using the legacy XML menu contract as the source of truth while reusing already-verified Python shell infrastructure where it fits the project.

## Sources of Truth
- Legacy menu contract: `remeres-map-editor-redux/data/menubar.xml`
- Current Python shell: `pyrme/ui/main_window.py`
- Reusable prior shell-state slice: `.worktrees/m5-shell-navigation/pyrme/ui/main_window.py`
- Durable workflow state: `.gsd/`

## Scope
- Rebuild the top-level menu tree to match the legacy C++ editor:
  - `File`
  - `Edit`
  - `Editor`
  - `Search`
  - `Map`
  - `Selection`
  - `View`
  - `Show`
  - `Navigate`
  - `Window`
  - `Experimental`
  - `Scripts`
  - `About`
- Introduce a stable action registry and menu builder so parity is defined once and rendered consistently.
- Reuse the verified shell-state and canvas seam work from the prior `M5-SHELL-NAVIGATION` slice where it aligns with the legacy contract.
- Track execution as GSD slices with explicit parity validation per slice.
- Use operator-style multi-agent orchestration during implementation, with the root agent acting as orchestrator.

## Non-Goals
- Invent new menu structures or command groupings when the legacy editor already defines them.
- Treat the prior M5 slice as if it already achieved full parity.
- Collapse the full parity program into one large change set.
- Replace missing backend behavior with undocumented placeholder behavior unless the corresponding legacy action is also intentionally non-functional.

## Reuse Policy
- Reuse as-is:
  - canvas seam contract from the prior M5 slice
  - shell state handling for position, floor, zoom, grid, ghosting, and persistent window state
  - shell-focused tests that remain valid under the legacy menu structure
- Rework:
  - top-level menu taxonomy
  - menu grouping and submenu structure
  - action exposure that currently reflects the simplified Python shell instead of the legacy editor
- Do not rewrite `M5-SHELL-NAVIGATION` history in GSD. New parity slices may depend on it, but must only claim the new delta they actually deliver.

## Orchestration Model
### Root Orchestrator
- The root agent remains the coordinator for the milestone.
- It decomposes the work, dispatches agents, consolidates findings, and approves or rejects slice completion.

### Operator Work Zone
- `legacy explorer`
  - extracts the exact command contract from `menubar.xml`
- `root explorer`
  - identifies existing Python behavior, seams, and missing backends
- `GSD phase runner`
  - keeps slices aligned with milestone state and ordering
- `implementer`
  - implements one slice with an explicit write set
- `parity auditor`
  - checks the Python result against the legacy contract
- `pytest slice runner`
  - runs the narrowest useful test slice for the change

### Required Workflow Layers
- Superpowers process:
  - `brainstorming`
  - `writing-plans`
  - `subagent-driven-development`
  - verification and review
- GSD process:
  - milestone and slice tracking
  - durable state and history
  - isolated execution context
- Context7:
  - required reference source for uncertain API behavior, especially Qt, GSD, and third-party library semantics

## Architecture
### MainWindow
- Owns the editor shell composition.
- Delegates command behavior to handlers instead of embedding all logic inline.
- Consumes the menu builder and action registry.

### Action Registry
- Single source of truth for each action:
  - stable action ID
  - visible label
  - shortcut
  - status/help text
  - menu path
  - handler binding
  - legacy source reference

### Menu Builder
- Builds the full menu tree from the registry/contract rather than hand-assembling menus ad hoc.
- Ensures ordering and grouping stay consistent across slices.

### Shell State
- Tracks:
  - current and previous position
  - current floor
  - zoom
  - grid visibility
  - ghost higher floors
  - lower floor visibility
  - dock and toolbar visibility
  - persisted window geometry/layout via `QSettings`
- Reuses the verified M5 shell-state approach where it remains compatible with the legacy contract.

### Command Handlers
- Group handlers by domain:
  - file
  - edit
  - editor
  - search
  - map
  - selection
  - view
  - show
  - navigate
  - window
  - scripts/about/experimental
- Bind existing dialogs and local backends where they already exist.
- If a backend is missing, the slice spec must say so explicitly rather than hiding it inside menu wiring.

### Parity Audit Layer
- Compares the Python menu surface against `menubar.xml`.
- Validates:
  - menu presence
  - menu order
  - submenu placement
  - action labels
  - shortcuts
  - expected handler intent

## GSD Slice Map
### Stable Slice IDs
1. `LEGACY-00-CONTRACT`
2. `LEGACY-10-FILE`
3. `LEGACY-20-EDIT`
4. `LEGACY-30-EDITOR`
5. `LEGACY-40-SEARCH`
6. `LEGACY-50-MAP`
7. `LEGACY-60-SELECTION`
8. `LEGACY-70-VIEW`
9. `LEGACY-80-SHOW`
10. `LEGACY-90-NAVIGATE`
11. `LEGACY-100-WINDOW`
12. `LEGACY-110-EXPERIMENTAL`
13. `LEGACY-120-SCRIPTS`
14. `LEGACY-130-ABOUT`
15. `LEGACY-140-FINAL-AUDIT`

### Recommended Execution Order
1. `LEGACY-00-CONTRACT`
2. `LEGACY-90-NAVIGATE`
3. `LEGACY-100-WINDOW`
4. `LEGACY-30-EDITOR`
5. `LEGACY-40-SEARCH`
6. `LEGACY-50-MAP`
7. `LEGACY-70-VIEW`
8. `LEGACY-80-SHOW`
9. `LEGACY-20-EDIT`
10. `LEGACY-60-SELECTION`
11. `LEGACY-10-FILE`
12. `LEGACY-110-EXPERIMENTAL`
13. `LEGACY-120-SCRIPTS`
14. `LEGACY-130-ABOUT`
15. `LEGACY-140-FINAL-AUDIT`

### Why This Order
- `LEGACY-00-CONTRACT` fixes the structural base first.
- `LEGACY-90-NAVIGATE` and `LEGACY-100-WINDOW` are the highest-value consumers of previously verified shell-state work.
- Search, map, view, and show slices then build on the corrected shell structure.
- Final audit is deferred until every functional menu group has landed.

## First Slice Contract
### `LEGACY-00-CONTRACT`
This slice should deliver:
- top-level legacy menu tree
- action registry skeleton
- menu builder
- snapshot or structural tests for menu topology
- parity audit foundation against `menubar.xml`

This slice should not try to complete every command backend. Its purpose is to establish the correct contract surface and make later slices safer.

## Testing Strategy
### Menu Tree Snapshot Tests
- Verify top-level order, submenu placement, labels, and shortcuts.

### Action Contract Tests
- Verify actions exist and route to the expected handler seam for the active slice.

### Shell State Tests
- Verify position, previous position, floor, zoom, grid, ghosting, lower floor visibility, and persisted window state.

### Dialog and Backend Integration Tests
- Verify actions open or invoke the real local dialog/backend where implemented.

### Parity Audit Tests
- Compare the Python menu/action surface against `menubar.xml`.

## Definition of Done
### Per Slice
A slice is complete only if:
- it cites the exact legacy actions it covers
- it documents reuse vs newly implemented behavior honestly
- the menu path, label, and shortcut match the legacy contract unless an intentional divergence is documented
- handlers are real for the scope of that slice
- targeted tests pass
- parity audit for the slice passes
- GSD state is updated with the correct slice evidence

### For the Full Epic
The epic is complete only if:
- the Python top-level menu tree matches the legacy editor structure
- all intended legacy menu groups are either implemented or explicitly documented as out of scope
- a final parity audit against `menubar.xml` passes
- the root Python shell is no longer a simplified placeholder shell

## Risks
- Blindly porting the prior M5 shell slice would preserve the wrong menu taxonomy.
- Allowing `MainWindow` to absorb too much inline logic would make parity fragile and hard to test.
- Mixing structural parity and large functional backends in one slice would make review quality collapse.
- Reusing prior verified history without documenting the new delta would make GSD history inaccurate.

## Mitigations
- Build contract and registry first.
- Keep slices narrow and domain-based.
- Use operator-style orchestration with one implementer write set at a time.
- Require parity audit before slice closeout.

## Acceptance Criteria
- A written implementation plan can be derived slice-by-slice from this spec.
- The plan can execute under GSD with honest dependency tracking.
- The execution model supports multi-agent orchestration without write-set conflicts.
- The resulting shell can converge to full legacy menu parity without inventing a second product design.
