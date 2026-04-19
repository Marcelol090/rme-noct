from __future__ import annotations

from pyrme.ui.main_window import MainWindow


def test_renderer_host_reports_frame_plan_after_tool_application(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._set_active_item_selection("Stone", 2148)

    changed = window._apply_active_tool_at_cursor()

    assert changed is True
    assert "frame plan: 1 visible tile @ floor 07" in window._canvas.diagnostic_text()
    assert "Tile Primitives: 1" in window._canvas.diagnostic_text()
    assert "Visible Tiles: 1" in window._canvas.diagnostic_text()
    assert "Map Generation: 1" in window._canvas.diagnostic_text()
    assert "Visible Rect:" in window._canvas.diagnostic_text()


def test_renderer_host_frame_plan_updates_after_erasing(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._set_active_item_selection("Stone", 2148)
    window._apply_active_tool_at_cursor()

    window._editor_context.session.mode = "erasing"
    changed = window._apply_active_tool_at_cursor()

    assert changed is True
    assert "frame plan: 0 visible tiles @ floor 07" in window._canvas.diagnostic_text()
    assert "Tile Primitives: 0" in window._canvas.diagnostic_text()
    assert "Visible Tiles: 0" in window._canvas.diagnostic_text()


def test_renderer_host_canvas_frame_updates_when_viewport_moves(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._set_active_item_selection("Stone", 2148)
    assert window._apply_active_tool_at_cursor() is True
    assert "Visible Tiles: 1" in window._canvas.diagnostic_text()
    tile_position = window._canvas.canvas_frame().tiles[0].position

    window._set_current_position(tile_position.x + 100, tile_position.y + 100, 7)

    assert "Visible Tiles: 0" in window._canvas.diagnostic_text()
