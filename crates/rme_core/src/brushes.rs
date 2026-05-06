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

pub trait Brush {
    fn id(&self) -> u32;

    fn kind(&self) -> BrushKind;

    fn placement_command(&self, variation_index: Option<usize>) -> BrushPlacementCommand;
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

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GroundBrush {
    definition: GroundBrushDefinition,
}

impl GroundBrush {
    pub fn new() -> Self {
        Self {
            definition: GroundBrushDefinition {
                id: 1,
                name: String::from("ground"),
                look_id: 0,
                ground_items: Vec::new(),
                visible_in_palette: true,
                uses_collection: false,
                max_variation: 0,
            },
        }
    }

    pub fn from_definition(definition: GroundBrushDefinition) -> Self {
        Self { definition }
    }
}

impl Default for GroundBrush {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WallBrush {
    definition: WallBrushDefinition,
}

impl WallBrush {
    pub fn new() -> Self {
        Self {
            definition: WallBrushDefinition {
                id: 2,
                name: String::from("wall"),
                look_id: 0,
                wall_items: Vec::new(),
                visible_in_palette: true,
                uses_collection: false,
            },
        }
    }

    pub fn from_definition(definition: WallBrushDefinition) -> Self {
        Self { definition }
    }
}

impl Default for WallBrush {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BrushPlacementCommand {
    Noop,
    SetGround { item_id: u16 },
    AddWall { item_id: u16 },
}

impl BrushDefinition {
    pub const fn kind(&self) -> BrushKind {
        match self {
            Self::Ground(_) => BrushKind::Ground,
            Self::Wall(_) => BrushKind::Wall,
        }
    }

    pub const fn id(&self) -> u32 {
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

    pub const fn look_id(&self) -> u16 {
        match self {
            Self::Ground(definition) => definition.look_id,
            Self::Wall(definition) => definition.look_id,
        }
    }

    pub const fn visible_in_palette(&self) -> bool {
        match self {
            Self::Ground(definition) => definition.visible_in_palette,
            Self::Wall(definition) => definition.visible_in_palette,
        }
    }

    pub const fn uses_collection(&self) -> bool {
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

impl Brush for GroundBrush {
    fn id(&self) -> u32 {
        self.definition.id
    }

    fn kind(&self) -> BrushKind {
        BrushKind::Ground
    }

    fn placement_command(&self, variation_index: Option<usize>) -> BrushPlacementCommand {
        BrushDefinition::Ground(self.definition.clone()).placement_command(variation_index)
    }
}

impl Brush for WallBrush {
    fn id(&self) -> u32 {
        self.definition.id
    }

    fn kind(&self) -> BrushKind {
        BrushKind::Wall
    }

    fn placement_command(&self, variation_index: Option<usize>) -> BrushPlacementCommand {
        BrushDefinition::Wall(self.definition.clone()).placement_command(variation_index)
    }
}

impl Brush for BrushDefinition {
    fn id(&self) -> u32 {
        Self::id(self)
    }

    fn kind(&self) -> BrushKind {
        Self::kind(self)
    }

    fn placement_command(&self, variation_index: Option<usize>) -> BrushPlacementCommand {
        Self::placement_command(self, variation_index)
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

pub type BrushManager = BrushCatalog;

impl BrushCatalog {
    pub fn new() -> Self {
        Self::default()
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
        self.by_id
            .get(&id)
            .and_then(|index| self.brushes.get(*index))
    }

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

        assert_eq!(
            catalog.get_by_name("grass").unwrap().related_items(),
            vec![4526, 4527]
        );
        assert_eq!(
            catalog.get_by_name("stone wall").unwrap().related_items(),
            vec![3361, 3362]
        );
    }

    #[test]
    fn ground_brush_resolves_deterministic_placement() {
        let catalog =
            BrushCatalog::from_definitions(vec![ground("grass", 10, &[4526, 4527])]).unwrap();

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
        let catalog =
            BrushCatalog::from_definitions(vec![ground("empty ground", 10, &[])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("empty ground", None),
            BrushPlacementCommand::Noop
        );
    }

    #[test]
    fn wall_brush_resolves_first_wall_item() {
        let catalog =
            BrushCatalog::from_definitions(vec![wall("stone wall", 20, &[3361, 3362])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("stone wall", None),
            BrushPlacementCommand::AddWall { item_id: 3361 }
        );
    }

    #[test]
    fn missing_brush_resolves_noop() {
        let catalog =
            BrushCatalog::from_definitions(vec![wall("stone wall", 20, &[3361])]).unwrap();

        assert_eq!(
            catalog.placement_command_by_name("missing", None),
            BrushPlacementCommand::Noop
        );
    }

    #[test]
    fn ground_brush_exposes_expected_id() {
        let brush = GroundBrush::new();
        assert_eq!(brush.id(), 1);
    }
}
