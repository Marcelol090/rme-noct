# M031/S04 Summary - Edit Map Transforms

## Done

- Added RED/GREEN coverage for Edit transform map mutation, confirmation seams, clear modified state, and exact deferred backend evidence.
- Added pure `EditorModel.replace_item_id`, `remove_item_id`, and `clear_modified_state` operations with undo history for map mutations.
- Wired `MainWindow` Replace Items and Remove Items by ID through an injectable `EditTransformService` plus confirmation seam.
- Kept Borderize/Randomize/Corpse/Unreachable/Invalid House actions deferred with exact missing-data evidence.

## Verification

- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_edit_menu.py -q --tb=short` -> 11 passed.
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_edit_menu.py tests/python/test_editor_activation_backend.py tests/python/test_canvas_seam_m4.py -q --tb=short` -> 42 passed.
- `rtk python3 -m ruff check pyrme/editor/model.py pyrme/ui/main_window.py tests/python/test_legacy_edit_menu.py` -> passed.
- `rtk git diff --check` -> passed.

## Remaining Evidence Gaps

- Borderize actions cannot mutate Python map state yet: `rme_core::AutoborderPlan` has no Python bridge or map mutation consumer.
- Randomize actions lack ground variant catalog data on `TileState`.
- Corpse cleanup lacks item type flags.
- Unreachable cleanup lacks pathing/visibility graph.
- Invalid house cleanup lacks per-tile house IDs.
