# M025 Map Statistics S01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real `Map -> Statistics` read-only dialog fed by Rust `MapModel` statistics.

**Architecture:** Rust owns map-domain aggregation through `MapStatistics` and `MapModel::collect_statistics()`. The PyO3 shell bridge exposes that object to Python. PyQt6 UI presents stats and keeps fallback mode honest by showing zeros when no native provider exists.

**Tech Stack:** Rust, PyO3, Python 3.12, PyQt6, pytest-qt, ruff, rustfmt.

---

## File Structure

- Modify `crates/rme_core/src/map.rs`: add `MapStatistics`, blocking flag helpers, and `MapModel::collect_statistics()`.
- Modify `crates/rme_core/src/editor.rs`: expose `EditorShellState.collect_statistics()`.
- Modify `crates/rme_core/src/lib.rs`: register `MapStatistics` PyO3 class.
- Modify `pyrme/core_bridge.py`: add `collect_statistics()` passthrough and fallback `None`.
- Create `pyrme/ui/dialogs/map_statistics.py`: read-only statistics dialog.
- Modify `pyrme/ui/dialogs/__init__.py`: export `MapStatisticsDialog`.
- Modify `pyrme/ui/main_window.py`: inject dialog factory and wire `Map -> Statistics`.
- Create `tests/python/test_map_statistics_dialog.py`: dialog field rendering test.
- Modify `tests/python/test_legacy_map_menu.py`: convert Statistics from safe gap to dialog seam.

## Task 1: Rust Statistics Contract

**Files:**
- Modify: `crates/rme_core/src/map.rs`
- Modify: `crates/rme_core/src/editor.rs`
- Modify: `crates/rme_core/src/lib.rs`

- [x] **Step 1: Write failing Rust test**

Append this test inside `#[cfg(test)] mod tests` in `crates/rme_core/src/map.rs`:

```rust
#[test]
fn map_model_collects_statistics_from_tiles_and_sidecars() {
    let mut model = MapModel::new();

    let mut walkable = Tile::new(MapPosition::new(1, 1, 7));
    walkable.set_ground(Some(Item::new(100)));
    walkable.add_item(Item::new(200));
    model.set_tile(walkable);

    let mut blocking = Tile::new(MapPosition::new(2, 1, 7));
    blocking.set_blocking(true);
    blocking.add_item(Item::new(300));
    model.set_tile(blocking);

    model.add_waypoint(Waypoint::new("Depot", MapPosition::new(10, 20, 7)));
    let spawn_index = model.add_spawn(Spawn::new(MapPosition::new(11, 21, 7), 5));
    model
        .add_spawn_creature(spawn_index, Creature::new("Rat", 1, -1, 60, false, 2))
        .unwrap();
    model
        .add_spawn_creature(spawn_index, Creature::new("Guide", 0, 0, 30, true, 0))
        .unwrap();
    model.add_house(House::new(
        12,
        "House",
        MapPosition::new(12, 22, 7),
        500,
        3,
        true,
        14,
    ));

    let stats = model.collect_statistics();

    assert_eq!(stats.tile_count, 2);
    assert_eq!(stats.walkable_tile_count, 1);
    assert_eq!(stats.blocking_tile_count, 1);
    assert_eq!(stats.item_count, 3);
    assert_eq!(stats.spawn_count, 1);
    assert_eq!(stats.creature_count, 2);
    assert_eq!(stats.waypoint_count, 1);
    assert_eq!(stats.house_count, 1);
    assert_eq!(stats.total_house_sqm, 14);
    assert_eq!(stats.town_count, 1);
}
```

- [x] **Step 2: Run test to verify RED**

Run:

```bash
PYO3_PYTHON=/tmp/rme-noct-m025-py312/bin/python \
LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:$LD_LIBRARY_PATH \
RUSTFLAGS='-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l python3.12 -C link-arg=-Wl,-rpath,/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib' \
cargo test -p rme_core map_model_collects_statistics_from_tiles_and_sidecars
```

Expected: FAIL because `Tile::set_blocking` or `MapModel::collect_statistics` does not exist.

