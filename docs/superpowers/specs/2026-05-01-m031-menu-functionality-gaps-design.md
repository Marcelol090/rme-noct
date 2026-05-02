# M031 Menu Functionality Gaps - Design

## Brainstorm

- Current parity covers menu order, labels, shortcuts, and safe status messages, but many File/Edit/Selection/Map actions still call `_show_unavailable`.
- Legacy behavior lives in `remeres-map-editor-redux` handlers: file lifecycle in `editor_manager.cpp`, edit/clipboard in `copy_operations.cpp`, selection/search in `search_handler.cpp`, map actions in `map_actions_handler.cpp`.
- Safest milestone shape is one behavior slice per menu area, with tests first and no broad UI redesign.

## Choice

Create `M031-menu-functionality-gaps` as a behavior-first milestone. Close real command gaps behind existing `MainWindow`, `EditorModel`, `EditorShellCoreBridge`, and dialog seams. Keep menu XML structure unchanged.

## Evidence

- `pyrme/assets/contracts/legacy/menubar.xml` is tracked source for File/Edit/Selection/Map labels and shortcuts.
- `pyrme/ui/main_window.py` currently wires many target actions to `_show_unavailable`.
- `tests/python/test_legacy_file_menu.py`, `test_legacy_edit_menu.py`, `test_legacy_selection_menu.py`, and `test_legacy_map_menu.py` assert current safe gaps.
- Current verification gap: `test_legacy_map_menu.py::test_map_backend_gap_actions_are_safe_until_backend_exists` hangs because `map_statistics_action` opens a modal while the test still expects a safe gap.
- Legacy reference-only files read from root checkout:
  - `remeres-map-editor-redux/source/editor/managers/editor_manager.cpp`
  - `remeres-map-editor-redux/source/editor/operations/copy_operations.cpp`
  - `remeres-map-editor-redux/source/editor/operations/selection_operations.cpp`
  - `remeres-map-editor-redux/source/ui/menubar/search_handler.cpp`
  - `remeres-map-editor-redux/source/ui/menubar/map_actions_handler.cpp`
  - `remeres-map-editor-redux/source/map/operations/map_processor.cpp`

## Scope

- File menu lifecycle, recent files, import/export/reload/report gaps.
- Edit menu undo/redo, cut/copy/paste, replace, borderize/randomize, remove/clear actions.
- Selection menu replace/search/remove/find gaps.
- Map menu cleanup/statistics/property data gaps.

## Non-goals

- No menu label/order changes unless legacy XML changes.
- No renderer sprite parity.
- No untested destructive map mutation.
- No broad rewrite of `MainWindow`.
- No hidden stub replacing a gap; unsupported behavior must stay explicit until implemented.

## Acceptance

- Every slice starts with failing tests for the specific menu gap.
- Each action either performs tested legacy-aligned behavior or remains documented as out of scope in that slice.
- Targeted tests pass for touched menu group.
- Full Python menu regression tests pass before milestone closeout.
