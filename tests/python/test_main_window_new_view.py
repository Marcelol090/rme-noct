from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    from pyrme.ui.editor_context import EditorContext


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


class _FakeCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor_context: EditorContext | None = None
        self.position: tuple[int, int, int] | None = None
        self.floor: int | None = None
        self.zoom_percent: int | None = None
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.show_lower: bool | None = None

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

    def bind_editor_context(self, context: EditorContext) -> None:
        self.editor_context = context


def test_new_view_adds_a_shared_editor_view_tab_with_copied_shell_state(
    qtbot,
    tmp_path: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(tmp_path, "parent.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32123, 32145, 5, track_history=True)
    window.zoom_in_action.trigger()
    window.show_grid_action.setChecked(True)
    window.ghost_higher_action.setChecked(True)
    window.show_lower_action.setChecked(False)
    window._editor_context.session.mode = "selection"

    window.new_view_action.trigger()

    assert window._view_tabs.count() == 2
    assert window._view_tabs.currentIndex() == 1
    assert len(window._views) == 2
    assert window._view_tabs.tabText(0) == "Untitled"
    assert window._view_tabs.tabText(1) == "Untitled"

    first_view = window._views[0]
    second_view = window._views[1]
    assert second_view.editor_context is first_view.editor_context
    assert second_view.editor_context.session is first_view.editor_context.session
    assert second_view.editor_context.session.document is first_view.editor_context.session.document
    assert second_view.editor_context.session.mode == "selection"
    assert canvases[0].editor_context is first_view.editor_context
    assert canvases[1].editor_context is first_view.editor_context
    assert second_view.shell_state.current_x == 32123
    assert second_view.shell_state.current_y == 32145
    assert second_view.shell_state.current_z == 5
    assert second_view.shell_state.previous_position == (32000, 32000, 7)
    assert second_view.shell_state.zoom_percent == 110
    assert second_view.shell_state.show_grid_enabled is True
    assert second_view.shell_state.ghost_higher_enabled is True
    assert second_view.shell_state.show_lower_enabled is False
    assert second_view.viewport.center_x == 32123
    assert second_view.viewport.center_y == 32145
    assert second_view.viewport.floor == 5
    assert second_view.minimap_viewport.center_x == 32123
    assert second_view.minimap_viewport.center_y == 32145
    assert second_view.minimap_viewport.zoom_percent == 110

    second_canvas = canvases[-1]
    assert window._view_tabs.currentWidget() is second_canvas
    assert second_canvas.position == (32123, 32145, 5)
    assert second_canvas.floor == 5
    assert second_canvas.zoom_percent == 110
    assert second_canvas.show_grid is True
    assert second_canvas.ghost_higher is True
    assert second_canvas.show_lower is False

    window._editor_context.session.document.name = "Kazordoon"
    window._editor_context.session.document.is_dirty = True
    window._refresh_view_titles()
    assert window._view_tabs.tabText(0) == "Kazordoon*"
    assert window._view_tabs.tabText(1) == "Kazordoon*"


def test_new_view_keeps_shell_state_independent_between_tabs(
    qtbot,
    tmp_path: Path,
) -> None:
    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        return _FakeCanvasWidget(parent)

    window = MainWindow(
        settings=_build_settings(tmp_path, "parent.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32050, 32060, 6, track_history=True)
    window.zoom_in_action.trigger()
    window.show_grid_action.setChecked(True)
    window.new_view_action.trigger()

    window.zoom_in_action.trigger()
    window._set_current_position(33000, 33010, 4, track_history=True)
    window.show_grid_action.setChecked(False)

    second_view = window._views[1]
    assert second_view.shell_state.zoom_percent == 120
    assert (
        second_view.shell_state.current_x,
        second_view.shell_state.current_y,
        second_view.shell_state.current_z,
    ) == (33000, 33010, 4)
    assert second_view.shell_state.show_grid_enabled is False
    assert second_view.viewport.center_x == 33000
    assert second_view.viewport.center_y == 33010
    assert second_view.viewport.floor == 4
    assert second_view.minimap_viewport.center_x == 33000
    assert second_view.minimap_viewport.center_y == 33010
    assert second_view.minimap_viewport.zoom_percent == 120

    window._view_tabs.setCurrentIndex(0)
    assert window._zoom_percent == 110
    assert (window._current_x, window._current_y, window._current_z) == (32050, 32060, 6)
    assert window._show_grid_enabled is True

    window.zoom_normal_action.trigger()
    window._set_current_position(32010, 32020, 7, track_history=True)
    first_view = window._views[0]
    assert first_view.shell_state.zoom_percent == 100
    assert (
        first_view.shell_state.current_x,
        first_view.shell_state.current_y,
        first_view.shell_state.current_z,
    ) == (32010, 32020, 7)
    assert first_view.viewport.center_x == 32010
    assert first_view.viewport.center_y == 32020
    assert first_view.viewport.floor == 7
    assert first_view.minimap_viewport.center_x == 32010
    assert first_view.minimap_viewport.center_y == 32020
    assert first_view.minimap_viewport.zoom_percent == 100

    window._view_tabs.setCurrentIndex(1)
    assert window._zoom_percent == 120
    assert (window._current_x, window._current_y, window._current_z) == (33000, 33010, 4)
    assert window._show_grid_enabled is False


def test_new_view_switch_keeps_toolbar_and_minimap_in_sync(
    qtbot,
    tmp_path: Path,
) -> None:
    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        return _FakeCanvasWidget(parent)

    window = MainWindow(
        settings=_build_settings(tmp_path, "docks.ini"),
        canvas_factory=_canvas_factory,
    )
    qtbot.addWidget(window)

    assert window.minimap_dock is not None
    assert window.floor_ghost_higher_action.isChecked() is False
    assert window.minimap_dock.pos_label.text() == "Z: 07"

    window._set_current_position(32010, 32020, 6, track_history=True)
    window.ghost_higher_action.setChecked(True)
    window.new_view_action.trigger()

    window._set_current_position(33000, 33010, 4, track_history=True)
    window.floor_ghost_higher_action.setChecked(False)

    assert window.minimap_dock.pos_label.text() == "Z: 04"
    assert window.floor_ghost_higher_action.isChecked() is False
    assert window.ghost_higher_action.isChecked() is False

    window._view_tabs.setCurrentIndex(0)
    assert window.minimap_dock.pos_label.text() == "Z: 06"
    assert window.floor_ghost_higher_action.isChecked() is True
    assert window.ghost_higher_action.isChecked() is True