- [x] **Step 3: Implement minimal Rust contract**

In `crates/rme_core/src/map.rs`, change imports:

```rust
use std::collections::{HashMap, HashSet};

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
```

Add after `impl House`:

```rust
#[pyclass]
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct MapStatistics {
    #[pyo3(get)]
    pub tile_count: u64,
    #[pyo3(get)]
    pub blocking_tile_count: u64,
    #[pyo3(get)]
    pub walkable_tile_count: u64,
    #[pyo3(get)]
    pub item_count: u64,
    #[pyo3(get)]
    pub spawn_count: u64,
    #[pyo3(get)]
    pub creature_count: u64,
    #[pyo3(get)]
    pub house_count: u64,
    #[pyo3(get)]
    pub total_house_sqm: u64,
    #[pyo3(get)]
    pub town_count: u64,
    #[pyo3(get)]
    pub waypoint_count: u64,
}

impl MapStatistics {
    pub fn new() -> Self {
        Self::default()
    }
}
```

Add to `impl Tile`:

```rust
/// TILESTATE_BLOCKING = 0x0004.
pub fn is_blocking(&self) -> bool {
    self.statflags & 0x0004 != 0
}

pub fn set_blocking(&mut self, blocking: bool) {
    if blocking {
        self.statflags |= 0x0004;
    } else {
        self.statflags &= !0x0004;
    }
}
```

Add to `impl MapModel`:

```rust
/// Collects map statistics by iterating over all tiles and metadata.
///
/// Performance: Synchronous iteration over the tile hashmap.
pub fn collect_statistics(&self) -> MapStatistics {
    let mut stats = MapStatistics::default();

    stats.tile_count = self.tiles.len() as u64;
    stats.spawn_count = self.spawns.len() as u64;
    stats.house_count = self.houses.len() as u64;
    stats.waypoint_count = self.waypoints.len() as u64;

    let mut unique_towns = HashSet::new();
    for house in &self.houses {
        unique_towns.insert(house.townid());
        stats.total_house_sqm += house.size() as u64;
    }
    stats.town_count = unique_towns.len() as u64;

    for spawn in &self.spawns {
        stats.creature_count += spawn.creatures().len() as u64;
    }

    for tile in self.tiles.values() {
        if tile.is_blocking() {
            stats.blocking_tile_count += 1;
        } else {
            stats.walkable_tile_count += 1;
        }
        stats.item_count += tile.size() as u64;
    }

    stats
}
```

In `crates/rme_core/src/editor.rs`, update map import and add method inside `#[pymethods] impl EditorShellState`:

```rust
use crate::map::{
    Creature, House, MapModel, MapPosition, MapStatistics, Spawn, Waypoint, DEFAULT_X, DEFAULT_Y,
    DEFAULT_Z,
};

fn collect_statistics(&self) -> MapStatistics {
    self.map.collect_statistics()
}
```

In `crates/rme_core/src/lib.rs`, register the class:

```rust
m.add_class::<map::MapStatistics>()?;
```

- [x] **Step 4: Run Rust GREEN**

Run same cargo command from Step 2.

Expected: `1 passed`.

## Task 2: Python Bridge And Dialog

**Files:**
- Modify: `pyrme/core_bridge.py`
- Create: `pyrme/ui/dialogs/map_statistics.py`
- Modify: `pyrme/ui/dialogs/__init__.py`
- Create: `tests/python/test_map_statistics_dialog.py`

- [x] **Step 1: Write failing Python dialog test**

