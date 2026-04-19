from __future__ import annotations

from pyrme.editor import MapPosition, TileState
from pyrme.ui.canvas_frame import build_canvas_frame
from pyrme.ui.editor_context import EditorContext
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def _viewport(width: int = 128, height: int = 128) -> EditorViewport:
    viewport = EditorViewport(
        ViewportSnapshot(
            center_x=32000,
            center_y=32000,
            floor=7,
            zoom_percent=100,
        )
    )
    viewport.set_view_size(width, height)
    return viewport


def test_canvas_frame_is_empty_without_editor_context() -> None:
    frame = build_canvas_frame(None, _viewport())

    assert frame.tiles == ()
    assert frame.map_generation == 0


def test_canvas_frame_includes_visible_tile_with_screen_rect() -> None:
    context = EditorContext()
    viewport = _viewport()
    context.session.editor.map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=2148,
            item_ids=(100, 101),
        )
    )

    frame = build_canvas_frame(context, viewport)

    assert len(frame.tiles) == 1
    tile = frame.tiles[0]
    assert tile.position == MapPosition(32000, 32000, 7)
    assert tile.ground_item_id == 2148
    assert tile.item_ids == (100, 101)
    assert tile.screen_rect == (64, 64, 32, 32)


def test_canvas_frame_excludes_tiles_outside_visible_rect_or_floor() -> None:
    context = EditorContext()
    viewport = _viewport()
    context.session.editor.map_model.set_tile(
        TileState(position=MapPosition(32000, 32000, 6), ground_item_id=1)
    )
    context.session.editor.map_model.set_tile(
        TileState(position=MapPosition(32100, 32100, 7), ground_item_id=2)
    )

    frame = build_canvas_frame(context, viewport)

    assert frame.tiles == ()


def test_canvas_frame_screen_rect_matches_viewport_mapping_within_one_pixel() -> None:
    context = EditorContext()
    viewport = _viewport()
    position = MapPosition(32001, 32000, 7)
    context.session.editor.map_model.set_tile(TileState(position=position, ground_item_id=1))

    frame = build_canvas_frame(context, viewport)

    expected_x, expected_y = viewport.map_to_screen(position.x, position.y, position.z)
    actual_x, actual_y, width, height = frame.tiles[0].screen_rect
    assert abs(actual_x - expected_x) < 1
    assert abs(actual_y - expected_y) < 1
    assert (width, height) == (32, 32)


def test_canvas_frame_tracks_map_generation() -> None:
    context = EditorContext()
    viewport = _viewport()
    context.session.editor.map_model.set_tile(
        TileState(position=MapPosition(32000, 32000, 7), ground_item_id=1)
    )

    frame = build_canvas_frame(context, viewport)

    assert frame.map_generation == context.session.editor.map_model.generation
