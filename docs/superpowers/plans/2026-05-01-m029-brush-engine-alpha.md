# M029 Brush Engine Alpha Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Rust `BrushCatalog` placeholder with a tested ground/wall brush contract that can resolve legacy-style brush definitions and apply deterministic placement commands.

**Architecture:** `crates/rme_core/src/brushes.rs` owns brush definitions, catalog validation, lookup, related-item collection, and pure placement command resolution. `crates/rme_core/src/map.rs` owns tile mutation by applying resolved placement commands to `MapModel`. Python/UI activation remains unchanged unless tests prove a bridge seam is required.

**Tech Stack:** Rust 2021, `rme_core`, Cargo tests, existing Python shell tests for regression verification.

---

## File Structure

- Modify `crates/rme_core/src/brushes.rs`: brush enums, definitions, validation errors, catalog lookup, placement command resolution, and Rust unit tests.
- Modify `crates/rme_core/src/map.rs`: apply brush placement commands to sparse tile storage and add Rust unit tests.
- Modify `crates/rme_core/src/editor.rs`: only if the final task needs an explicit `EditorShellState` bridge; otherwise run existing editor tests unchanged.
- Create `.gsd/milestones/M029-brush-engine-alpha/slices/S01/S01-PLAN.md`: GSD slice tracker.
- Create `.gsd/milestones/M029-brush-engine-alpha/slices/S01/tasks/.gitkeep`: task directory anchor.
- Update `.gsd/STATE.md`: active milestone/slice set to M029/S01 planning.

## Task 1: Brush Catalog Definitions

**Files:**
- Modify: `crates/rme_core/src/brushes.rs`
- Test: `crates/rme_core/src/brushes.rs`

- [ ] **Step 1: Write failing catalog tests**

Add this test module to `crates/rme_core/src/brushes.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    fn ground(name: &str, id: u32, item_ids: &[u16]) -> BrushDefinition {
        BrushDefinition::Ground(GroundBrushDefinition {
            id,
            name: name.to_string(),
            look_id: item_ids.first().copied().unwrap_or_default(),
            ground_items: item_ids.to_vec(),
            visible_in_palette: true,
            uses_collection: false,
            max_variation: item_ids.len().saturating_sub(1) as u8,
        })
    }

    fn wall(name: &str, id: u32, item_ids: &[u16]) -> BrushDefinition {
        BrushDefinition::Wall(WallBrushDefinition {
            id,
            name: name.to_string(),
            look_id: item_ids.first().copied().unwrap_or_default(),
            wall_items: item_ids.to_vec(),
            visible_in_palette: true,
            uses_collection: false,
        })
    }

    #[test]
    fn brush_catalog_rejects_reserved_names() {
        let err = BrushCatalog::from_definitions(vec![ground("all", 1, &[4526])]).unwrap_err();
        assert_eq!(err.to_string(), "Reserved brush name: all");

        let err = BrushCatalog::from_definitions(vec![wall("none", 2, &[3361])]).unwrap_err();
        assert_eq!(err.to_string(), "Reserved brush name: none");
    }

    #[test]
    fn brush_catalog_rejects_duplicate_names() {
        let err = BrushCatalog::from_definitions(vec![
            ground("grass", 1, &[4526]),
            wall("grass", 2, &[3361]),
        ])
        .unwrap_err();
        assert_eq!(err.to_string(), "Duplicate brush name: grass");
    }

    #[test]
    fn brush_catalog_resolves_by_name_and_id() {
        let catalog = BrushCatalog::from_definitions(vec![
            ground("grass", 10, &[4526, 4527]),
            wall("stone wall", 20, &[3361]),
        ])
        .unwrap();

        assert_eq!(catalog.len(), 2);
        assert_eq!(catalog.get_by_name("grass").unwrap().id(), 10);
        assert_eq!(catalog.get_by_id(20).unwrap().name(), "stone wall");
        assert!(catalog.get_by_name("missing").is_none());
    }

    #[test]
    fn brush_catalog_collects_related_items() {
        let catalog = BrushCatalog::from_definitions(vec![
            ground("grass", 10, &[4526, 4527]),
            wall("stone wall", 20, &[3361, 3362]),
        ])
        .unwrap();

        assert_eq!(catalog.get_by_name("grass").unwrap().related_items(), vec![4526, 4527]);
        assert_eq!(catalog.get_by_name("stone wall").unwrap().related_items(), vec![3361, 3362]);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cargo test -p rme_core brushes --quiet
```

