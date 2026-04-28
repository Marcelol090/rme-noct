# M007 Context - Brush activation backend

## Why

After the Item palette selection seam exists, the editor needs a canonical backend contract for active mode, active brush id, active item id, and tool application behavior.

## Contract

- `EditorModel` is the canonical owner of editor activation state.
- `EditorSessionState` delegates mode and active brush/item fields to the backend editor.
- Drawing with an active item writes that item as tile ground.
- Erasing removes existing tiles.
- Selection mode records positions without duplicating work.

## Non-Goals

- No extra palette UI wiring in this slice.
- No toolbar redesign.
- No fake draw behavior beyond `EditorModel.apply_active_tool_at`.
