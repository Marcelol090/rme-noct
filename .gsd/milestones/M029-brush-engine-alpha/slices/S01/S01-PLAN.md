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

- [x] RED: catalog rejects reserved names `all` and `none`
- [x] RED: catalog rejects duplicate names
- [x] RED: catalog resolves brushes by name and id
- [x] RED: catalog exposes related item ids for ground/wall brushes
- [x] GREEN: replace placeholder `BrushCatalog` with definitions and validation
- [x] VERIFY: `cargo test -p rme_core brushes --quiet`

### T02 - Placement command resolution

- [x] RED: ground brush resolves deterministic ground item by variation index
- [x] RED: empty ground brush resolves `Noop`
- [x] RED: wall brush resolves first configured wall item
- [x] RED: missing brush resolves `Noop`
- [x] GREEN: add `BrushPlacementCommand` and catalog command resolution
- [x] VERIFY: `cargo test -p rme_core brushes --quiet`

### T03 - MapModel command application

- [x] RED: `SetGround` creates tile and sets ground
- [x] RED: same ground command reports no-op
- [x] RED: `AddWall` appends wall item
- [x] RED: `Noop` does not create tile
- [x] GREEN: add `MapModel::apply_brush_command`
- [x] VERIFY: `cargo test -p rme_core brush_command_tests --quiet`

### T04 - Regression and closeout

- [x] VERIFY: `cargo test -p rme_core editor::tests --quiet`
- [x] VERIFY: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/python/test_editor_activation_backend.py tests/python/test_rme_core_editor_shell.py -q --tb=short`
- [x] VERIFY: `npm run preflight`
- [x] REVIEW: Caveman Review on diff
- [x] SUMMARY: write `tasks/T04-SUMMARY.md`
- [x] STATE: mark M029/S01 complete and route M030 as follow-up

## Non-Goals

- No full XML brush loader.
- No `borders.xml` parser.
- No autoborder calculation.
- No wall neighbor alignment recalculation.
- No floating tool palette or visual redesign.
- No sprite rendering changes.
