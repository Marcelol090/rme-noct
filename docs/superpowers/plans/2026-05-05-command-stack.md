# Command Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Rust-backed tile command journal and route existing Python Undo/Redo through it without changing current map/UI behavior.

**Architecture:** Keep Python `MapModel` as the UI source of truth. `EditorModel` still builds and applies tile edit batches, but command history storage moves behind `pyrme.core_bridge` into native `EditorShellState` when available and a stateful Python fallback otherwise.

**Tech Stack:** Rust, PyO3 0.23, Python dataclasses, PyQt6 action wiring tests, RTK-wrapped WSL verification.

---

## Context

- Design: `docs/superpowers/specs/2026-05-05-command-stack-design.md`
- GSD context: `.gsd/milestones/M036-command-stack/M036-command-stack-CONTEXT.md`
- Existing baseline: `PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_legacy_edit_menu.py -q --tb=short` -> `13 passed`
- Context7 PyO3 note: `PyResult<T>` raises Python exceptions; `PyValueError::new_err(...)` maps validation failures; `Vec<u16>` returns Python lists in PyO3 0.23.

## Files

- Create: `crates/rme_core/src/command_stack.rs`
- Modify: `crates/rme_core/src/lib.rs`
- Modify: `crates/rme_core/src/editor.rs`
- Create: `pyrme/editor/command_history.py`
- Modify: `pyrme/editor/model.py`
- Modify: `pyrme/editor/__init__.py`
- Modify: `pyrme/core_bridge.py`
- Modify: `tests/python/test_core_bridge.py`
- Modify: `tests/python/test_legacy_edit_menu.py`
- Modify: `tests/python/test_rme_core_editor_shell.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M036-command-stack/slices/S01/S01-PLAN.md`

---

### Task 1: Rust Command Stack Domain

**Files:**
- Create: `crates/rme_core/src/command_stack.rs`
- Modify: `crates/rme_core/src/lib.rs`

- [ ] **Step 1: Add failing Rust tests**

Create `crates/rme_core/src/command_stack.rs` with this test module first:

```rust
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
```

- [ ] **Step 2: Run RED**

Run:

```bash
cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m036-command-stack-20260505"
PATH="$HOME/.local/bin:$PATH" rtk cargo test -p rme_core command_stack
```

Expected: fail on missing `TileSnapshot`, `TileCommandChange`, `CommandStack`.

- [ ] **Step 3: Implement domain**

Add above tests in same file with this implementation before the test module:

```rust
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
```

Modify `crates/rme_core/src/lib.rs`:

```rust
pub mod command_stack;
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
PATH="$HOME/.local/bin:$PATH" rtk cargo test -p rme_core command_stack
```

Expected: command stack tests pass.

- [ ] **Step 5: Commit task**

```bash
git add crates/rme_core/src/command_stack.rs crates/rme_core/src/lib.rs
git commit -m "feat(M036/T01): add command stack core"
```

---

### Task 2: Native and Fallback Bridge

**Files:**
- Modify: `crates/rme_core/src/editor.rs`
- Modify: `pyrme/core_bridge.py`
- Modify: `tests/python/test_core_bridge.py`
- Modify: `tests/python/test_rme_core_editor_shell.py`

- [ ] **Step 1: Add Python bridge RED tests**

Append to `tests/python/test_core_bridge.py`:

```python
def test_fallback_bridge_records_tile_command_history() -> None:
    core = EditorShellCoreBridge(_FallbackEditorShellState(), native=False)
    change = (32000, 32000, 7, None, (100, (200, 300)))

    assert core.record_tile_command("Draw Tile", (change,)) is True
    assert core.can_undo_tile_command() is True
    assert core.can_redo_tile_command() is False

    assert core.undo_tile_command() == (
        (32000, 32000, 7, (100, (200, 300)), None),
    )
    assert core.can_undo_tile_command() is False
    assert core.can_redo_tile_command() is True

    assert core.redo_tile_command() == (
        (32000, 32000, 7, None, (100, (200, 300))),
    )


def test_fallback_bridge_ignores_noop_tile_command() -> None:
    core = EditorShellCoreBridge(_FallbackEditorShellState(), native=False)
    snapshot = (100, (200,))

    assert core.record_tile_command(
        "No-op",
        ((32000, 32000, 7, snapshot, snapshot),),
    ) is False
    assert core.can_undo_tile_command() is False
```

