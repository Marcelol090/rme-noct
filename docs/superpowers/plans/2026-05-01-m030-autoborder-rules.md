# M030 Autoborder Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a pure Rust autoborder rule engine that maps legacy edge names and 8-neighbour patterns into deterministic border placement plans.

**Architecture:** `crates/rme_core/src/autoborder.rs` owns legacy edge-name mapping, rule validation, neighbourhood encoding, and stable plan resolution. `crates/rme_core/src/lib.rs` exposes the module and nothing else in this slice. The current `BrushCatalog` and `MapModel` seams stay unchanged until a later slice consumes `AutoborderPlan`.

**Tech Stack:** Rust 2021, `rme_core`, Cargo tests, legacy RME C++ sources as behavioral oracle.

---

## File Structure

- Create: `crates/rme_core/src/autoborder.rs`
- Modify: `crates/rme_core/src/lib.rs`
- Create: `.gsd/milestones/M030-autoborder-rules/slices/S01/S01-SUMMARY.md`
- Create: `.gsd/milestones/M030-autoborder-rules/slices/S01/tasks/T01-SUMMARY.md`
- Create: `.gsd/milestones/M030-autoborder-rules/slices/S01/tasks/T02-SUMMARY.md`
- Modify: `.gsd/milestones/M030-autoborder-rules/slices/S01/S01-PLAN.md`
- Modify: `.gsd/STATE.md`

## Task 1: Pure edge contract and rule model

**Files:**
- Create: `crates/rme_core/src/autoborder.rs`
- Modify: `crates/rme_core/src/lib.rs`

- [ ] **Step 1: Write failing tests for edge mapping and validation**

Add this test module to `crates/rme_core/src/autoborder.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    fn auto_border(id: u32, group: u16, edge: BorderType, item_id: u16) -> AutoBorderDefinition {
        let mut tiles = [0; 13];
        tiles[border_type_index(edge)] = item_id;
        AutoBorderDefinition {
            id,
            group,
            ground: true,
            tiles,
        }
    }

    fn rule(id: u32, name: &str, edge: BorderType, item_id: u16) -> GroundBorderRule {
        GroundBorderRule {
            id,
            name: name.to_string(),
            outer: true,
            to: BorderTarget::All,
            autoborder: auto_border(id, 0, edge, item_id),
            optional_autoborder: None,
        }
    }

    #[test]
    fn edge_names_match_legacy_contract() {
        assert_eq!(edge_name_to_border_type("n").unwrap(), BorderType::NorthHorizontal);
        assert_eq!(edge_name_to_border_type("w").unwrap(), BorderType::WestHorizontal);
        assert_eq!(edge_name_to_border_type("s").unwrap(), BorderType::SouthHorizontal);
        assert_eq!(edge_name_to_border_type("e").unwrap(), BorderType::EastHorizontal);
        assert_eq!(edge_name_to_border_type("cnw").unwrap(), BorderType::NorthWestCorner);
        assert_eq!(edge_name_to_border_type("cne").unwrap(), BorderType::NorthEastCorner);
        assert_eq!(edge_name_to_border_type("csw").unwrap(), BorderType::SouthWestCorner);
        assert_eq!(edge_name_to_border_type("cse").unwrap(), BorderType::SouthEastCorner);
        assert_eq!(edge_name_to_border_type("dnw").unwrap(), BorderType::NorthWestDiagonal);
        assert_eq!(edge_name_to_border_type("dne").unwrap(), BorderType::NorthEastDiagonal);
        assert_eq!(edge_name_to_border_type("dsw").unwrap(), BorderType::SouthWestDiagonal);
        assert_eq!(edge_name_to_border_type("dse").unwrap(), BorderType::SouthEastDiagonal);
    }

    #[test]
    fn edge_names_reject_unknown_values() {
        let err = edge_name_to_border_type("north").unwrap_err();
        assert_eq!(err.to_string(), "Unknown autoborder edge: north");
    }

    #[test]
    fn validation_rejects_duplicate_rule_ids() {
        let err = validate_ground_border_rules(&[
            rule(7, "grass", BorderType::NorthHorizontal, 4526),
            rule(7, "snow", BorderType::SouthHorizontal, 4527),
        ])
        .unwrap_err();
        assert_eq!(err.to_string(), "Duplicate autoborder rule id: 7");
    }

    #[test]
    fn validation_rejects_duplicate_rule_names() {
        let err = validate_ground_border_rules(&[
            rule(7, "grass", BorderType::NorthHorizontal, 4526),
            rule(8, "grass", BorderType::SouthHorizontal, 4527),
        ])
        .unwrap_err();
        assert_eq!(err.to_string(), "Duplicate autoborder rule name: grass");
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cargo test -p rme_core autoborder --quiet
```

