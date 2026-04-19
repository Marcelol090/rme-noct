from __future__ import annotations

from pyrme.editor import MapModel, MapPosition, TileState
from pyrme.rendering.diagnostic_primitives import build_diagnostic_tile_primitives
from pyrme.rendering.frame_plan import build_render_frame_plan
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def _viewport(zoom_percent: int = 100) -> EditorViewport:
    viewport = EditorViewport(
        ViewportSnapshot(
            center_x=32000,
            center_y=32000,
            floor=7,
            zoom_percent=zoom_percent,
        )
    )
    viewport.set_view_size(128, 128)
    return viewport


def test_diagnostic_primitives_map_tile_commands_to_screen_rects() -> None:
    map_model = MapModel()
    map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=2148,
            item_ids=(100, 101),
        )
    )
    viewport = _viewport()
    plan = build_render_frame_plan(map_model, viewport)

    primitives = build_diagnostic_tile_primitives(plan, viewport)

    assert len(primitives) == 1
    assert primitives[0].position == MapPosition(32000, 32000, 7)
    assert primitives[0].screen_rect == (64, 64, 32, 32)
    assert primitives[0].label == "2148 +2"


def test_diagnostic_primitives_scale_with_viewport_zoom() -> None:
    map_model = MapModel()
    map_model.set_tile(TileState(position=MapPosition(32000, 32000, 7), ground_item_id=1))
    normal_viewport = _viewport(100)
    zoomed_viewport = _viewport(200)

    normal = build_diagnostic_tile_primitives(
        build_render_frame_plan(map_model, normal_viewport),
        normal_viewport,
    )
    zoomed = build_diagnostic_tile_primitives(
        build_render_frame_plan(map_model, zoomed_viewport),
        zoomed_viewport,
    )

    assert normal[0].screen_rect[2:] == (32, 32)
    assert zoomed[0].screen_rect[2:] == (64, 64)


def test_diagnostic_primitives_keep_frame_plan_order() -> None:
    map_model = MapModel()
    map_model.set_tile(TileState(position=MapPosition(32001, 32000, 7), ground_item_id=2))
    map_model.set_tile(TileState(position=MapPosition(32000, 32000, 7), ground_item_id=1))
    viewport = _viewport()
    plan = build_render_frame_plan(map_model, viewport)

    primitives = build_diagnostic_tile_primitives(plan, viewport.snapshot())

    assert [primitive.position for primitive in primitives] == [
        MapPosition(32000, 32000, 7),
        MapPosition(32001, 32000, 7),
    ]
