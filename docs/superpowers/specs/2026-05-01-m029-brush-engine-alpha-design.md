# M029 Brush Engine Alpha Design

## Source

- GitHub Issue: #72 `Roadmap: Phase 3 - Brush Engine and Toolset`
- Approved by user on 2026-05-01 after issue triage.
- Worktree: `.worktrees/m029-brush-engine-alpha`
- Branch: `gsd/M029/S01`

## Goal

Build the first Rust-core brush engine foundation for legacy-compatible terrain editing. This milestone establishes stable brush metadata, selection, and placement command contracts for ground and wall brushes without claiming full autoborder or UI parity.

## Legacy Evidence

Legacy source of truth lives under `remeres-map-editor-redux`:

- `source/brushes/brush.h`
- `source/brushes/brush.cpp`
- `source/brushes/brush_enums.h`
- `source/brushes/managers/brush_manager.h`
- `source/brushes/managers/brush_manager.cpp`
- `source/brushes/ground/ground_brush.h`
- `source/brushes/ground/ground_brush.cpp`
- `source/brushes/wall/wall_brush.h`
- `source/brushes/wall/wall_brush.cpp`
- `source/brushes/ground/auto_border.h`

Relevant legacy behavior:

- `Brush` owns a generated id, palette visibility, collection marker, name, look id, draw, undraw, can-draw, related-items hooks, drag/smear flags, and variation limits.
- `Brushes` stores brushes by name, rejects reserved names `all` and `none`, reports unknown brush types, and supports ground/wall brush types.
- `BrushManager` tracks current brush, previous brush, brush shape, exact size, X/Y size, aspect lock, variation, spawn time, and light/door options.
- `GroundBrush::draw` chooses one configured ground item by chance and places it as tile ground.
- `GroundBrush::undraw` removes tile ground only when that tile belongs to the same ground brush.
- `WallBrush::draw` cleans matching walls, chooses the first available wall item through alignment lists, and places a wall item. Alignment recalculation belongs to later wall border work.
- `WallBrush::canDrag` returns true and `canSmear` returns false.
- `AutoBorder` and border calculators are separate systems and should not be implemented fully in M029.

## Scope

M029/S01 will implement a small, testable Rust brush domain:

- immutable brush definitions for `ground` and `wall`
- legacy enum equivalents for brush shape, brush kind, and wall alignment
- brush catalog lookup by name and id
- validation for reserved names, duplicate names, and unsupported brush kinds
- deterministic placement commands for ground and wall brushes
- related-item collection for ground and wall definitions
- Python bridge only if needed to prove editor shell integration

## Non-Goals

- No full XML brush loader.
- No `borders.xml` parser.
- No autoborder calculation.
- No wall neighbor alignment recalculation.
- No floating tool palette or visual redesign.
- No changes to `pyrme/ui` unless needed for a narrow bridge test.
- No sprite rendering changes.

## Architecture

The Rust core keeps brush behavior data-oriented and independent of Qt. `crates/rme_core/src/brushes.rs` becomes the owner of brush definitions, catalog validation, and pure placement command resolution. `MapModel` remains the owner of tile mutation.

Brush application should produce explicit outcomes:

- `Noop` for unsupported or invalid operations
- `SetGround(item_id)` for ground brush placement
- `AddWall(item_id)` for initial wall placement
- `RemoveGround(item_id)` or equivalent internal result when undrawing becomes necessary

The first slice should keep randomness out of the hot path. If a ground brush has weighted items, tests should use deterministic selection through an explicit variation/index input. Real randomization can be added later behind the same contract.

## Data Flow

1. UI or Python shell identifies an active brush by id or name.
2. Rust `BrushCatalog` resolves the brush definition.
3. Brush engine creates a placement command from brush kind, target tile, and optional variation.
4. Editor shell applies the command to `MapModel`.
5. Tests assert tile ground/items and changed/no-op status.

## Error Handling

- Reserved names `all` and `none` are rejected with stable error text.
- Duplicate brush names are rejected.
- Unknown brush kinds are rejected.
- Empty ground item lists produce no placement command.
- Empty wall item lists produce no placement command.
- Invalid variation indexes fall back to deterministic first item.

## Testing

Use TDD. Primary tests should live in Rust near `crates/rme_core/src/brushes.rs` and `crates/rme_core/src/editor.rs`.

Required verification:

- `cargo test -p rme_core brushes`
- `cargo test -p rme_core editor`
- targeted Python bridge tests only if a Python seam changes
- `npm run preflight`

## Acceptance

- Brush catalog is no longer an empty placeholder.
- Ground brush can place a configured ground item through Rust core.
- Wall brush can add a configured wall item through Rust core.
- Catalog validation covers reserved, duplicate, and unknown brush definitions.
- Existing Python activation behavior remains unchanged.
- M030 remains the explicit follow-up for configurable autoborder rules.
