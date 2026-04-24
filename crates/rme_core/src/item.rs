//! Item model for the Rust core.
//!
//! Matches the legacy C++ `Item` contract: server id, count/subtype,
//! action id, unique id. Additional attributes (text, description)
//! are deferred to a future attribute map.

use serde::{Deserialize, Serialize};

/// Core item representation matching legacy item.h contract.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Item {
    id: u16,
    count: u8,
    action_id: u16,
    unique_id: u16,
}

impl Item {
    /// Creates an item with the given server id and default attributes.
    pub const fn new(id: u16) -> Self {
        Self {
            id,
            count: 1,
            action_id: 0,
            unique_id: 0,
        }
    }

    /// Returns the server item id.
    pub const fn id(&self) -> u16 {
        self.id
    }

    /// Returns the stack count / subtype.
    pub const fn count(&self) -> u8 {
        self.count
    }

    /// Sets the stack count / subtype.
    pub fn set_count(&mut self, count: u8) {
        self.count = count;
    }

    /// Returns the action id (0 = none).
    pub const fn action_id(&self) -> u16 {
        self.action_id
    }

    /// Sets the action id.
    pub fn set_action_id(&mut self, action_id: u16) {
        self.action_id = action_id;
    }

    /// Returns the unique id (0 = none).
    pub const fn unique_id(&self) -> u16 {
        self.unique_id
    }

    /// Sets the unique id.
    pub fn set_unique_id(&mut self, unique_id: u16) {
        self.unique_id = unique_id;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn item_new_sets_id_and_defaults() {
        let item = Item::new(2148);
        assert_eq!(item.id(), 2148);
        assert_eq!(item.count(), 1);
        assert_eq!(item.action_id(), 0);
        assert_eq!(item.unique_id(), 0);
    }

    #[test]
    fn item_set_count_updates_value() {
        let mut item = Item::new(100);
        item.set_count(50);
        assert_eq!(item.count(), 50);
    }

    #[test]
    fn item_set_action_id_updates_value() {
        let mut item = Item::new(100);
        item.set_action_id(1234);
        assert_eq!(item.action_id(), 1234);
    }

    #[test]
    fn item_set_unique_id_updates_value() {
        let mut item = Item::new(100);
        item.set_unique_id(5678);
        assert_eq!(item.unique_id(), 5678);
    }

    #[test]
    fn item_clone_produces_equal_copy() {
        let mut original = Item::new(2148);
        original.set_count(10);
        original.set_action_id(42);
        let cloned = original.clone();
        assert_eq!(original, cloned);
    }

    #[test]
    fn items_with_different_ids_are_not_equal() {
        let a = Item::new(100);
        let b = Item::new(200);
        assert_ne!(a, b);
    }

    #[test]
    fn items_with_different_counts_are_not_equal() {
        let mut a = Item::new(100);
        let b = Item::new(100);
        a.set_count(5);
        assert_ne!(a, b);
    }
}