Create `tests/python/test_map_statistics_dialog.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from pyrme.ui.dialogs.map_statistics import MapStatisticsDialog


@dataclass(slots=True)
class _Stats:
    tile_count: int = 10
    blocking_tile_count: int = 3
    walkable_tile_count: int = 7
    item_count: int = 15
    spawn_count: int = 2
    creature_count: int = 4
    house_count: int = 2
    total_house_sqm: int = 20
    town_count: int = 1
    waypoint_count: int = 5


class _ShellState:
    def collect_statistics(self) -> _Stats:
        return _Stats()


def test_map_statistics_dialog_reads_core_stat_fields(qtbot) -> None:
    dialog = MapStatisticsDialog(shell_state=_ShellState())
    qtbot.addWidget(dialog)

    assert dialog.tile_count.text() == "10"
    assert dialog.item_count.text() == "15"
    assert dialog.blocking_tiles.text() == "3"
    assert dialog.walkable_tiles.text() == "7"
    assert dialog.spawn_count.text() == "2"
    assert dialog.creature_count.text() == "4"
    assert dialog.waypoint_count.text() == "5"
    assert dialog.house_count.text() == "2"
    assert dialog.house_sqm.text() == "20"
    assert dialog.town_count.text() == "1"
    assert dialog.pathable_perc.text() == "70.0%"
    assert dialog.sqm_per_house.text() == "10.0"
```

- [x] **Step 2: Run test to verify RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen /tmp/rme-noct-m025-py312/bin/python -m pytest tests/python/test_map_statistics_dialog.py -q --tb=short
```

Expected: FAIL with `ModuleNotFoundError` for `pyrme.ui.dialogs.map_statistics`.

- [x] **Step 3: Implement bridge and dialog**

Add to `_FallbackEditorShellState` in `pyrme/core_bridge.py`:

```python
def collect_statistics(self) -> Any:
    return None
```

Add to `EditorShellCoreBridge` in `pyrme/core_bridge.py`:

```python
def collect_statistics(self) -> Any:
    if hasattr(self._inner, "collect_statistics"):
        return self._inner.collect_statistics()
    return None
```

Create `pyrme/ui/dialogs/map_statistics.py` with:

```python
"""Map statistics dialog."""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss, qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY


class StatCard(QFrame):
    """A compact section for related map statistics."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {qss_color(THEME.obsidian_glass)};
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 8px;
            }}
        """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title.upper())
        self.title_label.setFont(TYPOGRAPHY.ui_label(11, 700))
        self.title_label.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        layout.addWidget(self.title_label)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        layout.addLayout(self.grid)
        self.row = 0

    def add_stat(self, label: str, value: str) -> QLabel:
        lbl = QLabel(label)
        lbl.setFont(TYPOGRAPHY.ui_label(12))
        lbl.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")

        val = QLabel(value)
        val.setFont(TYPOGRAPHY.code_label(13, 600))
        val.setStyleSheet(f"color: {qss_color(THEME.moonstone_white)};")
        val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.grid.addWidget(lbl, self.row, 0)
        self.grid.addWidget(val, self.row, 1)
        self.row += 1
        return val