Expected: FAIL with missing `BrushDefinition`, `GroundBrushDefinition`, `WallBrushDefinition`, and `BrushCatalog::from_definitions`.

- [ ] **Step 3: Implement catalog definitions**

Replace placeholder content in `crates/rme_core/src/brushes.rs` with:

```rust
//! Brush-domain primitives for the Rust core.
//!
//! Mirrors the first stable subset of legacy RME brush behavior without Qt,
//! XML loading, or autoborder calculation.

use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BrushShape {
    Circle,
    Square,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BrushKind {
    Ground,
    Wall,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WallAlignment {
    Pole,
    SouthEnd,
    EastEnd,
    NorthwestDiagonal,
    WestEnd,
    NortheastDiagonal,
    Horizontal,
    SouthT,
    NorthEnd,
    Vertical,
    SouthwestDiagonal,
    EastT,
    SoutheastDiagonal,
    WestT,
    NorthT,
    Intersection,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GroundBrushDefinition {
    pub id: u32,
    pub name: String,
    pub look_id: u16,
    pub ground_items: Vec<u16>,
    pub visible_in_palette: bool,
    pub uses_collection: bool,
    pub max_variation: u8,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WallBrushDefinition {
    pub id: u32,
    pub name: String,
    pub look_id: u16,
    pub wall_items: Vec<u16>,
    pub visible_in_palette: bool,
    pub uses_collection: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BrushDefinition {
    Ground(GroundBrushDefinition),
    Wall(WallBrushDefinition),
}

impl BrushDefinition {
    pub const fn kind(&self) -> BrushKind {
        match self {
            Self::Ground(_) => BrushKind::Ground,
            Self::Wall(_) => BrushKind::Wall,
        }
    }

    pub fn id(&self) -> u32 {
        match self {
            Self::Ground(definition) => definition.id,
            Self::Wall(definition) => definition.id,
        }
    }

    pub fn name(&self) -> &str {
        match self {
            Self::Ground(definition) => &definition.name,
            Self::Wall(definition) => &definition.name,
        }
    }

    pub fn look_id(&self) -> u16 {
        match self {
            Self::Ground(definition) => definition.look_id,
            Self::Wall(definition) => definition.look_id,
        }
    }

    pub fn visible_in_palette(&self) -> bool {
        match self {
            Self::Ground(definition) => definition.visible_in_palette,
            Self::Wall(definition) => definition.visible_in_palette,
        }
    }

    pub fn uses_collection(&self) -> bool {
        match self {
            Self::Ground(definition) => definition.uses_collection,
            Self::Wall(definition) => definition.uses_collection,
        }
    }

    pub fn related_items(&self) -> Vec<u16> {
        match self {
            Self::Ground(definition) => definition.ground_items.clone(),
            Self::Wall(definition) => definition.wall_items.clone(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BrushCatalogError {
    ReservedName(String),
    DuplicateName(String),
    DuplicateId(u32),
}

impl fmt::Display for BrushCatalogError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ReservedName(name) => write!(f, "Reserved brush name: {name}"),
            Self::DuplicateName(name) => write!(f, "Duplicate brush name: {name}"),
            Self::DuplicateId(id) => write!(f, "Duplicate brush id: {id}"),
        }
    }
}

impl Error for BrushCatalogError {}

#[derive(Debug, Default, Clone)]
pub struct BrushCatalog {
    brushes: Vec<BrushDefinition>,
    by_name: BTreeMap<String, usize>,
    by_id: BTreeMap<u32, usize>,
}

impl BrushCatalog {
    pub const fn new() -> Self {
        Self {
            brushes: Vec::new(),
            by_name: BTreeMap::new(),
            by_id: BTreeMap::new(),
        }
    }

    pub fn from_definitions(definitions: Vec<BrushDefinition>) -> Result<Self, BrushCatalogError> {
        let mut by_name = BTreeMap::new();
        let mut by_id = BTreeMap::new();
        let mut seen_names = BTreeSet::new();
        let mut seen_ids = BTreeSet::new();

        for (index, definition) in definitions.iter().enumerate() {
            let name = definition.name();
            if name == "all" || name == "none" {
                return Err(BrushCatalogError::ReservedName(name.to_string()));
            }
            if !seen_names.insert(name.to_string()) {
                return Err(BrushCatalogError::DuplicateName(name.to_string()));
            }
            if !seen_ids.insert(definition.id()) {
                return Err(BrushCatalogError::DuplicateId(definition.id()));
            }
            by_name.insert(name.to_string(), index);
            by_id.insert(definition.id(), index);
        }

        Ok(Self {
            brushes: definitions,
            by_name,
            by_id,
        })
    }

    pub fn len(&self) -> usize {
        self.brushes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.brushes.is_empty()
    }

    pub fn get_by_name(&self, name: &str) -> Option<&BrushDefinition> {
        self.by_name
            .get(name)
            .and_then(|index| self.brushes.get(*index))
    }

    pub fn get_by_id(&self, id: u32) -> Option<&BrushDefinition> {
        self.by_id.get(&id).and_then(|index| self.brushes.get(*index))
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
cargo test -p rme_core brushes --quiet
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/brushes.rs
git commit -m "feat(M029/S01): add brush catalog contract"
```

