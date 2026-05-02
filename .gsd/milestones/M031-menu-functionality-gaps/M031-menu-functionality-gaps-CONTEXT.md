# M031 Context - Menu Functionality Gaps

## Why

Legacy menu parity is structurally complete, but File/Edit/Selection/Map still contain behavior gaps covered by safe status tests. M031 converts those gaps into tested shell/core behavior in small slices.

## Contract

- Preserve legacy XML order, labels, shortcuts, and status tips.
- Use legacy C++ behavior as source of truth when behavior is known.
- Replace `_show_unavailable` only when a real backend or explicit seam exists.
- Keep dangerous map-wide operations behind confirmation or pure planning contracts.
- Tests first, implementation second.

## Source Evidence

- `pyrme/assets/contracts/legacy/menubar.xml`
- `pyrme/ui/main_window.py`
- `tests/python/test_legacy_file_menu.py`
- `tests/python/test_legacy_edit_menu.py`
- `tests/python/test_legacy_selection_menu.py`
- `tests/python/test_legacy_map_menu.py`
- Current verification gap: `test_legacy_map_menu.py::test_map_backend_gap_actions_are_safe_until_backend_exists` hangs when `map_statistics_action` opens a modal.
- Reference-only root checkout: `remeres-map-editor-redux/source/editor/managers/editor_manager.cpp`
- Reference-only root checkout: `remeres-map-editor-redux/source/editor/operations/copy_operations.cpp`
- Reference-only root checkout: `remeres-map-editor-redux/source/editor/operations/selection_operations.cpp`
- Reference-only root checkout: `remeres-map-editor-redux/source/ui/menubar/search_handler.cpp`
- Reference-only root checkout: `remeres-map-editor-redux/source/ui/menubar/map_actions_handler.cpp`

## Non-Goals

- No top-level menu contract redesign.
- No broad UI redesign.
- No filesystem import/export behavior without tests and injected seams.
- No fake implementation that only changes status text.