Append to `tests/python/test_rme_core_editor_shell.py`:

```python
def test_native_rme_core_exposes_tile_command_history() -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )
    required = (
        "record_tile_command",
        "can_undo_tile_command",
        "can_redo_tile_command",
        "undo_tile_command",
        "redo_tile_command",
    )
    missing = [name for name in required if not hasattr(rme_core.EditorShellState, name)]
    if missing:
        pytest.skip(f"pyrme.rme_core missing M036 methods: {missing}")

    shell = rme_core.EditorShellState()
    assert shell.record_tile_command(
        "Draw Tile",
        [(32000, 32000, 7, None, (100, [200, 300]))],
    ) is True
    assert shell.can_undo_tile_command() is True
    assert shell.undo_tile_command() == [
        (32000, 32000, 7, (100, [200, 300]), None)
    ]
    assert shell.can_redo_tile_command() is True
    assert shell.redo_tile_command() == [
        (32000, 32000, 7, None, (100, [200, 300]))
    ]
```

- [ ] **Step 2: Run RED**

```bash
PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_core_bridge.py -q --tb=short
```

Expected: fail on missing `record_tile_command`.

- [ ] **Step 3: Add PyO3 bridge methods**

In `crates/rme_core/src/editor.rs`, import:

```rust
use crate::command_stack::{
    CommandPosition, CommandStack, TileCommandBatch, TileCommandChange, TileSnapshot,
};
use crate::map::MAX_Z;
```

Change `EditorShellState`:

```rust
pub struct EditorShellState {
    map: MapModel,
    render: RenderState,
    budget: RenderBudget,
    command_stack: CommandStack,
}
```

Set default:

```rust
command_stack: CommandStack::default(),
```

Add type aliases near imports:

```rust
type PyTileSnapshot = Option<(Option<u16>, Vec<u16>)>;
type PyTileCommandChange = (i32, i32, i32, PyTileSnapshot, PyTileSnapshot);
type PyTileCommandReplay = (u16, u16, u8, PyTileSnapshot, PyTileSnapshot);
```

Add helper functions outside `#[pymethods]`:

```rust
fn py_snapshot(snapshot: PyTileSnapshot) -> Option<TileSnapshot> {
    snapshot.map(|(ground_id, item_ids)| TileSnapshot { ground_id, item_ids })
}

fn replay_snapshot(snapshot: Option<TileSnapshot>) -> PyTileSnapshot {
    snapshot.map(|value| (value.ground_id, value.item_ids))
}

fn command_position(x: i32, y: i32, z: i32) -> PyResult<CommandPosition> {
    if !(0..=i32::from(u16::MAX)).contains(&x) {
        return Err(PyValueError::new_err(format!("x out of range: {x}")));
    }
    if !(0..=i32::from(u16::MAX)).contains(&y) {
        return Err(PyValueError::new_err(format!("y out of range: {y}")));
    }
    if !(0..=i32::from(MAX_Z)).contains(&z) {
        return Err(PyValueError::new_err(format!("z out of range: {z}")));
    }
    Ok(CommandPosition::new(x as u16, y as u16, z as u8))
}

fn py_changes(changes: Vec<PyTileCommandChange>) -> PyResult<Vec<TileCommandChange>> {
    changes
        .into_iter()
        .map(|(x, y, z, before, after)| {
            Ok(TileCommandChange {
                position: command_position(x, y, z)?,
                before: py_snapshot(before),
                after: py_snapshot(after),
            })
        })
        .collect()
}

fn replay_changes(batch: TileCommandBatch) -> Vec<PyTileCommandReplay> {
    batch
        .changes
        .into_iter()
        .map(|change| {
            let (x, y, z) = change.position.as_tuple();
            (
                x,
                y,
                z,
                replay_snapshot(change.before),
                replay_snapshot(change.after),
            )
        })
        .collect()
}
```

