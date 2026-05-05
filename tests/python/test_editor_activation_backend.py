from __future__ import annotations

from pyrme.editor import EditorModel, MapPosition, TileState
from pyrme.editor.brushes import brush_placement_for_active_id
from pyrme.ui.editor_context import EditorContext


def test_session_activation_state_delegates_to_editor_backend() -> None:
    context = EditorContext()

    assert context.session.mode == "drawing"
    assert context.session.active_brush_id is None
    assert context.session.active_item_id is None
    assert context.session.editor.mode == "drawing"
    assert context.session.editor.active_brush_id is None
    assert context.session.editor.active_item_id is None

    context.session.mode = "selection"
    context.session.active_brush_id = "item:1"
    context.session.active_item_id = 1

    assert context.session.editor.mode == "selection"
    assert context.session.editor.active_brush_id == "item:1"
    assert context.session.editor.active_item_id == 1


def test_editor_backend_activation_state_reflects_through_session() -> None:
    context = EditorContext()

    context.session.editor.mode = "fill"
    context.session.editor.active_brush_id = "palette:raw"
    context.session.editor.active_item_id = None

    assert context.session.mode == "fill"
    assert context.session.active_brush_id == "palette:raw"
    assert context.session.active_item_id is None


def test_editor_backend_normalizes_invalid_mode_to_drawing() -> None:
    context = EditorContext()

    context.session.editor.mode = "unknown"

    assert context.session.editor.mode == "drawing"
    assert context.session.mode == "drawing"


def test_editor_backend_activation_commands_update_canonical_state() -> None:
    editor = EditorModel()

    editor.set_mode("selection")
    editor.activate_item_brush(2148)

    assert editor.mode == "selection"
    assert editor.active_brush_id == "item:2148"
    assert editor.active_item_id == 2148

    editor.activate_palette_brush("RAW")

    assert editor.active_brush_id == "palette:raw"
    assert editor.active_item_id is None

    editor.clear_active_brush()

    assert editor.active_brush_id is None
    assert editor.active_item_id is None


def test_editor_backend_selection_tool_selects_position_once() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)

    editor.set_mode("selection")

    assert editor.apply_active_tool_at(position) is True
    assert editor.has_selection() is True
    assert editor.apply_active_tool_at(position) is False


def test_editor_backend_drawing_tool_uses_active_item_as_ground() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)

    editor.set_mode("drawing")
    editor.activate_item_brush(2148)

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=2148,
    )
    assert editor.map_model.is_dirty is True


def test_editor_backend_drawing_tool_preserves_existing_item_stack() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.map_model.set_tile(
        TileState(position=position, ground_item_id=100, item_ids=(200, 300))
    )
    editor.map_model.clear_changed()

    editor.set_mode("drawing")
    editor.activate_item_brush(2148)

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=2148,
        item_ids=(200, 300),
    )


def test_editor_backend_ground_catalog_brush_sets_ground_and_preserves_stack() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.map_model.set_tile(
        TileState(position=position, ground_item_id=100, item_ids=(200, 300))
    )
    editor.map_model.clear_changed()

    editor.set_mode("drawing")
    editor.active_brush_id = "brush:ground:10"

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=4526,
        item_ids=(200, 300),
    )


def test_editor_backend_wall_catalog_brush_appends_wall_item_once() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.map_model.set_tile(TileState(position=position, ground_item_id=4526))
    editor.map_model.clear_changed()

    editor.set_mode("drawing")
    editor.active_brush_id = "brush:wall:20"

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=4526,
        item_ids=(3361,),
    )
    assert editor.apply_active_tool_at(position) is False
    assert editor.map_model.get_tile(position) == TileState(
        position=position,
        ground_item_id=4526,
        item_ids=(3361,),
    )


def test_editor_backend_unknown_catalog_brush_noops() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)

    editor.set_mode("drawing")
    editor.active_brush_id = "brush:ground:999"

    assert brush_placement_for_active_id(editor.active_brush_id) is None
    assert editor.apply_active_tool_at(position) is False
    assert editor.map_model.get_tile(position) is None


def test_editor_backend_erasing_tool_removes_existing_tile() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    editor.map_model.set_tile(TileState(position=position, ground_item_id=2148))
    editor.map_model.clear_changed()

    editor.set_mode("erasing")

    assert editor.apply_active_tool_at(position) is True
    assert editor.map_model.get_tile(position) is None
    assert editor.map_model.is_dirty is True


def test_editor_backend_tool_noops_when_operation_is_not_supported() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)

    editor.set_mode("drawing")
    assert editor.apply_active_tool_at(position) is False

    editor.set_mode("fill")
    assert editor.apply_active_tool_at(position) is False

    editor.set_mode("move")
    assert editor.apply_active_tool_at(position) is False
