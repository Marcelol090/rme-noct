from __future__ import annotations

from pyrme.editor import TileState
from pyrme.rendering import SpriteItemMetadata, SpriteResourceResolver
from pyrme.ui.canvas_host import RendererHostCanvasWidget
from pyrme.ui.main_window import MainWindow

SPRITE_BYTE_LEN = 32 * 32 * 4


class _RecordingRenderDispatcher:
    def __init__(self) -> None:
        self.payloads: list[list[dict[str, object]]] = []

    def render_frame(self, sprites: list[dict[str, object]]) -> int:
        self.payloads.append(list(sprites))
        return len(sprites)


class _CountOverrideRenderDispatcher(_RecordingRenderDispatcher):
    def __init__(self, queued_count: int) -> None:
        super().__init__()
        self.queued_count = queued_count

    def render_frame(self, sprites: list[dict[str, object]]) -> int:
        super().render_frame(sprites)
        return self.queued_count


class _FailingRenderDispatcher:
    def render_frame(self, sprites: list[dict[str, object]]) -> int:
        raise RuntimeError("renderer boom")


def _sprite_pixels(seed: int) -> bytes:
    return bytes((seed + index) % 256 for index in range(SPRITE_BYTE_LEN))


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
    assert (
        "Sprite Resources: 1 total | resolved 0 | missing item 1 | missing sprite 0"
        in window._canvas.diagnostic_text()
    )


def test_renderer_host_sprite_diagnostics_use_injected_resolver(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._canvas.set_sprite_resource_resolver(
        SpriteResourceResolver(
            items={
                2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
            },
            sprites={
                55: b"stone",
            },
        )
    )
    window._set_active_item_selection("Stone", 2148)

    changed = window._apply_active_tool_at_cursor()

    assert changed is True
    assert (
        "Sprite Resources: 1 total | resolved 1 | missing item 0 | missing sprite 0"
        in window._canvas.diagnostic_text()
    )


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


def test_renderer_host_paintgl_dispatches_resolved_sprite_payload_to_rme_core(
    qtbot,
) -> None:
    dispatcher = _RecordingRenderDispatcher()
    window = MainWindow(
        canvas_factory=lambda parent=None: RendererHostCanvasWidget(
            parent,
            render_dispatcher=dispatcher,
        )
    )
    qtbot.addWidget(window)
    window._canvas.set_sprite_resource_resolver(
        SpriteResourceResolver(
            items={
                2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
                3031: SpriteItemMetadata(item_id=3031, sprite_ids=(77,)),
            },
            sprites={
                55: _sprite_pixels(1),
                77: _sprite_pixels(2),
            },
        )
    )
    window._set_active_item_selection("Stone", 2148)
    assert window._apply_active_tool_at_cursor() is True
    tile_position = window._canvas.canvas_frame().tiles[0].position
    window._editor_context.session.document.map_model.set_tile(
        TileState(position=tile_position, ground_item_id=2148, item_ids=(3031,))
    )
    window._canvas._state_changed()
    window._canvas._paint_diagnostics = lambda painter: None

    window._canvas.paintGL()

    assert dispatcher.payloads == [
        [
            {
                "x": tile_position.x,
                "y": tile_position.y,
                "layer": 0,
                "sprite_id": 55,
                "pixels": _sprite_pixels(1),
            },
            {
                "x": tile_position.x,
                "y": tile_position.y,
                "layer": 1,
                "sprite_id": 77,
                "pixels": _sprite_pixels(2),
            },
        ]
    ]
    assert "Sprite Dispatch: 2 queued" in window._canvas.diagnostic_text()


def test_renderer_host_reports_dispatcher_returned_queue_count(qtbot) -> None:
    dispatcher = _CountOverrideRenderDispatcher(queued_count=9)
    window = MainWindow(
        canvas_factory=lambda parent=None: RendererHostCanvasWidget(
            parent,
            render_dispatcher=dispatcher,
        )
    )
    qtbot.addWidget(window)
    window._canvas.set_sprite_resource_resolver(
        SpriteResourceResolver(
            items={
                2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
                3031: SpriteItemMetadata(item_id=3031, sprite_ids=(77,)),
            },
            sprites={
                55: _sprite_pixels(1),
                77: _sprite_pixels(2),
            },
        )
    )
    window._set_active_item_selection("Stone", 2148)
    assert window._apply_active_tool_at_cursor() is True
    tile_position = window._canvas.canvas_frame().tiles[0].position
    window._editor_context.session.document.map_model.set_tile(
        TileState(position=tile_position, ground_item_id=2148, item_ids=(3031,))
    )
    window._canvas._state_changed()
    window._canvas._paint_diagnostics = lambda painter: None

    window._canvas.paintGL()

    assert len(dispatcher.payloads[0]) == 2
    assert "Sprite Dispatch: 9 queued" in window._canvas.diagnostic_text()


def test_renderer_host_paintgl_skips_unresolved_sprite_resources(qtbot) -> None:
    dispatcher = _RecordingRenderDispatcher()
    window = MainWindow(
        canvas_factory=lambda parent=None: RendererHostCanvasWidget(
            parent,
            render_dispatcher=dispatcher,
        )
    )
    qtbot.addWidget(window)
    window._canvas.set_sprite_resource_resolver(
        SpriteResourceResolver(
            items={
                2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
                3031: SpriteItemMetadata(item_id=3031, sprite_ids=(77,)),
            },
            sprites={
                55: _sprite_pixels(1),
            },
        )
    )
    window._set_active_item_selection("Stone", 2148)
    assert window._apply_active_tool_at_cursor() is True
    tile_position = window._canvas.canvas_frame().tiles[0].position
    window._editor_context.session.document.map_model.set_tile(
        TileState(position=tile_position, ground_item_id=2148, item_ids=(3031,))
    )
    window._canvas._state_changed()
    window._canvas._paint_diagnostics = lambda painter: None

    window._canvas.paintGL()

    assert dispatcher.payloads == [
        [
            {
                "x": tile_position.x,
                "y": tile_position.y,
                "layer": 0,
                "sprite_id": 55,
                "pixels": _sprite_pixels(1),
            },
        ]
    ]
    assert "Sprite Dispatch: 1 queued" in window._canvas.diagnostic_text()


def test_renderer_host_paintgl_reports_dispatch_failure_without_raising(
    qtbot,
) -> None:
    window = MainWindow(
        canvas_factory=lambda parent=None: RendererHostCanvasWidget(
            parent,
            render_dispatcher=_FailingRenderDispatcher(),
        )
    )
    qtbot.addWidget(window)
    window._canvas._paint_diagnostics = lambda painter: None

    window._canvas.paintGL()

    assert "Sprite Dispatch: 0 queued" in window._canvas.diagnostic_text()
    assert (
        "Sprite Dispatch Error: RuntimeError: renderer boom"
        in window._canvas.diagnostic_text()
    )
