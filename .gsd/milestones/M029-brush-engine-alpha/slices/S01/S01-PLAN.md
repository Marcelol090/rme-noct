# S01 Plan - BRUSH-ENGINE-ALPHA-CONTRACT

## Milestone

**M029 - Brush Engine Alpha**

Branch: `gsd/M029/S01`

Worktree: `.worktrees/m029-brush-engine-alpha`

Issue: #72 `Roadmap: Phase 3 - Brush Engine and Toolset`

## Stop Condition

Rust core exposes tested ground/wall brush definitions, catalog validation, deterministic placement command resolution, and `MapModel` command application. Autoborder and UI tool palette remain deferred.

## Tasks

### T01 - Brush catalog definitions

- [ ] RED: catalog rejects reserved names `all` and `none`
- [ ] RED: catalog rejects duplicate names
- [ ] RED: catalog resolves brushes by name and id
- [ ] RED: catalog exposes related item ids for ground/wall brushes
- [ ] GREEN: replace placeholder `BrushCatalog` with definitions and validation
- [ ] VERIFY: `cargo test -p rme_core brushes --quiet`

### T02 - Placement command resolution

- [ ] RED: ground brush resolves deterministic ground item by variation index
- [ ] RED: empty ground brush resolves `Noop`
- [ ] RED: wall brush resolves first configured wall item
- [ ] RED: missing brush resolves `Noop`
- [ ] GREEN: add `BrushPlacementCommand` and catalog command resolution
- [ ] VERIFY: `cargo test -p rme_core brushes --quiet`

### T03 - MapModel command application

- [ ] RED: `SetGround` creates tile and sets ground
- [ ] RED: same ground command reports no-op
- [ ] RED: `AddWall` appends wall item
- [ ] RED: `Noop` does not create tile
- [ ] GREEN: add `MapModel::apply_brush_command`
- [ ] VERIFY: `cargo test -p rme_core brush_command_tests --quiet`

### T04 - Regression and closeout

- [ ] VERIFY: `cargo test -p rme_core editor::tests --quiet`
- [ ] VERIFY: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_editor_activation_backend.py tests/python/test_rme_core_editor_shell.py -q --tb=short`
- [ ] VERIFY: `npm run preflight`
- [ ] REVIEW: Caveman Review on diff
- [ ] SUMMARY: write `tasks/T04-SUMMARY.md`
- [ ] STATE: mark M029/S01 complete and route M030 as follow-up

## Non-Goals

- No full XML brush loader.
- No `borders.xml` parser.
- No autoborder calculation.
- No wall neighbor alignment recalculation.
- No floating tool palette or visual redesign.
- No sprite rendering changes.
