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
        assert_eq!(
            edge_name_to_border_type("n").unwrap(),
            BorderType::NorthHorizontal
        );
        assert_eq!(
            edge_name_to_border_type("w").unwrap(),
            BorderType::WestHorizontal
        );
        assert_eq!(
            edge_name_to_border_type("s").unwrap(),
            BorderType::SouthHorizontal
        );
        assert_eq!(
            edge_name_to_border_type("e").unwrap(),
            BorderType::EastHorizontal
        );
        assert_eq!(
            edge_name_to_border_type("cnw").unwrap(),
            BorderType::NorthWestCorner
        );
        assert_eq!(
            edge_name_to_border_type("cne").unwrap(),
            BorderType::NorthEastCorner
        );
        assert_eq!(
            edge_name_to_border_type("csw").unwrap(),
            BorderType::SouthWestCorner
        );
        assert_eq!(
            edge_name_to_border_type("cse").unwrap(),
            BorderType::SouthEastCorner
        );
        assert_eq!(
            edge_name_to_border_type("dnw").unwrap(),
            BorderType::NorthWestDiagonal
        );
        assert_eq!(
            edge_name_to_border_type("dne").unwrap(),
            BorderType::NorthEastDiagonal
        );
        assert_eq!(
            edge_name_to_border_type("dsw").unwrap(),
            BorderType::SouthWestDiagonal
        );
        assert_eq!(
            edge_name_to_border_type("dse").unwrap(),
            BorderType::SouthEastDiagonal
        );
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
