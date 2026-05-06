#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, Hash)]
pub struct CommandPosition {
    x: u16,
    y: u16,
    z: u8,
}

impl CommandPosition {
    pub const fn new(x: u16, y: u16, z: u8) -> Self {
        Self { x, y, z }
    }

    pub const fn as_tuple(self) -> (u16, u16, u8) {
        (self.x, self.y, self.z)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TileSnapshot {
    pub ground_id: Option<u16>,
    pub item_ids: Vec<u16>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TileCommandChange {
    pub position: CommandPosition,
    pub before: Option<TileSnapshot>,
    pub after: Option<TileSnapshot>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TileCommandBatch {
    pub label: String,
    pub changes: Vec<TileCommandChange>,
}

#[derive(Debug, Default, Clone)]
pub struct CommandStack {
    undo_stack: Vec<TileCommandBatch>,
    redo_stack: Vec<TileCommandBatch>,
}

impl CommandStack {
    pub fn can_undo(&self) -> bool {
        !self.undo_stack.is_empty()
    }

    pub fn can_redo(&self) -> bool {
        !self.redo_stack.is_empty()
    }

    pub fn record(&mut self, label: impl Into<String>, changes: Vec<TileCommandChange>) -> bool {
        let effective: Vec<TileCommandChange> = changes
            .into_iter()
            .filter(|change| change.before != change.after)
            .collect();
        if effective.is_empty() {
            return false;
        }
        self.undo_stack.push(TileCommandBatch {
            label: label.into(),
            changes: effective,
        });
        self.redo_stack.clear();
        true
    }

    pub fn undo(&mut self) -> Option<TileCommandBatch> {
        let batch = self.undo_stack.pop()?;
        let replay = TileCommandBatch {
            label: batch.label.clone(),
            changes: batch
                .changes
                .iter()
                .rev()
                .map(|change| TileCommandChange {
                    position: change.position,
                    before: change.after.clone(),
                    after: change.before.clone(),
                })
                .collect(),
        };
        self.redo_stack.push(batch);
        Some(replay)
    }

    pub fn redo(&mut self) -> Option<TileCommandBatch> {
        let batch = self.redo_stack.pop()?;
        self.undo_stack.push(batch.clone());
        Some(batch)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn pos() -> CommandPosition {
        CommandPosition::new(32000, 32000, 7)
    }

    fn snapshot(id: u16) -> TileSnapshot {
        TileSnapshot {
            ground_id: Some(id),
            item_ids: vec![200, 300],
        }
    }

    #[test]
    fn record_undo_redo_replays_tile_batch() {
        let mut stack = CommandStack::default();
        let change = TileCommandChange {
            position: pos(),
            before: None,
            after: Some(snapshot(100)),
        };

        assert!(stack.record("Draw Tile", vec![change.clone()]));
        assert!(stack.can_undo());
        assert!(!stack.can_redo());

        let undo = stack.undo().unwrap();
        assert_eq!(undo.label, "Draw Tile");
        assert_eq!(undo.changes[0].before, Some(snapshot(100)));
        assert_eq!(undo.changes[0].after, None);
        assert!(!stack.can_undo());
        assert!(stack.can_redo());

        let redo = stack.redo().unwrap();
        assert_eq!(redo.changes, vec![change]);
        assert!(stack.can_undo());
        assert!(!stack.can_redo());
    }

    #[test]
    fn new_record_clears_redo() {
        let mut stack = CommandStack::default();
        assert!(stack.record(
            "First",
            vec![TileCommandChange {
                position: pos(),
                before: None,
                after: Some(snapshot(100)),
            }],
        ));
        assert!(stack.undo().is_some());
        assert!(stack.can_redo());

        assert!(stack.record(
            "Second",
            vec![TileCommandChange {
                position: CommandPosition::new(32001, 32000, 7),
                before: None,
                after: Some(snapshot(101)),
            }],
        ));
        assert!(!stack.can_redo());
    }

    #[test]
    fn no_op_batch_is_not_recorded() {
        let mut stack = CommandStack::default();
        assert!(!stack.record(
            "No-op",
            vec![TileCommandChange {
                position: pos(),
                before: Some(snapshot(100)),
                after: Some(snapshot(100)),
            }],
        ));
        assert!(!stack.can_undo());
    }
}
