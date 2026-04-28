from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.editor import MapPosition
from pyrme.ui.canvas_host import EditorToolApplyResult
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from pyrme.ui.editor_context import EditorContext


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


class _ViewportCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor_context: EditorContext | None = None
        self.position: tuple[int, int, int] | None = None
        self.floor: int | None = None
        self.zoom_percent: int | None = None
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.show_lower: bool | None = None
        self.apply_target: MapPosition | None = None

    def bind_editor_context(self, context: EditorContext) -> None:
        self.editor_context = context

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)

    def set_floor(self, z: int) -> None:
        self.floor = z

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled

    def apply_active_tool(self) -> EditorToolApplyResult:
        assert self.editor_context is not None
        assert self.apply_target is not None
        return EditorToolApplyResult(
            changed=self.editor_context.session.editor.apply_active_tool_at(
                self.apply_target
            ),
            position=self.apply_target,
        )


def test_editor_views_own_independent_viewport_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_ViewportCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _ViewportCanvasWidget:
        canvas = _ViewportCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "viewport-independent.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32100, 32110, 6, track_history=True)
    window.editor_zoom_in_action.trigger()
    window.editor_new_view_action.trigger()

    first_view = window._views[0]
    second_view = window._views[1]
    assert second_view.viewport.snapshot() == first_view.viewport.snapshot()

    window._set_current_position(32200, 32210, 8, track_history=True)
    window.editor_zoom_out_action.trigger()

    assert second_view.viewport.center == (32200, 32210, 8)
    assert second_view.viewport.previous_position == (32100, 32110, 6)
    assert second_view.viewport.zoom_percent == 100

    window._view_tabs.setCurrentIndex(0)

    assert first_view.viewport.center == (32100, 32110, 6)
    assert first_view.viewport.previous_position == (32000, 32000, 7)
    assert first_view.viewport.zoom_percent == 110
    assert (window._current_x, window._current_y, window._current_z) == (
        32100,
        32110,
        6,
    )
    assert window._previous_position == (32000, 32000, 7)
    assert window._zoom_percent == 110
    assert canvases[0].position == (32100, 32110, 6)
    assert canvases[0].zoom_percent == 110

    window._view_tabs.setCurrentIndex(1)

    assert (window._current_x, window._current_y, window._current_z) == (
        32200,
        32210,
        8,
    )
    assert window._previous_position == (32100, 32110, 6)
    assert window._zoom_percent == 100
    assert canvases[1].position == (32200, 32210, 8)
    assert canvases[1].zoom_percent == 100


def test_tool_application_updates_only_active_viewport(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_ViewportCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _ViewportCanvasWidget:
        canvas = _ViewportCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "viewport-tool-apply.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32100, 32110, 6, track_history=True)
    window.editor_new_view_action.trigger()
    first_view = window._views[0]
    second_view = window._views[1]
    canvases[1].apply_target = MapPosition(33000, 33010, 4)
    window._set_active_item_selection("Stone", 1)

    assert window._apply_active_tool_at_cursor() is True

    assert first_view.viewport.center == (32100, 32110, 6)
    assert second_view.viewport.center == (33000, 33010, 4)
    assert second_view.viewport.previous_position == (32000, 32000, 7)
    assert (window._current_x, window._current_y, window._current_z) == (
        33000,
        33010,
        4,
    )