Add methods inside `#[pymethods] impl EditorShellState`:

```rust
fn record_tile_command(
    &mut self,
    label: &str,
    changes: Vec<PyTileCommandChange>,
) -> PyResult<bool> {
    Ok(self.command_stack.record(label, py_changes(changes)?))
}

fn can_undo_tile_command(&self) -> bool {
    self.command_stack.can_undo()
}

fn can_redo_tile_command(&self) -> bool {
    self.command_stack.can_redo()
}

fn undo_tile_command(&mut self) -> Vec<PyTileCommandReplay> {
    self.command_stack
        .undo()
        .map(replay_changes)
        .unwrap_or_default()
}

fn redo_tile_command(&mut self) -> Vec<PyTileCommandReplay> {
    self.command_stack
        .redo()
        .map(replay_changes)
        .unwrap_or_default()
}
```

- [ ] **Step 4: Add Python fallback/proxy**

In `pyrme/core_bridge.py`, add aliases near imports:

```python
TileSnapshotPayload = tuple[int | None, tuple[int, ...]]
TileCommandPayload = tuple[
    int,
    int,
    int,
    TileSnapshotPayload | None,
    TileSnapshotPayload | None,
]
```

Add fields to `_FallbackEditorShellState`:

```python
    _tile_undo_stack: list[tuple[str, tuple[TileCommandPayload, ...]]] = field(
        default_factory=list
    )
    _tile_redo_stack: list[tuple[str, tuple[TileCommandPayload, ...]]] = field(
        default_factory=list
    )
```

Add methods to `_FallbackEditorShellState`:

```python
    def record_tile_command(
        self,
        label: str,
        changes: list[TileCommandPayload] | tuple[TileCommandPayload, ...],
    ) -> bool:
        effective = tuple(change for change in changes if change[3] != change[4])
        if not effective:
            return False
        self._tile_undo_stack.append((str(label), effective))
        self._tile_redo_stack.clear()
        return True

    def can_undo_tile_command(self) -> bool:
        return bool(self._tile_undo_stack)

    def can_redo_tile_command(self) -> bool:
        return bool(self._tile_redo_stack)

    def undo_tile_command(self) -> list[TileCommandPayload]:
        if not self._tile_undo_stack:
            return []
        label, changes = self._tile_undo_stack.pop()
        self._tile_redo_stack.append((label, changes))
        return [
            (x, y, z, after, before)
            for x, y, z, before, after in reversed(changes)
        ]

    def redo_tile_command(self) -> list[TileCommandPayload]:
        if not self._tile_redo_stack:
            return []
        label, changes = self._tile_redo_stack.pop()
        self._tile_undo_stack.append((label, changes))
        return list(changes)
```

Add `EditorShellCoreBridge._command_inner`:

```python
    def _command_inner(self) -> Any:
        if hasattr(self._inner, "record_tile_command"):
            return self._inner
        if not hasattr(self, "_command_fallback"):
            self._command_fallback = _FallbackEditorShellState()
        return self._command_fallback
```

Add bridge methods:

```python
    def record_tile_command(
        self,
        label: str,
        changes: tuple[TileCommandPayload, ...],
    ) -> bool:
        return bool(self._command_inner().record_tile_command(label, list(changes)))

    def can_undo_tile_command(self) -> bool:
        return bool(self._command_inner().can_undo_tile_command())

    def can_redo_tile_command(self) -> bool:
        return bool(self._command_inner().can_redo_tile_command())

    def undo_tile_command(self) -> tuple[TileCommandPayload, ...]:
        return tuple(self._command_inner().undo_tile_command())

    def redo_tile_command(self) -> tuple[TileCommandPayload, ...]:
        return tuple(self._command_inner().redo_tile_command())
```

