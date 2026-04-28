from __future__ import annotations

from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


def test_viewport_clamps_center_floor_and_zoom() -> None:
    viewport = EditorViewport()

    viewport.set_center(99_999, -10, 99)
    viewport.set_zoom_percent(1)

    assert viewport.center == (65000, 0, 15)
    assert viewport.zoom_percent == 10

    viewport.set_floor(-5)
    viewport.set_zoom_percent(900)

    assert viewport.center == (65000, 0, 0)
    assert viewport.zoom_percent == 800


def test_viewport_computes_centered_scroll_from_legacy_tile_space() -> None:
    viewport = EditorViewport()
    viewport.set_view_size(640, 480)

    viewport.set_center(32000, 32100, 7)

    assert viewport.scroll_origin == (1_023_680, 1_026_960)
    assert viewport.legacy_zoom_scale == 1.0

    viewport.set_zoom_percent(200)

    assert viewport.scroll_origin == (1_023_840, 1_027_080)
    assert viewport.legacy_zoom_scale == 0.5


def test_viewport_applies_floor_offset_to_centered_scroll() -> None:
    viewport = EditorViewport()
    viewport.set_view_size(640, 480)

    viewport.set_center(32000, 32000, 5)

    assert viewport.scroll_origin == (1_023_616, 1_023_696)


def test_viewport_scroll_updates_center_and_snapshot_round_trips() -> None:
    viewport = EditorViewport()
    viewport.set_view_size(640, 480)
    viewport.scroll_to(1_024_000, 1_024_320)

    assert viewport.center == (32010, 32017, 7)

    viewport.scroll_relative(64, -32)
    snapshot = viewport.snapshot()

    assert snapshot == ViewportSnapshot(
        center_x=32012,
        center_y=32016,
        floor=7,
        zoom_percent=100,
        logical_width=640,
        logical_height=480,
        scale_factor=1.0,
        scroll_x=1_024_064,
        scroll_y=1_024_288,
    )

    restored = EditorViewport()
    restored.restore(snapshot)

    assert restored.snapshot() == snapshot


def test_viewport_translates_screen_points_through_legacy_scroll_zoom_and_floor() -> None:
    viewport = EditorViewport()
    viewport.set_view_size(640, 480)
    viewport.set_center(32000, 32100, 7)

    assert viewport.screen_to_map(320, 240) == (32000, 32100, 7)
    assert viewport.screen_to_map(0, 0) == (31990, 32092, 7)
    assert viewport.map_to_screen(32000, 32100, 7) == (320, 240)

    viewport.set_zoom_percent(200)

    assert viewport.screen_to_map(320, 240) == (32000, 32100, 7)
    assert viewport.screen_to_map(0, 0) == (31995, 32096, 7)
    assert viewport.map_to_screen(32000, 32100, 7) == (320, 240)


def test_viewport_translation_applies_above_ground_floor_offset() -> None:
    viewport = EditorViewport()
    viewport.set_view_size(640, 480)
    viewport.set_center(32000, 32000, 5)

    assert viewport.screen_to_map(320, 240) == (32000, 32000, 5)
    assert viewport.screen_to_map(0, 0) == (31990, 31992, 5)
    assert viewport.map_to_screen(32000, 32000, 5) == (320, 240)


def test_viewport_visible_rect_matches_legacy_padding() -> None:
    viewport = EditorViewport()
    viewport.set_view_size(640, 480)
    viewport.set_center(32000, 32100, 7)

    assert viewport.visible_rect() == (31990.0, 32092.5, 21.0, 16.0)