## Task 2: Placement Command Resolution

**Files:**
- Modify: `crates/rme_core/src/brushes.rs`
- Test: `crates/rme_core/src/brushes.rs`

- [ ] **Step 1: Write failing placement tests**

Add these tests inside the existing `#[cfg(test)] mod tests` in `crates/rme_core/src/brushes.rs`:

```rust
    #[test]
    fn ground_brush_resolves_deterministic_placement() {
        let catalog = BrushCatalog::from_definitions(vec![ground("grass", 10, &[4526, 4527])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("grass", Some(1)),
            BrushPlacementCommand::SetGround { item_id: 4527 }
        );
        assert_eq!(
            catalog.placement_command_by_name("grass", Some(99)),
            BrushPlacementCommand::SetGround { item_id: 4526 }
        );
    }

    #[test]
    fn empty_ground_brush_resolves_noop() {
        let catalog = BrushCatalog::from_definitions(vec![ground("empty ground", 10, &[])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("empty ground", None),
            BrushPlacementCommand::Noop
        );
    }

    #[test]
    fn wall_brush_resolves_first_wall_item() {
        let catalog = BrushCatalog::from_definitions(vec![wall("stone wall", 20, &[3361, 3362])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("stone wall", None),
            BrushPlacementCommand::AddWall { item_id: 3361 }
        );
    }

    #[test]
    fn missing_brush_resolves_noop() {
        let catalog = BrushCatalog::from_definitions(vec![wall("stone wall", 20, &[3361])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("missing", None),
            BrushPlacementCommand::Noop
        );
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cargo test -p rme_core brushes --quiet
```

Expected: FAIL with missing `BrushPlacementCommand` and `placement_command_by_name`.

- [ ] **Step 3: Implement placement command resolution**

Add this enum and methods to `crates/rme_core/src/brushes.rs`:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BrushPlacementCommand {
    Noop,
    SetGround { item_id: u16 },
    AddWall { item_id: u16 },
}

impl BrushDefinition {
    pub fn placement_command(&self, variation_index: Option<usize>) -> BrushPlacementCommand {
        match self {
            Self::Ground(definition) => {
                let Some(first) = definition.ground_items.first().copied() else {
                    return BrushPlacementCommand::Noop;
                };
                let item_id = variation_index
                    .and_then(|index| definition.ground_items.get(index).copied())
                    .unwrap_or(first);
                BrushPlacementCommand::SetGround { item_id }
            }
            Self::Wall(definition) => definition
                .wall_items
                .first()
                .copied()
                .map(|item_id| BrushPlacementCommand::AddWall { item_id })
                .unwrap_or(BrushPlacementCommand::Noop),
        }
    }
}

