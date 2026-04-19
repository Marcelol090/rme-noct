from __future__ import annotations

from pyrme.editor import MapModel, MapPosition, TileState
from pyrme.rendering.frame_plan import build_render_frame_plan
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def _centered_viewport(width: int = 64, height: int = 64) -> EditorViewport:
    viewport = EditorViewport(
        ViewportSnapshot(center_x=32000, center_y=32000, floor=7)
    )
    viewport.set_view_size(width, height)
    return viewport


def test_frame_plan_is_empty_for_empty_map() -> None:
    viewport = _centered_viewport()

    plan = build_render_frame_plan(MapModel(), viewport)

    assert plan.tile_count == 0
    assert plan.tile_commands == ()
    assert plan.summary() == "frame plan: 0 visible tiles @ floor 07"


def test_frame_plan_includes_visible_tiles_on_current_floor() -> None:
    viewport = _centered_viewport()
    map_model = MapModel()
    map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=2148,
            item_ids=(100, 101),
        )
    )

    plan = build_render_frame_plan(map_model, viewport)

    assert plan.tile_count == 1
    assert plan.tile_commands[0].position == MapPosition(32000, 32000, 7)
    assert plan.tile_commands[0].ground_item_id == 2148
    assert plan.tile_commands[0].item_ids == (100, 101)


def test_frame_plan_rejects_tiles_outside_visible_rect_or_floor() -> None:
    viewport = _centered_viewport()
    map_model = MapModel()
    map_model.set_tile(TileState(position=MapPosition(32000, 32000, 6), ground_item_id=1))
    map_model.set_tile(TileState(position=MapPosition(32100, 32100, 7), ground_item_id=2))

    plan = build_render_frame_plan(map_model, viewport)

    assert plan.tile_count == 0


def test_frame_plan_command_order_is_stable_by_map_position() -> None:
    viewport = _centered_viewport(128, 128)
    map_model = MapModel()
    map_model.set_tile(TileState(position=MapPosition(32001, 32000, 7), ground_item_id=2))
    map_model.set_tile(TileState(position=MapPosition(32000, 32000, 7), ground_item_id=1))

    plan = build_render_frame_plan(map_model, viewport.snapshot())

    assert [command.position for command in plan.tile_commands] == [
        MapPosition(32000, 32000, 7),
        MapPosition(32001, 32000, 7),
    ]
