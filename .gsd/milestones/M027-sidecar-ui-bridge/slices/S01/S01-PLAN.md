# M027/S01 Sidecar UI Bridge Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect existing waypoint and house UI workflows to editor-core sidecar state.

**Architecture:** `MapModel` owns sidecar collections. `EditorShellState` exposes small PyO3 methods. `EditorShellCoreBridge` provides native/fallback Python methods. Existing `WaypointsDock` and `HouseManagerDialog` use the bridge; no new UI screens.

**Tech Stack:** Rust `rme_core` + PyO3, Python bridge, PyQt6 widgets, pytest/pytest-qt.

---

## Files

- Modify: `crates/rme_core/src/map.rs`
- Modify: `crates/rme_core/src/editor.rs`
- Modify: `pyrme/core_bridge.py`
- Modify: `pyrme/ui/docks/waypoints.py`
- Modify: `tests/python/test_core_bridge.py`
- Modify: `tests/python/test_waypoints_layers_tier2.py`
- Modify: `tests/python/test_house_manager_dialog.py`
- Modify: `tests/python/test_rme_core_editor_shell.py`
- Modify: `.gsd/STATE.md`
- Create: `.gsd/milestones/M027-sidecar-ui-bridge/slices/S01/tasks/T01-SUMMARY.md`

---

## Task 1: Native waypoint/house bridge

**Files:**
- Modify: `crates/rme_core/src/map.rs`
- Modify: `crates/rme_core/src/editor.rs`
- Test: `crates/rme_core/src/editor.rs`

- [x] **Step 1: Write failing Rust tests**

Add tests in `crates/rme_core/src/editor.rs`:

```rust
#[test]
fn editor_bridge_lists_updates_and_removes_waypoints() {
    let mut shell = EditorShellState::default();
    assert!(shell.add_waypoint("Temple", 100, 200, 7));
    assert_eq!(shell.get_waypoints(), vec![("Temple".to_string(), 100, 200, 7)]);
    assert!(shell.update_waypoint(0, "Depot", 101, 201, 8));
    assert_eq!(shell.get_waypoints(), vec![("Depot".to_string(), 101, 201, 8)]);
    assert!(shell.remove_waypoint(0));
    assert!(shell.get_waypoints().is_empty());
    assert!(!shell.remove_waypoint(0));
}

#[test]
fn editor_bridge_lists_adds_updates_and_removes_houses_for_dialog() {
    let mut shell = EditorShellState::default();
    assert!(shell.add_house(12, "Depot", 102, 202, 7, 500, 3, true, 14));
    assert_eq!(
        shell.get_houses(),
        vec![(12, "Depot".to_string(), 3, 500, true, 102, 202, 7)]
    );
    assert!(shell.update_house(12, "Depot North", 4, 700, false, 103, 203, 8));
    assert_eq!(
        shell.get_houses(),
        vec![(12, "Depot North".to_string(), 4, 700, false, 103, 203, 8)]
    );
    assert!(shell.remove_house(12));
    assert!(shell.get_houses().is_empty());
    assert!(!shell.update_house(12, "Missing", 0, 0, false, 0, 0, 0));
}
```

- [x] **Step 2: Run failing test**

Run:

```bash
cargo test -p rme_core editor_bridge_lists_updates_and_removes_waypoints editor_bridge_lists_adds_updates_and_removes_houses_for_dialog
```

Expected: fail because methods do not exist.

- [x] **Step 3: Implement minimal native methods**

Add `MapModel` methods:

```rust
pub fn update_waypoint(&mut self, index: usize, waypoint: Waypoint) -> bool
pub fn remove_waypoint(&mut self, index: usize) -> bool
pub fn update_house(&mut self, house: House) -> bool
pub fn remove_house(&mut self, house_id: u32) -> bool
```

Add `EditorShellState` methods:

```rust
fn get_waypoints(&self) -> Vec<(String, u16, u16, u8)>
fn update_waypoint(&mut self, index: usize, name: &str, x: i32, y: i32, z: i32) -> bool
fn remove_waypoint(&mut self, index: usize) -> bool
fn get_houses(&self) -> Vec<(u32, String, u32, u32, bool, u16, u16, u8)>
fn update_house(&mut self, houseid: u32, name: &str, townid: u32, rent: u32, guildhall: bool, entryx: i32, entryy: i32, entryz: i32) -> bool
fn remove_house(&mut self, houseid: u32) -> bool
```

- [x] **Step 4: Run Rust verification**

Run:

```bash
cargo test -p rme_core editor
```