impl BrushCatalog {
    pub fn placement_command_by_name(
        &self,
        name: &str,
        variation_index: Option<usize>,
    ) -> BrushPlacementCommand {
        self.get_by_name(name)
            .map(|definition| definition.placement_command(variation_index))
            .unwrap_or(BrushPlacementCommand::Noop)
    }

    pub fn placement_command_by_id(
        &self,
        id: u32,
        variation_index: Option<usize>,
    ) -> BrushPlacementCommand {
        self.get_by_id(id)
            .map(|definition| definition.placement_command(variation_index))
            .unwrap_or(BrushPlacementCommand::Noop)
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
cargo test -p rme_core brushes --quiet
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/brushes.rs
git commit -m "feat(M029/S01): resolve brush placement commands"
```

## Task 3: MapModel Brush Command Application

**Files:**
- Modify: `crates/rme_core/src/map.rs`
- Test: `crates/rme_core/src/map.rs`

- [ ] **Step 1: Write failing map tests**

Add this test module near the existing tests in `crates/rme_core/src/map.rs`:

```rust
#[cfg(test)]
mod brush_command_tests {
    use super::*;
    use crate::brushes::BrushPlacementCommand;

    #[test]
    fn apply_brush_command_sets_ground() {
        let mut map = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);

        assert!(map.apply_brush_command(pos, BrushPlacementCommand::SetGround { item_id: 4526 }));
        let tile = map.get_tile(&pos).unwrap();
        assert_eq!(tile.ground().map(Item::id), Some(4526));
        assert!(tile.items().is_empty());
        assert!(tile.is_modified());
    }

    #[test]
    fn apply_brush_command_same_ground_is_noop() {
        let mut map = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);

        assert!(map.apply_brush_command(pos, BrushPlacementCommand::SetGround { item_id: 4526 }));
        assert!(!map.apply_brush_command(pos, BrushPlacementCommand::SetGround { item_id: 4526 }));
    }

    #[test]
    fn apply_brush_command_adds_wall_item() {
        let mut map = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);