Expected: FAIL with missing `autoborder` module, `BorderType`, `GroundBorderRule`, and validation helpers.

- [ ] **Step 3: Implement the minimal edge contract**

Add the module export in `crates/rme_core/src/lib.rs`:

```rust
pub mod autoborder;
```

Implement `crates/rme_core/src/autoborder.rs`:

```rust
use std::collections::BTreeSet;
use std::error::Error;
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum BorderType {
    None,
    NorthHorizontal,
    EastHorizontal,
    SouthHorizontal,
    WestHorizontal,
    NorthWestCorner,
    NorthEastCorner,
    SouthWestCorner,
    SouthEastCorner,
    NorthWestDiagonal,
    NorthEastDiagonal,
    SouthEastDiagonal,
    SouthWestDiagonal,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BorderTarget {
    All,
    None,
    Brush(u32),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AutoBorderDefinition {
    pub id: u32,
    pub group: u16,
    pub ground: bool,
    pub tiles: [u16; 13],
}

impl AutoBorderDefinition {
    pub fn item_for(&self, border_type: BorderType) -> Option<u16> {
        let item_id = self.tiles[border_type_index(border_type)];
        if item_id == 0 {
            None
        } else {
            Some(item_id)
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GroundBorderRule {
    pub id: u32,
    pub name: String,
    pub outer: bool,
    pub to: BorderTarget,
    pub autoborder: AutoBorderDefinition,
    pub optional_autoborder: Option<AutoBorderDefinition>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AutoborderError {
    UnknownEdge(String),
    DuplicateRuleId(u32),
    DuplicateRuleName(String),
}

impl fmt::Display for AutoborderError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnknownEdge(edge) => write!(f, "Unknown autoborder edge: {edge}"),
            Self::DuplicateRuleId(id) => write!(f, "Duplicate autoborder rule id: {id}"),
            Self::DuplicateRuleName(name) => write!(f, "Duplicate autoborder rule name: {name}"),
        }
    }
}

impl Error for AutoborderError {}

pub fn edge_name_to_border_type(edge: &str) -> Result<BorderType, AutoborderError> {
    match edge {
        "n" => Ok(BorderType::NorthHorizontal),
        "w" => Ok(BorderType::WestHorizontal),
        "s" => Ok(BorderType::SouthHorizontal),
        "e" => Ok(BorderType::EastHorizontal),
        "cnw" => Ok(BorderType::NorthWestCorner),
        "cne" => Ok(BorderType::NorthEastCorner),
        "csw" => Ok(BorderType::SouthWestCorner),
        "cse" => Ok(BorderType::SouthEastCorner),
        "dnw" => Ok(BorderType::NorthWestDiagonal),
        "dne" => Ok(BorderType::NorthEastDiagonal),
        "dsw" => Ok(BorderType::SouthWestDiagonal),
        "dse" => Ok(BorderType::SouthEastDiagonal),
        _ => Err(AutoborderError::UnknownEdge(edge.to_string())),
    }
}

pub fn validate_ground_border_rules(rules: &[GroundBorderRule]) -> Result<(), AutoborderError> {
    let mut ids = BTreeSet::new();
    let mut names = BTreeSet::new();
    for rule in rules {
        if !ids.insert(rule.id) {
            return Err(AutoborderError::DuplicateRuleId(rule.id));
        }
        if !names.insert(rule.name.clone()) {
            return Err(AutoborderError::DuplicateRuleName(rule.name.clone()));
        }
    }
    Ok(())
}

const fn border_type_index(border_type: BorderType) -> usize {
    match border_type {
        BorderType::None => 0,
        BorderType::NorthHorizontal => 1,
        BorderType::EastHorizontal => 2,
        BorderType::SouthHorizontal => 3,
        BorderType::WestHorizontal => 4,
        BorderType::NorthWestCorner => 5,
        BorderType::NorthEastCorner => 6,
        BorderType::SouthWestCorner => 7,
        BorderType::SouthEastCorner => 8,
        BorderType::NorthWestDiagonal => 9,
        BorderType::NorthEastDiagonal => 10,
        BorderType::SouthEastDiagonal => 11,
        BorderType::SouthWestDiagonal => 12,
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
cargo test -p rme_core autoborder --quiet
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/autoborder.rs crates/rme_core/src/lib.rs
git commit -m "feat(M030/S01): add autoborder edge contract"
```

