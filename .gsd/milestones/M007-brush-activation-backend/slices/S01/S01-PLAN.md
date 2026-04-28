# S01: BRUSH-10-ACTIVATION-BACKEND-CONTRACT

**Goal:** Verify the editor backend owns activation state and applies active tools honestly before broader UI command wiring.

**Demo:** A test can set session mode and active item id, apply the active tool at a map position, and observe the canonical map/selection state change.

## Must-Haves

- Session mode delegates to `EditorModel.mode`.
- Session active brush id delegates to `EditorModel.active_brush_id`.
- Session active item id delegates to `EditorModel.active_item_id`.
- Invalid mode values normalize to `drawing`.
- `activate_item_brush`, `activate_palette_brush`, and `clear_active_brush` update canonical state.
- `apply_active_tool_at` handles selection, drawing, erasing, and no-op modes.

## Non Goals

- No new UI commands.
- No toolbar or menu restructuring.
- No fake canvas drawing.

## Verification

- `.\.venv\Scripts\python.exe -m ruff check tests/python/test_editor_activation_backend.py`
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_editor_activation_backend.py -q --tb=short`

## Tasks

- [x] **T01: Cover session/backend activation delegation** `est:10m`
  - Files: `tests/python/test_editor_activation_backend.py`
  - Done when: tests prove session fields read/write through `EditorModel`.

- [x] **T02: Cover backend activation commands** `est:10m`
  - Files: `tests/python/test_editor_activation_backend.py`
  - Done when: item brush, palette brush, clear brush, and invalid mode behavior are tested.

- [x] **T03: Cover active tool behavior** `est:15m`
  - Files: `tests/python/test_editor_activation_backend.py`
  - Done when: selection, drawing, erasing, preserved stack, and unsupported/no-active-item no-op paths are tested.

- [x] **T04: Closeout and scope separation** `est:10m`
  - Files: `.gsd/milestones/M007-brush-activation-backend/slices/S01/S01-SUMMARY.md`, `.gsd/STATE.md`
  - Done when: verification is recorded and UI-shell dirty work remains unstaged.

## Closeout

S01 is complete when backend activation behavior is tested without mixing pending UI-shell changes.
