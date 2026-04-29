from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtGui import QColor, QFont, QPen

from pyrme.editor import MapPosition
from pyrme.rendering import DiagnosticTilePrimitive
from pyrme.ui.canvas_host import RendererHostCanvasWidget
from pyrme.ui.editor_context import EditorContext

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class _DrawTextCall:
    text: str
    pen_color: QColor


class _RecordingPainter:
    def __init__(self) -> None:
        self.draw_text_calls: list[_DrawTextCall] = []
        self.fonts: list[QFont] = []
        self.brush_colors: list[QColor] = []
        self.drawn_rects: list[object] = []
        self._pen_color = QColor()
        self.ended = False

    def fillRect(self, *args) -> None:  # noqa: N802
        pass

    def setRenderHint(self, *args) -> None:  # noqa: N802
        pass

    def setPen(self, pen: QColor | QPen) -> None:  # noqa: N802
        self._pen_color = pen.color() if isinstance(pen, QPen) else QColor(pen)

    def setBrush(self, brush: QColor) -> None:  # noqa: N802
        self.brush_colors.append(QColor(brush))

    def save(self) -> None:
        pass

    def restore(self) -> None:
        pass

    def drawRect(self, rect) -> None:  # noqa: N802
        self.drawn_rects.append(rect)

    def drawRoundedRect(self, *args) -> None:  # noqa: N802
        pass

    def setFont(self, font: QFont) -> None:  # noqa: N802
        self.fonts.append(QFont(font))

    def drawText(self, rect, flags, text: str) -> None:  # noqa: N802
        self.draw_text_calls.append(_DrawTextCall(text, QColor(self._pen_color)))

    def end(self) -> None:
        self.ended = True


def test_renderer_host_diagnostic_text_reports_fps_and_coordinates(qtbot) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)

    canvas.set_position(32010, 32020, 5)

    text = canvas.diagnostic_text()
    assert "FPS:" in text
    assert "Position: 32010, 32020, 05" in text
    assert "OpenGL Context:" in text


def test_renderer_host_overlay_uses_diagnostic_text_style(qtbot) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)
    canvas.set_position(32010, 32020, 5)
    painter = _RecordingPainter()

    canvas._paint_diagnostics(painter)

    assert painter.ended is True
    assert painter.fonts
    assert painter.fonts[-1].family() == "JetBrains Mono"
    assert painter.fonts[-1].pointSize() == 10
    assert QColor("#E8E6F0") in [call.pen_color for call in painter.draw_text_calls]
    assert QColor(0, 0, 0, 204) in [call.pen_color for call in painter.draw_text_calls]
    assert any("FPS:" in call.text for call in painter.draw_text_calls)
    assert any("Position: 32010, 32020, 05" in call.text for call in painter.draw_text_calls)


def test_t05_does_not_ship_mapcanvas_placeholder_artifacts() -> None:
    assert not (ROOT / "pyrme/ui/canvas.py").exists()
    assert not (ROOT / "tests/python/test_canvas_rendering.py").exists()


def test_renderer_host_grid_overlay_uses_amethyst_grid_token(qtbot) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)
    canvas._frame_primitives = (
        DiagnosticTilePrimitive(
            position=MapPosition(32000, 32000, 7),
            screen_rect=(0, 0, 32, 32),
            label="2148",
        ),
    )
    painter = _RecordingPainter()

    canvas._paint_tile_primitives(painter)

    assert painter.drawn_rects
    assert QColor(124, 92, 252, 38) in painter.brush_colors


def test_renderer_host_selected_tile_overlay_uses_selection_token(qtbot) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)
    context = EditorContext()
    position = MapPosition(32000, 32000, 7)
    context.session.editor.selection_positions.add(position)
    canvas.bind_editor_context(context)
    canvas._frame_primitives = (
        DiagnosticTilePrimitive(
            position=position,
            screen_rect=(0, 0, 32, 32),
            label="2148",
        ),
    )
    painter = _RecordingPainter()

    canvas._paint_tile_primitives(painter)

    assert painter.drawn_rects
    assert QColor(255, 255, 255, 51) in painter.brush_colors


def test_renderer_host_invalid_tile_overlay_uses_invalid_token(qtbot) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)
    position = MapPosition(32000, 32000, 7)
    canvas.set_invalid_tile_positions((position,))
    canvas._frame_primitives = (
        DiagnosticTilePrimitive(
            position=position,
            screen_rect=(0, 0, 32, 32),
            label="2148",
        ),
    )
    painter = _RecordingPainter()

    canvas._paint_tile_primitives(painter)

    assert painter.drawn_rects
    assert QColor(224, 92, 92, 102) in painter.brush_colors


def test_renderer_host_invalid_tile_overlay_respects_show_invalid_tiles_flag(
    qtbot,
) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)
    position = MapPosition(32000, 32000, 7)
    canvas.set_show_flag("show_invalid_tiles", False)
    canvas.set_invalid_tile_positions((position,))
    canvas._frame_primitives = (
        DiagnosticTilePrimitive(
            position=position,
            screen_rect=(0, 0, 32, 32),
            label="2148",
        ),
    )
    painter = _RecordingPainter()

    canvas._paint_tile_primitives(painter)

    assert QColor(224, 92, 92, 102) not in painter.brush_colors
    assert QColor(124, 92, 252, 38) in painter.brush_colors


def test_renderer_host_selected_tile_wins_when_invalid_overlay_is_hidden(
    qtbot,
) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)
    context = EditorContext()
    position = MapPosition(32000, 32000, 7)
    context.session.editor.selection_positions.add(position)
    canvas.bind_editor_context(context)
    canvas.set_show_flag("show_invalid_tiles", False)
    canvas.set_invalid_tile_positions((position,))
    canvas._frame_primitives = (
        DiagnosticTilePrimitive(
            position=position,
            screen_rect=(0, 0, 32, 32),
            label="2148",
        ),
    )
    painter = _RecordingPainter()

    canvas._paint_tile_primitives(painter)

    assert painter.drawn_rects
    assert QColor(224, 92, 92, 102) not in painter.brush_colors
    assert painter.brush_colors == [QColor(255, 255, 255, 51)]