## Task 2: Deterministic resolver and stable plan output

**Files:**
- Modify: `crates/rme_core/src/autoborder.rs`

- [ ] **Step 1: Write failing resolver tests**

Add these tests to the same `#[cfg(test)]` module:

```rust
    const NW: u8 = 1 << 0;
    const N: u8 = 1 << 1;
    const NE: u8 = 1 << 2;
    const W: u8 = 1 << 3;
    const E: u8 = 1 << 4;
    const SW: u8 = 1 << 5;
    const S: u8 = 1 << 6;
    const SE: u8 = 1 << 7;

    fn mask(bits: &[u8]) -> u8 {
        bits.iter().copied().fold(0, |acc, bit| acc | bit)
    }

    fn neighborhood(center: Option<u32>, neighbors: [AutoborderNeighbor; 8]) -> AutoborderNeighborhood {
        AutoborderNeighborhood { center, neighbors }
    }

    #[test]
    fn legacy_mask_translation_matches_cpp_patterns() {
        assert_eq!(
            legacy_border_types_from_mask(mask(&[N, W])),
            [
                BorderType::NorthWestDiagonal,
                BorderType::None,
                BorderType::None,
                BorderType::None,
            ]
        );
        assert_eq!(
            legacy_border_types_from_mask(mask(&[N, E, W])),
            [
                BorderType::NorthHorizontal,
                BorderType::EastHorizontal,
                BorderType::WestHorizontal,
                BorderType::None,
            ]
        );
    }

    #[test]
    fn empty_neighborhood_returns_empty_plan() {
        let rules = vec![rule(7, "grass", BorderType::NorthHorizontal, 4526)];
        let plan = resolve_autoborder_plan(
            &rules,
            &neighborhood(None, [AutoborderNeighbor::Empty; 8]),
        )
        .unwrap();
        assert!(plan.placements().is_empty());
    }

    #[test]
    fn optional_border_is_emitted_before_regular_border() {
        let regular = auto_border(7, 0, BorderType::NorthHorizontal, 5001);
        let optional = auto_border(7, 0, BorderType::NorthHorizontal, 5000);
        let rules = vec![GroundBorderRule {
            id: 7,
            name: "grass".to_string(),
            outer: true,
            to: BorderTarget::All,
            autoborder: regular,
            optional_autoborder: Some(optional),
        }];
        let plan = resolve_autoborder_plan(
            &rules,
            &neighborhood(Some(7), [AutoborderNeighbor::Brush(99); 8]),
        )
        .unwrap();

        assert_eq!(plan.placements()[0].item_id, 5000);
        assert_eq!(plan.placements()[1].item_id, 5001);
    }

    #[test]
    fn resolver_is_stable_for_repeated_input() {
        let rules = vec![rule(7, "grass", BorderType::NorthHorizontal, 4526)];
        let neighborhood = neighborhood(Some(7), [AutoborderNeighbor::Brush(1); 8]);

        let first = resolve_autoborder_plan(&rules, &neighborhood).unwrap();
        let second = resolve_autoborder_plan(&rules, &neighborhood).unwrap();

        assert_eq!(first, second);
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cargo test -p rme_core autoborder --quiet
```