- [ ] **Step 5: Run GREEN**

```bash
PATH="$HOME/.local/bin:$PATH" rtk cargo test -p rme_core command_stack
PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_core_bridge.py tests/python/test_rme_core_editor_shell.py -q --tb=short
```

Expected: Rust command stack and Python bridge tests pass or native-only tests skip when extension is stale.

- [ ] **Step 6: Commit task**

```bash
git add crates/rme_core/src/editor.rs pyrme/core_bridge.py tests/python/test_core_bridge.py tests/python/test_rme_core_editor_shell.py
git commit -m "feat(M036/T02): expose command history bridge"
```

---

### Task 3: EditorModel History Delegation

**Files:**
- Create: `pyrme/editor/command_history.py`
- Modify: `pyrme/editor/model.py`
- Modify: `pyrme/editor/__init__.py`
- Modify: `tests/python/test_legacy_edit_menu.py`

- [ ] **Step 1: Add RED tests for bridge-owned history**

Modify `tests/python/test_legacy_edit_menu.py`:

```python
def test_editor_model_tracks_undo_redo_for_tile_edits() -> None:
    editor = EditorModel()
    assert not hasattr(editor, "_undo_stack")
    assert not hasattr(editor, "_redo_stack")
    position = MapPosition(32000, 32000, 7)
    editor.activate_item_brush(1)

    assert editor.apply_active_tool_at(position) is True
    assert editor.can_undo() is True
    assert editor.can_redo() is False
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=1,
    )

    assert editor.undo() is True
    assert editor.map_model.get_tile(position) is None
    assert editor.can_undo() is False
    assert editor.can_redo() is True

    assert editor.redo() is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=1,
    )
```

Add new test:

```python
def test_editor_model_new_edit_after_undo_clears_redo() -> None:
    editor = EditorModel()
    first = MapPosition(32000, 32000, 7)
    second = MapPosition(32001, 32000, 7)
    editor.activate_item_brush(1)

    assert editor.apply_active_tool_at(first) is True
    assert editor.undo() is True
    assert editor.can_redo() is True

    assert editor.apply_active_tool_at(second) is True
    assert editor.can_undo() is True
    assert editor.can_redo() is False
```

- [ ] **Step 2: Run RED**

```bash
PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_legacy_edit_menu.py::test_editor_model_tracks_undo_redo_for_tile_edits tests/python/test_legacy_edit_menu.py::test_editor_model_new_edit_after_undo_clears_redo -q --tb=short
```

Expected: fail because `_undo_stack` / `_redo_stack` still exist.

- [ ] **Step 3: Add Python command history adapter**

Create `pyrme/editor/command_history.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from pyrme.core_bridge import EditorShellCoreBridge, create_editor_shell_state

TileSnapshotPayload: TypeAlias = tuple[int | None, tuple[int, ...]]
TileCommandPayload: TypeAlias = tuple[
    int,
    int,
    int,
    TileSnapshotPayload | None,
    TileSnapshotPayload | None,
]


@dataclass(slots=True)
class TileCommandHistory:
    bridge: EditorShellCoreBridge = field(default_factory=create_editor_shell_state)

    def record(self, label: str, changes: tuple[TileCommandPayload, ...]) -> bool:
        return self.bridge.record_tile_command(label, changes)

    def can_undo(self) -> bool:
        return self.bridge.can_undo_tile_command()

    def can_redo(self) -> bool:
        return self.bridge.can_redo_tile_command()

    def undo(self) -> tuple[TileCommandPayload, ...]:
        return self.bridge.undo_tile_command()

    def redo(self) -> tuple[TileCommandPayload, ...]:
        return self.bridge.redo_tile_command()
```

Update `pyrme/editor/__init__.py`:

```python
from pyrme.editor.command_history import TileCommandHistory
```

Add `"TileCommandHistory"` to `__all__`.

- [ ] **Step 4: Refactor EditorModel**

In `pyrme/editor/model.py`, import:

```python
from pyrme.editor.command_history import (
    TileCommandHistory,
    TileCommandPayload,
    TileSnapshotPayload,
)
```

Replace `_undo_stack` and `_redo_stack` fields with:

```python
    _command_history: TileCommandHistory = field(
        default_factory=TileCommandHistory,
        repr=False,
    )
```

Replace methods:

```python
    def can_undo(self) -> bool:
        return self._command_history.can_undo()

    def can_redo(self) -> bool:
        return self._command_history.can_redo()

    def undo(self) -> bool:
        replay = self._command_history.undo()
        if not replay:
            return False
        return self._apply_replay_payloads(replay)

    def redo(self) -> bool:
        replay = self._command_history.redo()
        if not replay:
            return False
        return self._apply_replay_payloads(replay)
```

Change `_apply_changes` signature:

```python
    def _apply_changes(
        self,
        changes: tuple[TileEditChange, ...],
        *,
        record: bool = True,
        label: str = "Tile Edit",
    ) -> bool:
```

Replace body tail with:

```python
        if record and not self._command_history.record(
            label,
            tuple(self._change_to_payload(change) for change in effective_changes),
        ):
            return False
        self._apply_replay_changes(effective_changes)
        return True
```

Add helpers:

```python
    def _apply_replay_changes(self, changes: tuple[TileEditChange, ...]) -> None:
        for change in changes:
            if change.after is None:
                self.map_model.remove_tile(change.position)
            else:
                self.map_model.set_tile(change.after)

    def _apply_replay_payloads(
        self,
        payloads: tuple[TileCommandPayload, ...],
    ) -> bool:
        changes = tuple(self._payload_to_change(payload) for payload in payloads)
        if not changes:
            return False
        self._apply_replay_changes(changes)
        return True

    @staticmethod
    def _snapshot_to_payload(tile: TileState | None) -> TileSnapshotPayload | None:
        if tile is None:
            return None
        return (tile.ground_item_id, tuple(tile.item_ids))

    @staticmethod
    def _payload_to_snapshot(
        position: MapPosition,
        payload: TileSnapshotPayload | None,
    ) -> TileState | None:
        if payload is None:
            return None
        ground_item_id, item_ids = payload
        return TileState(
            position=position,
            ground_item_id=ground_item_id,
            item_ids=tuple(item_ids),
        )

    def _change_to_payload(self, change: TileEditChange) -> TileCommandPayload:
        return (
            change.position.x,
            change.position.y,
            change.position.z,
            self._snapshot_to_payload(change.before),
            self._snapshot_to_payload(change.after),
        )

    def _payload_to_change(self, payload: TileCommandPayload) -> TileEditChange:
        x, y, z, before, after = payload
        position = MapPosition(x, y, z)
        return TileEditChange(
            position=position,
            before=self._payload_to_snapshot(position, before),
            after=self._payload_to_snapshot(position, after),
        )
```

Add labels at current mutation call sites:

```python
# In apply_active_tool_at drawing branch:
self._apply_changes(
    (TileEditChange(position=position, before=existing, after=next_tile),),
    label="Draw Tile",
)

# In apply_active_tool_at erasing branch:
self._apply_changes(
    (TileEditChange(position=position, before=existing, after=None),),
    label="Erase Tile",
)

# Existing local variables stay unchanged in these methods:
self._apply_changes(changes, label="Cut Selection")
self._apply_changes(tuple(changes), label="Paste Selection")
self._apply_changes(tuple(changes), label="Replace Items")
self._apply_changes(tuple(changes), label="Remove Items")
self._apply_changes(tuple(changes), label="Borderize")
```

- [ ] **Step 5: Run GREEN**

```bash
PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_legacy_edit_menu.py -q --tb=short
```

Expected: all edit-menu tests pass.

- [ ] **Step 6: Commit task**

```bash
git add pyrme/editor/command_history.py pyrme/editor/model.py pyrme/editor/__init__.py tests/python/test_legacy_edit_menu.py
git commit -m "feat(M036/T03): delegate editor history"
```

