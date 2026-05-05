# M031/S06 Map Cleanup Statistics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Map menu statistics gap with real in-memory map statistics and keep unsupported cleanup actions honest.

**Architecture:** Add a small Python statistics snapshot derived from `EditorModel.map_model`. Inject it into `MapStatisticsDialog` from `MainWindow` so the action is testable without opening a blocking modal. Keep cleanup invalid tiles/zones as explicit deferred actions because current Python tile state has no invalid item/zone flags.

**Tech Stack:** Python 3, PyQt6, pytest-qt, existing `EditorModel`, `MainWindow`, and `MapStatisticsDialog`.

---

## Task 1: RED Map Statistics and Cleanup Tests

**Files:**
- Modify: `tests/python/test_legacy_map_menu.py`

- [ ] **Step 1: Add failing tests**

Add tests that assert:
- Cleanup invalid tiles reports `Cleanup invalid tiles deferred: TileState has no invalid item or unresolved item flags.`
- Cleanup invalid zones reports `Cleanup invalid zones deferred: TileState has no invalid zone or opaque OTBM fragment fields.`
- `map_statistics_action` passes current map-derived statistics into an injected dialog factory and does not hang.
- Town Manager, House Manager, and Map Properties still open through their seams.

- [ ] **Step 2: Verify RED**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short
```

Expected:
- FAIL because cleanup messages are generic unavailable text and statistics dialog factory injection/data bridge are missing.

## Task 2: Map Statistics Snapshot

**Files:**
- Modify: `pyrme/editor/model.py`
- Modify: `pyrme/ui/dialogs/map_statistics.py`
- Test: `tests/python/test_legacy_map_menu.py`

- [ ] **Step 1: Add minimal statistics shape**

Add an immutable Python data shape with fields already consumed by `MapStatisticsDialog`: `tile_count`, `item_count`, `blocking_tile_count`, `walkable_tile_count`, `spawn_count`, `creature_count`, `waypoint_count`, `house_count`, `total_house_sqm`, and `town_count`.

- [ ] **Step 2: Derive real values from `MapModel`**

Only `tile_count` and `item_count` are real in this slice. Set unsupported sidecar/population values to `0`. Treat all current in-memory tiles as walkable and blocking count as `0` because no blocking flags exist.

- [ ] **Step 3: Verify GREEN**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short
```

Expected:
- PASS for statistics bridge tests.

## Task 3: MainWindow Map Action Wiring

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Test: `tests/python/test_legacy_map_menu.py`

- [ ] **Step 1: Inject map statistics dialog factory**

Add `map_statistics_dialog_factory` optional constructor seam, defaulting to `MapStatisticsDialog`.

- [ ] **Step 2: Feed current editor statistics**

Change `_show_map_statistics()` to instantiate the dialog with current `EditorModel` statistics.

- [ ] **Step 3: Replace generic cleanup gaps**

Wire cleanup invalid tiles/zones to exact deferred evidence messages.

- [ ] **Step 4: Verify GREEN**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short
```

Expected:
- PASS.

## Task 4: Closeout

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/S06-PLAN.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/S06-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/T01-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/T02-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/T03-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/T04-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S06/T05-SUMMARY.md`

- [ ] **Step 1: Mark plan tasks complete**

Mark every S06 task `[x]`.

- [ ] **Step 2: Record evidence**

Summaries must include RED evidence, targeted PASS evidence, and exact cleanup missing-data reasons.

- [ ] **Step 3: Verify**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_map_menu.py -q --tb=short
rtk python3 -m ruff check pyrme/editor/model.py pyrme/ui/main_window.py pyrme/ui/dialogs/map_statistics.py tests/python/test_legacy_map_menu.py
rtk git diff --check
```

Expected:
- All pass.