Expected: FAIL with missing `AutoborderNeighbor`, `AutoborderNeighborhood`, `AutoborderPlacement`, `AutoborderPlan`, `legacy_border_types_from_mask`, and `resolve_autoborder_plan`.

- [ ] **Step 3: Implement the resolver**

Add these types and helpers to `crates/rme_core/src/autoborder.rs`:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AutoborderNeighbor {
    Empty,
    Brush(u32),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AutoborderNeighborhood {
    pub center: Option<u32>,
    pub neighbors: [AutoborderNeighbor; 8],
}

impl AutoborderNeighborhood {
    pub const fn empty() -> Self {
        Self {
            center: None,
            neighbors: [AutoborderNeighbor::Empty; 8],
        }
    }

    pub fn mask_for(&self, target: BorderTarget) -> u8 {
        self.neighbors
            .iter()
            .enumerate()
            .fold(0, |mask, (index, neighbor)| {
                let matches = match (target, neighbor) {
                    (BorderTarget::All, AutoborderNeighbor::Brush(_)) => true,
                    (BorderTarget::None, AutoborderNeighbor::Empty) => true,
                    (BorderTarget::Brush(expected), AutoborderNeighbor::Brush(actual)) => {
                        *actual == expected
                    }
                    _ => false,
                };
                if matches {
                    mask | (1 << index)
                } else {
                    mask
                }
            })
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct AutoborderPlacement {
    pub rule_id: u32,
    pub item_id: u16,
    pub alignment_mask: u8,
    pub outer: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AutoborderPlan {
    placements: Vec<AutoborderPlacement>,
}

impl AutoborderPlan {
    pub fn empty() -> Self {
        Self {
            placements: Vec::new(),
        }
    }

    pub fn placements(&self) -> &[AutoborderPlacement] {
        &self.placements
    }
}

pub fn legacy_border_types_from_mask(mask: u8) -> [BorderType; 4] {
    let has_n = mask & (1 << 1) != 0;
    let has_w = mask & (1 << 3) != 0;
    let has_e = mask & (1 << 4) != 0;
    let has_s = mask & (1 << 6) != 0;
    let cardinal_count = [has_n, has_w, has_e, has_s]
        .into_iter()
        .filter(|present| *present)
        .count();

    if cardinal_count == 2 {
        if has_n && has_w {
            return [
                BorderType::NorthWestDiagonal,
                BorderType::None,
                BorderType::None,
                BorderType::None,
            ];
        }
        if has_n && has_e {
            return [
                BorderType::NorthEastDiagonal,
                BorderType::None,
                BorderType::None,
                BorderType::None,
            ];
        }
        if has_s && has_w {
            return [
                BorderType::SouthWestDiagonal,
                BorderType::None,
                BorderType::None,
                BorderType::None,
            ];
        }
        if has_s && has_e {
            return [
                BorderType::SouthEastDiagonal,
                BorderType::None,
                BorderType::None,
                BorderType::None,
            ];
        }
    }

    let mut result = [BorderType::None; 4];
    let mut slot = 0;
    let mut push = |border_type: BorderType| {
        if slot < result.len() {
            result[slot] = border_type;
            slot += 1;
        }
    };

    if has_n {
        push(BorderType::NorthHorizontal);
    }
    if has_e {
        push(BorderType::EastHorizontal);
    }
    if has_s {
        push(BorderType::SouthHorizontal);
    }
    if has_w {
        push(BorderType::WestHorizontal);
    }

    if mask & (1 << 0) != 0 && !has_n && !has_w {
        push(BorderType::NorthWestCorner);
    }
    if mask & (1 << 2) != 0 && !has_n && !has_e {
        push(BorderType::NorthEastCorner);
    }
    if mask & (1 << 5) != 0 && !has_s && !has_w {
        push(BorderType::SouthWestCorner);
    }
    if mask & (1 << 7) != 0 && !has_s && !has_e {
        push(BorderType::SouthEastCorner);
    }

    result
}

pub fn resolve_autoborder_plan(
    rules: &[GroundBorderRule],
    neighborhood: &AutoborderNeighborhood,
) -> Result<AutoborderPlan, AutoborderError> {
    validate_ground_border_rules(rules)?;

    let mut placements = Vec::new();
    for rule in rules {
        let alignment_mask = neighborhood.mask_for(rule.to);
        if alignment_mask == 0 {
            continue;
        }

        let border_types = legacy_border_types_from_mask(alignment_mask);
        if let Some(optional) = &rule.optional_autoborder {
            if let Some(border_type) = border_types
                .into_iter()
                .find(|border_type| *border_type != BorderType::None)
            {
                if let Some(item_id) = optional.item_for(border_type) {
                    placements.push(AutoborderPlacement {
                        rule_id: rule.id,
                        item_id,
                        alignment_mask,
                        outer: rule.outer,
                    });
                }
            }
        }

        for border_type in border_types {
            if border_type == BorderType::None {
                break;
            }
            if let Some(item_id) = rule.autoborder.item_for(border_type) {
                placements.push(AutoborderPlacement {
                    rule_id: rule.id,
                    item_id,
                    alignment_mask,
                    outer: rule.outer,
                });
            }
        }
    }

    Ok(AutoborderPlan { placements })
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
cargo test -p rme_core autoborder --quiet
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add crates/rme_core/src/autoborder.rs
git commit -m "feat(M030/S01): add autoborder resolver"
```

## Task 3: Slice closeout and state recording

**Files:**
- Modify: `.gsd/milestones/M030-autoborder-rules/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M030-autoborder-rules/slices/S01/S01-SUMMARY.md`
- Create: `.gsd/milestones/M030-autoborder-rules/slices/S01/tasks/T01-SUMMARY.md`
- Create: `.gsd/milestones/M030-autoborder-rules/slices/S01/tasks/T02-SUMMARY.md`
- Modify: `.gsd/STATE.md`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
cargo test -p rme_core autoborder --quiet
git diff --check
```

Expected: exit 0.

- [ ] **Step 2: Write the slice summary**

Create `.gsd/milestones/M030-autoborder-rules/slices/S01/S01-SUMMARY.md`:

```markdown
# S01 Summary - M030 Autoborder rules

## Scope

- Added the pure autoborder rule model in `rme_core`.
- Matched legacy edge names and rejected invalid ones.
- Resolved deterministic 8-neighbour placement plans.

## Verification

- `cargo test -p rme_core autoborder --quiet`
- `git diff --check`

## Notes

- Qt, preview, and map mutation remain out of scope.
```

- [ ] **Step 3: Mark slice plan complete**

Edit `.gsd/milestones/M030-autoborder-rules/slices/S01/S01-PLAN.md` and mark every finished task with `[x]`.

- [ ] **Step 4: Update state**

Edit `.gsd/STATE.md`:

```markdown
**Active Milestone:** none
**Active Slice:** none
**Active Task:** none
**Phase:** discovery
**Next Action:** Review M030/S01 result and decide whether to add a follow-up slice for map/UI consumption.
```

Add a recent decision:

```markdown
- `M030-autoborder-rules` is complete: pure autoborder rules now live in `rme_core`, and later slices can consume `AutoborderPlan` without reinterpreting legacy edge rules.
```

- [ ] **Step 5: Commit closeout**

```bash
git add .gsd/STATE.md .gsd/milestones/M030-autoborder-rules/slices/S01/S01-PLAN.md .gsd/milestones/M030-autoborder-rules/slices/S01/S01-SUMMARY.md .gsd/milestones/M030-autoborder-rules/slices/S01/tasks/T01-SUMMARY.md .gsd/milestones/M030-autoborder-rules/slices/S01/tasks/T02-SUMMARY.md
git commit -m "docs(M030/S01): close autoborder rules slice"
```

## Final Verification Before PR

Run:

```bash
cargo test -p rme_core autoborder --quiet
git diff --check
git status --short --branch --untracked-files=no
```

Expected: tests pass and tracked worktree is clean.