---

### Task 4: UI Regression, GSD Closeout, Review Gate

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M036-command-stack/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M036-command-stack/slices/S01/S01-SUMMARY.md`

- [ ] **Step 1: Run targeted verification**

```bash
PATH="$HOME/.local/bin:$PATH" rtk cargo test -p rme_core command_stack
PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py tests/python/test_rme_core_editor_shell.py -q --tb=short
PATH="$HOME/.local/bin:$PATH" rtk npm run preflight --silent
```

Expected:
- Rust command stack tests pass.
- Python bridge/edit menu tests pass.
- Native extension tests either pass or skip with explicit stale-binary reason.
- Preflight validation reports `ok`.

- [ ] **Step 2: Write summary**

Create `.gsd/milestones/M036-command-stack/slices/S01/S01-SUMMARY.md`:

```markdown
# M036/S01 Summary

## Done

- Added Rust `CommandStack` for tile edit command batches.
- Exposed record/undo/redo state through native `EditorShellState`.
- Mirrored command history in Python fallback bridge.
- Routed `EditorModel` Undo/Redo through bridge-backed command history.
- Preserved current Edit menu behavior for Draw, Erase, Cut, Paste, Replace Items, Remove Items, and Borderize.

## Verification

- `PATH="$HOME/.local/bin:$PATH" rtk cargo test -p rme_core command_stack`
- `PATH="$HOME/.local/bin:$PATH" rtk pytest tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py tests/python/test_rme_core_editor_shell.py -q --tb=short`
- `PATH="$HOME/.local/bin:$PATH" rtk npm run preflight --silent`

## Out of Scope

- Clipboard format redesign.
- File lifecycle command journal.
- Renderer, minimap, Search menu.
- Full Rust map ownership migration.
```

- [ ] **Step 3: Mark GSD plan**

Update `.gsd/milestones/M036-command-stack/slices/S01/S01-PLAN.md` task list to checked:

```markdown
- [x] T01: Add Rust command stack domain and tests.
- [x] T02: Expose PyO3/fallback command history bridge.
- [x] T03: Route Python `EditorModel` undo/redo through the bridge.
- [x] T04: Re-verify UI edit actions and close review gaps.
```

Update `.gsd/STATE.md` header:

```markdown
**Active Milestone:** M036-command-stack
**Active Slice:** S01-COMMAND-STACK
**Active Task:** none
**Phase:** review
**Next Action:** Run caveman-review on M036/S01 diff, then commit/push/PR after approval.
**Last Updated:** 2026-05-05T00:00:00-03:00
```

- [ ] **Step 4: Run diff review**

Use `caveman-review` and `superpowers:receiving-code-review` if feedback appears.

```bash
git diff --stat
git diff -- crates/rme_core/src/command_stack.rs crates/rme_core/src/editor.rs pyrme/core_bridge.py pyrme/editor/model.py pyrme/editor/command_history.py tests/python/test_core_bridge.py tests/python/test_legacy_edit_menu.py tests/python/test_rme_core_editor_shell.py
```

Expected: no gap. Fix any real gap before commit.

- [ ] **Step 5: Commit closeout**

```bash
git add .gsd/STATE.md .gsd/milestones/M036-command-stack docs/superpowers/specs/2026-05-05-command-stack-design.md docs/superpowers/plans/2026-05-05-command-stack.md
git commit -m "docs(M036/S01): plan command stack slice"
```

If implementation commits already include docs, skip duplicate doc commit and keep one clean final history.

---

## PR Gate

After implementation + clean review:

```bash
git status -sb
git log --oneline origin/main..HEAD
PATH="$HOME/.local/bin:$PATH" rtk gh pr create --draft --base main --head gsd/M036/S01-command-stack --title "[codex] M036 command stack" --body-file .gsd/milestones/M036-command-stack/slices/S01/S01-SUMMARY.md
```

Use `github:yeet` for commit/push/PR if local `gh` coverage is enough; use GitHub connector fallback only if `gh` blocks.