Expected: pass.

---

## Task 2: Python bridge fallback methods

**Files:**
- Modify: `pyrme/core_bridge.py`
- Test: `tests/python/test_core_bridge.py`

- [x] **Step 1: Write failing Python bridge tests**

Add tests:

```python
def test_fallback_bridge_stores_waypoints() -> None:
    core = create_editor_shell_state()
    assert core.add_waypoint("Temple", 100, 200, 7) is True
    assert core.get_waypoints() == [("Temple", 100, 200, 7)]
    assert core.update_waypoint(0, "Depot", 101, 201, 8) is True
    assert core.remove_waypoint(0) is True
    assert core.get_waypoints() == []


def test_fallback_bridge_stores_houses() -> None:
    core = create_editor_shell_state()
    assert core.add_house(12, "Depot", 0) is True
    assert core.get_houses() == [(12, "Depot", 0, 0, False, 32000, 32000, 7)]
    assert core.update_house(12, "Depot North", 3, 500, True, 100, 200, 7) is True
    assert core.get_houses() == [(12, "Depot North", 3, 500, True, 100, 200, 7)]
    assert core.remove_house(12) is True
    assert core.get_houses() == []
```

- [x] **Step 2: Run failing tests**

Run:

```bash
python3 -m pytest tests/python/test_core_bridge.py -q --tb=short
```

Expected: fail because methods do not exist.

- [x] **Step 3: Implement minimal bridge methods**

Add fallback storage lists and bridge wrappers for `get_waypoints`, `add_waypoint`, `update_waypoint`, `remove_waypoint`, `get_houses`, `add_house`, `update_house`, `remove_house`.

- [x] **Step 4: Run bridge tests**

Run:

```bash
python3 -m pytest tests/python/test_core_bridge.py -q --tb=short
```

Expected: pass.

---

## Task 3: WaypointsDock editor binding

**Files:**
- Modify: `pyrme/ui/docks/waypoints.py`
- Modify: `pyrme/ui/main_window.py`
- Test: `tests/python/test_waypoints_layers_tier2.py`

- [x] **Step 1: Write failing widget test**

Add a fake editor test that constructs `WaypointsDock(editor=fake)`, verifies initial load, add, rename, and remove call the fake editor.

- [x] **Step 2: Run failing widget test**

Run:

```bash
python3 -m pytest tests/python/test_waypoints_layers_tier2.py -q --tb=short
```

Expected: fail because dock does not accept editor bridge.

- [x] **Step 3: Implement minimal dock binding**

Add optional `editor` argument. If bridge has waypoint methods, use bridge for add/rename/remove and refresh from `get_waypoints`; otherwise keep current local behavior.

Update `MainWindow._setup_docks()` to pass `self._editor_context.session.editor`.

- [x] **Step 4: Run widget tests**

Run:

```bash
python3 -m pytest tests/python/test_waypoints_layers_tier2.py -q --tb=short
```

Expected: pass.

---

## Task 4: House dialog/native save integration

**Files:**
- Modify: `tests/python/test_house_manager_dialog.py`
- Modify: `tests/python/test_rme_core_editor_shell.py`
- Modify: `.gsd/STATE.md`
- Create: `.gsd/milestones/M027-sidecar-ui-bridge/slices/S01/tasks/T01-SUMMARY.md`

- [x] **Step 1: Write failing dialog/native tests**

Add fake bridge test for `HouseManagerDialog` list/add/update/remove. Add native shell test verifying bridge changes save expected waypoint and house XML.

- [x] **Step 2: Run failing tests**

Run:

```bash
python3 -m pytest tests/python/test_house_manager_dialog.py tests/python/test_rme_core_editor_shell.py -q --tb=short
```

Expected: fail until native/Python bridge is complete.

- [x] **Step 3: Apply minimal fixes from earlier tasks only**

No new UI. No spawn manager. No Map Properties wiring.

- [x] **Step 4: Run final verification**

Run:

```bash
npm run preflight --silent
cargo test -p rme_core editor
python3 -m pytest tests/python/test_core_bridge.py tests/python/test_waypoints_layers_tier2.py tests/python/test_house_manager_dialog.py tests/python/test_rme_core_editor_shell.py -q --tb=short
```

Expected: all pass.

- [x] **Step 5: Close slice docs**

Write `T01-SUMMARY.md`, mark checked tasks in this plan, update `.gsd/STATE.md` to review.

- [x] **Step 6: Caveman Review**

Review diff for scope gaps:

```bash
git diff --stat
git diff --check
```

Expected: no blocking gap.