        assert!(map.apply_brush_command(pos, BrushPlacementCommand::AddWall { item_id: 3361 }));
        let tile = map.get_tile(&pos).unwrap();
        assert_eq!(tile.items().iter().map(Item::id).collect::<Vec<_>>(), vec![3361]);
        assert!(tile.is_modified());
    }

    #[test]
    fn apply_brush_command_noop_does_not_create_tile() {
        let mut map = MapModel::new();
        let pos = MapPosition::new(100, 200, 7);

        assert!(!map.apply_brush_command(pos, BrushPlacementCommand::Noop));
        assert!(map.get_tile(&pos).is_none());
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cargo test -p rme_core brush_command_tests --quiet
```

Expected: FAIL with missing `MapModel::apply_brush_command`.

- [ ] **Step 3: Implement map mutation**

In `crates/rme_core/src/map.rs`, add import:

```rust
use crate::brushes::BrushPlacementCommand;
```

Add method inside `impl MapModel`:

```rust
    pub fn apply_brush_command(
        &mut self,
        position: MapPosition,
        command: BrushPlacementCommand,
    ) -> bool {
        match command {
            BrushPlacementCommand::Noop => false,
            BrushPlacementCommand::SetGround { item_id } => {
                let changed = {
                    let tile = self.get_or_create_tile(position);
                    if tile.ground().map(Item::id) == Some(item_id) {
                        false
                    } else {
                        tile.set_ground(Some(Item::new(item_id)));
                        tile.mark_modified();
                        true
                    }
                };
                if changed {
                    self.generation += 1;
                    self.is_dirty = true;
                }
                changed
            }
            BrushPlacementCommand::AddWall { item_id } => {
                {
                    let tile = self.get_or_create_tile(position);
                    tile.add_item(Item::new(item_id));
                    tile.mark_modified();
                }
                self.generation += 1;
                self.is_dirty = true;
                true
            }
        }
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
cargo test -p rme_core brush_command_tests --quiet
```

Expected: PASS.

- [ ] **Step 5: Run adjacent Rust tests**

Run:

```bash
cargo test -p rme_core map::tests --quiet
cargo test -p rme_core editor::tests --quiet
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add crates/rme_core/src/map.rs
git commit -m "feat(M029/S01): apply brush commands to map"
```

## Task 4: Editor Regression and GSD Closeout

**Files:**
- Modify: `.gsd/milestones/M029-brush-engine-alpha/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M029-brush-engine-alpha/slices/S01/tasks/T04-SUMMARY.md`
- Modify: `.gsd/STATE.md`
- Test: existing Rust/Python targeted commands

- [ ] **Step 1: Run targeted verification**

Run:

```bash
cargo test -p rme_core brushes --quiet
cargo test -p rme_core brush_command_tests --quiet
cargo test -p rme_core editor::tests --quiet
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/python/test_editor_activation_backend.py tests/python/test_rme_core_editor_shell.py -q --tb=short
npm run preflight
```

Expected: all commands exit 0.

- [ ] **Step 2: Write task summary**

Create `.gsd/milestones/M029-brush-engine-alpha/slices/S01/tasks/T04-SUMMARY.md`:

```markdown
# T04 Summary - M029/S01 Brush Engine Alpha

## Scope

- Added Rust brush catalog definitions for ground and wall brush metadata.
- Added catalog validation for reserved names, duplicate names, and duplicate ids.
- Added deterministic placement command resolution.
- Added `MapModel::apply_brush_command` for ground and wall placement.
- Preserved current Python activation behavior.

## Legacy Evidence

- `remeres-map-editor-redux/source/brushes/brush.h`
- `remeres-map-editor-redux/source/brushes/brush.cpp`
- `remeres-map-editor-redux/source/brushes/ground/ground_brush.cpp`
- `remeres-map-editor-redux/source/brushes/wall/wall_brush.cpp`

## Verification

- `cargo test -p rme_core brushes --quiet`
- `cargo test -p rme_core brush_command_tests --quiet`
- `cargo test -p rme_core editor::tests --quiet`
- `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/python/test_editor_activation_backend.py tests/python/test_rme_core_editor_shell.py -q --tb=short`
- `npm run preflight`

## Follow-up

- M030 owns autoborder parsing and neighbor alignment.
- UI tool palette integration remains out of M029/S01.
```

- [ ] **Step 3: Mark S01 plan complete**

Edit `.gsd/milestones/M029-brush-engine-alpha/slices/S01/S01-PLAN.md` and mark all completed tasks with `[x]`.

- [ ] **Step 4: Update state**

Edit `.gsd/STATE.md`:

```markdown
**Active Milestone:** none
**Active Slice:** none
**Active Task:** none
**Phase:** discovery
**Next Action:** Review M029/S01 PR and plan M030-autoborder-rules after merge.
```

Add recent decision:

```markdown
- `M029-brush-engine-alpha` is complete: Rust `BrushCatalog` now validates ground/wall brush definitions and `MapModel` applies deterministic brush placement commands while autoborder remains deferred to M030.
```

- [ ] **Step 5: Caveman review diff**

Run:

```bash
git diff --stat
git diff --cached --stat
git diff --check
```

Expected: no whitespace errors. Review diff against this plan before commit.

- [ ] **Step 6: Commit closeout**

```bash
git add .gsd/STATE.md .gsd/milestones/M029-brush-engine-alpha/slices/S01/S01-PLAN.md .gsd/milestones/M029-brush-engine-alpha/slices/S01/tasks/T04-SUMMARY.md
git commit -m "docs(M029/S01): close brush engine alpha"
```

## Final Verification Before PR

Run:

```bash
cargo test -p rme_core brushes --quiet
cargo test -p rme_core brush_command_tests --quiet
cargo test -p rme_core editor::tests --quiet
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/python/test_editor_activation_backend.py tests/python/test_rme_core_editor_shell.py -q --tb=short
npm run preflight
git status --short --branch --untracked-files=no
```

Expected: tests pass and tracked worktree is clean.