class MapStatisticsDialog(QDialog):
    """Read-only dashboard for map statistics aggregated from Rust core."""

    DIALOG_SIZE = QSize(640, 520)

    def __init__(self, parent: QWidget | None = None, shell_state=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Map Statistics")
        self.resize(self.DIALOG_SIZE)
        self.setMinimumSize(560, 460)
        self._shell_state = shell_state

        self.setStyleSheet(dialog_base_qss())
        self._build_layout()
        self.refresh_stats()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        heading = QLabel("Map Statistics")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        grid = QGridLayout()
        grid.setSpacing(16)

        self.env_card = StatCard("Environment")
        self.tile_count = self.env_card.add_stat("Tile Count:", "0")
        self.item_count = self.env_card.add_stat("Item Count:", "0")
        self.blocking_tiles = self.env_card.add_stat("Blocking Tiles:", "0")
        self.walkable_tiles = self.env_card.add_stat("Walkable Tiles:", "0")
        grid.addWidget(self.env_card, 0, 0)

        self.pop_card = StatCard("Population")
        self.spawn_count = self.pop_card.add_stat("Spawn Count:", "0")
        self.creature_count = self.pop_card.add_stat("Creature Count:", "0")
        self.waypoint_count = self.pop_card.add_stat("Waypoints:", "0")
        grid.addWidget(self.pop_card, 0, 1)

        self.housing_card = StatCard("Housing")
        self.house_count = self.housing_card.add_stat("House Count:", "0")
        self.house_sqm = self.housing_card.add_stat("Total House SQM:", "0")
        self.town_count = self.housing_card.add_stat("Towns:", "0")
        grid.addWidget(self.housing_card, 1, 0)

        self.ratios_card = StatCard("Ratios")
        self.pathable_perc = self.ratios_card.add_stat("Pathable Tiles:", "0%")
        self.sqm_per_house = self.ratios_card.add_stat("Avg SQM / House:", "0")
        grid.addWidget(self.ratios_card, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(ghost_button_qss())
        self.close_btn.clicked.connect(self.accept)
        footer.addWidget(self.close_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(primary_button_qss())
        self.refresh_btn.clicked.connect(self.refresh_stats)
        footer.addWidget(self.refresh_btn)

        layout.addLayout(footer)

    def refresh_stats(self) -> None:
        if not self._shell_state:
            return

        stats = self._shell_state.collect_statistics()
        if not stats:
            return

        self.tile_count.setText(f"{stats.tile_count:,}")
        self.item_count.setText(f"{stats.item_count:,}")
        self.blocking_tiles.setText(f"{stats.blocking_tile_count:,}")
        self.walkable_tiles.setText(f"{stats.walkable_tile_count:,}")
        self.spawn_count.setText(f"{stats.spawn_count:,}")
        self.creature_count.setText(f"{stats.creature_count:,}")
        self.waypoint_count.setText(f"{stats.waypoint_count:,}")
        self.house_count.setText(f"{stats.house_count:,}")
        self.house_sqm.setText(f"{stats.total_house_sqm:,}")
        self.town_count.setText(f"{stats.town_count:,}")

        pathable = (
            stats.walkable_tile_count / stats.tile_count * 100
            if stats.tile_count > 0
            else 0
        )
        self.pathable_perc.setText(f"{pathable:.1f}%")

        avg_sqm = (
            stats.total_house_sqm / stats.house_count
            if stats.house_count > 0
            else 0
        )
        self.sqm_per_house.setText(f"{avg_sqm:.1f}")
```

In `pyrme/ui/dialogs/__init__.py`, import and export:

```python
from pyrme.ui.dialogs.map_statistics import MapStatisticsDialog

__all__ = [
    ...
    "MapStatisticsDialog",
]
```

- [x] **Step 4: Run Python GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen /tmp/rme-noct-m025-py312/bin/python -m pytest tests/python/test_map_statistics_dialog.py -q --tb=short
```

Expected: `1 passed`.

## Task 3: MainWindow Menu Integration

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Modify: `tests/python/test_legacy_map_menu.py`

- [x] **Step 1: Write failing menu integration test**

In `tests/python/test_legacy_map_menu.py`, add:

```python
class _MapStatisticsDialog:
    opened = False
    parent = None
    shell_state = None

    def __init__(self, parent=None, shell_state=None) -> None:
        type(self).parent = parent
        type(self).shell_state = shell_state

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)
```

Remove `(window.map_statistics_action, "map statistics"),` from
`test_map_backend_gap_actions_are_safe_until_backend_exists`.

Add:

```python
def test_map_statistics_action_uses_dialog_seam(qtbot, settings_workspace: Path) -> None:
    _MapStatisticsDialog.opened = False
    _MapStatisticsDialog.parent = None
    _MapStatisticsDialog.shell_state = None
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-statistics-action.ini"),
        enable_docks=False,
        map_statistics_dialog_factory=_MapStatisticsDialog,
    )
    qtbot.addWidget(window)

    window.map_statistics_action.trigger()

    assert _MapStatisticsDialog.opened is True
    assert _MapStatisticsDialog.parent is window
    assert _MapStatisticsDialog.shell_state is not None
```

- [x] **Step 2: Run test to verify RED**

Run:

```bash
QT_QPA_PLATFORM=offscreen /tmp/rme-noct-m025-py312/bin/python -m pytest tests/python/test_legacy_map_menu.py::test_map_statistics_action_uses_dialog_seam -q --tb=short
```

Expected: FAIL because `MainWindow.__init__` has no `map_statistics_dialog_factory`.

- [x] **Step 3: Implement MainWindow wiring**

In `pyrme/ui/main_window.py`, import `MapStatisticsDialog`, add constructor arg
`map_statistics_dialog_factory=None`, assign:

```python
self._map_statistics_dialog_factory = (
    map_statistics_dialog_factory or MapStatisticsDialog
)
```

Replace `_show_map_statistics()` with:

```python
def _show_map_statistics(self) -> None:
    shell_state = getattr(self._canvas, "_shell_core", None)
    dialog = self._map_statistics_dialog_factory(self, shell_state=shell_state)
    dialog.exec()
```

- [x] **Step 4: Run menu GREEN**

Run:

```bash
QT_QPA_PLATFORM=offscreen /tmp/rme-noct-m025-py312/bin/python -m pytest tests/python/test_legacy_map_menu.py::test_map_statistics_action_uses_dialog_seam tests/python/test_legacy_map_menu.py::test_map_backend_gap_actions_are_safe_until_backend_exists -q --tb=short
```

Expected: `2 passed`.

## Task 4: Slice Verification And GSD Closeout

**Files:**
- Modify: `.gsd/milestones/M025-map-statistics/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M025-map-statistics/slices/S01/S01-SUMMARY.md`
- Modify: `.gsd/STATE.md`

- [x] **Step 1: Run full slice verification**

Run all verification commands from `M025-CONTEXT.md`.

Expected:

- `npm run preflight --silent`: Validation ok.
- Python target suite: all tests pass.
- Rust target test: `1 passed`.
- `ruff`: All checks passed.
- `rustfmt --check --edition 2021` on touched Rust files: no diff.
- `git diff --check`: no output.

- [x] **Step 2: Run caveman-review gap check**

Review only touched diff. Expected: no blocking gap.

- [x] **Step 3: Write summary**

Create `.gsd/milestones/M025-map-statistics/slices/S01/S01-SUMMARY.md`:

```markdown
# M025 Map Statistics S01 Summary

## Completed

- Added Rust `MapStatistics` aggregation on `MapModel`.
- Exposed `collect_statistics()` through `EditorShellState` and Python bridge.
- Added `MapStatisticsDialog`.
- Wired `Map -> Statistics` to real dialog seam.
- Kept cleanup actions as explicit safe gaps.

## Verification

- `npm run preflight --silent`: passed
- `test_map_statistics_dialog.py test_legacy_map_menu.py`: passed
- `cargo test -p rme_core map_model_collects_statistics_from_tiles_and_sidecars`: passed
- `ruff`: passed
- `rustfmt --check --edition 2021` on touched Rust files: passed
- `git diff --check`: passed

## Notes

- Branch is intentionally based on `gsd/M018/S01` because `origin/main` lacks
  the full map sidecar domains this slice consumes.
- Fallback shell returns `None`; UI shows zeros instead of fake statistics.
```

- [x] **Step 4: Update plan and state**

Mark tasks done in this plan and update `.gsd/STATE.md`:

```markdown
**Active Milestone:** M025-map-statistics
**Active Slice:** S01
**Active Task:** complete
**Phase:** review
**Next Action:** caveman-review clean, then commit and prepare PR/stack decision.
```

- [x] **Step 5: Commit**

Run:

```bash
git add crates/rme_core/src/map.rs crates/rme_core/src/editor.rs crates/rme_core/src/lib.rs pyrme/core_bridge.py pyrme/ui/dialogs/__init__.py pyrme/ui/dialogs/map_statistics.py pyrme/ui/main_window.py tests/python/test_map_statistics_dialog.py tests/python/test_legacy_map_menu.py .gsd/milestones/M025-map-statistics/DESIGN.md .gsd/milestones/M025-map-statistics/M025-CONTEXT.md .gsd/milestones/M025-map-statistics/slices/S01/S01-PLAN.md .gsd/milestones/M025-map-statistics/slices/S01/S01-SUMMARY.md .gsd/STATE.md
git commit -m "feat(M025/S01): add map statistics dialog"
```
