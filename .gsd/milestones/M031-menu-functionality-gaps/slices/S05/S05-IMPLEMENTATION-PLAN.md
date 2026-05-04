# M031/S05 Selection Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Selection menu item operations act on selected tiles when current map data supports the behavior.

**Architecture:** Reuse the S04 `EditorModel` item replacement/removal helpers with `positions=selection_positions`. Add one pure selected-item summary helper. Wire `MainWindow` selection actions through the existing `EditTransformService` seam and keep unsupported item-type filters as exact deferred evidence.

**Tech Stack:** Python 3, PyQt6, pytest-qt, existing `EditorModel` and `MainWindow` shell contracts.

---

## Task 1: RED Selection Operation Tests

**Files:**
- Modify: `tests/python/test_legacy_selection_menu.py`

- [ ] **Step 1: Add failing tests for selected-area mutation and search**

Add tests that create two selected tiles and one unselected tile, then assert:
- `replace_on_selection_items` replaces only selected occurrences.
- `remove_on_selection_item` removes only selected occurrences.
- `search_on_selection_item` reports selected occurrences for one chosen item ID.
- `search_on_selection_everything` reports total selected tile/item counts.
- `search_on_selection_unique` reports unique selected item IDs.
- `search_on_selection_action/container/writeable` report exact missing `TileState` type-flag evidence.

- [ ] **Step 2: Verify RED**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short
```

Expected:
- FAIL because selection actions still call `_show_unavailable`.

## Task 2: EditorModel Selected Item Summary

**Files:**
- Modify: `pyrme/editor/model.py`
- Test: `tests/python/test_legacy_selection_menu.py`

- [ ] **Step 1: Add pure selected item tests**

Assert a new `EditorModel.selection_item_counts()` returns item occurrence counts only from selected tiles.

- [ ] **Step 2: Verify RED**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py::test_editor_model_counts_selected_item_occurrences -q --tb=short
```

Expected:
- FAIL with missing `selection_item_counts`.

- [ ] **Step 3: Implement minimal helper**

Add `selection_item_counts(self) -> dict[int, int]` that counts ground and stack item IDs from selected tiles only.

- [ ] **Step 4: Verify GREEN**

Run same targeted test.

Expected:
- PASS.

## Task 3: MainWindow Selection Wiring

**Files:**
- Modify: `pyrme/ui/main_window.py`
- Test: `tests/python/test_legacy_selection_menu.py`

- [ ] **Step 1: Wire replace/remove/search actions**

Use existing `EditTransformService.choose_replace_items`, `choose_remove_items_by_id`, and `confirm_map_transform`.

Selection-scoped actions must call:
- `editor.replace_item_id(old_id, new_id, editor.selection_positions)`
- `editor.remove_item_id(item_id, editor.selection_positions)`
- `editor.selection_item_counts()`

- [ ] **Step 2: Keep unsupported filters explicit**

Action/Container/Writeable statuses must say `TileState has no item type flags.`

- [ ] **Step 3: Verify GREEN**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short
```

Expected:
- PASS.

## Task 4: Closeout

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/S05-PLAN.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/S05-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/T01-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/T02-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/T03-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/T04-SUMMARY.md`
- Create: `.gsd/milestones/M031-menu-functionality-gaps/slices/S05/T05-SUMMARY.md`

- [ ] **Step 1: Mark plan tasks complete**

Mark every S05 task `[x]`.

- [ ] **Step 2: Record evidence**

Summaries must include RED evidence, targeted PASS evidence, and exact deferred-data gaps.

- [ ] **Step 3: Verify**

Run:
```bash
QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short
rtk python3 -m ruff check pyrme/editor/model.py pyrme/ui/main_window.py tests/python/test_legacy_selection_menu.py
rtk git diff --check
```

Expected:
- All pass.
