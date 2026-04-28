from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.editor import MapPosition, TileState
from pyrme.ui.canvas_host import EditorToolApplyResult
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
        self.view_flags: dict[str, bool] = {}
        self.show_flags: dict[str, bool] = {}
        self.editor_mode: str | None = None
        self.active_brush_name: str | None = None
        self.active_brush_id: str | None = None
        self.active_item_id: int | None = None
        self.apply_count = 0

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

    def set_view_flag(self, name: str, enabled: bool) -> None:
        self.view_flags[name] = enabled

    def set_show_flag(self, name: str, enabled: bool) -> None:
        self.show_flags[name] = enabled

    def set_editor_mode(self, mode: str) -> None:
        self.editor_mode = mode

    def set_active_brush(
        self,
        brush_name: str,
        brush_id: str | None,
        item_id: int | None,
    ) -> None:
        self.active_brush_name = brush_name
        self.active_brush_id = brush_id
        self.active_item_id = item_id

    def apply_active_tool(self) -> EditorToolApplyResult:
        self.apply_count += 1
        assert self.editor_context is not None
        assert self.position is not None
        position = MapPosition(*self.position)
        return EditorToolApplyResult(
            changed=self.editor_context.session.editor.apply_active_tool_at(position),
            position=position,
        )


def test_new_view_shares_editor_context_and_copies_shell_state(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32123, 32145, 5, track_history=True)
    assert window.editor_zoom_in_action is not None
    window.editor_zoom_in_action.trigger()
    window.show_grid_action.setChecked(True)
    window.ghost_higher_action.setChecked(True)
    window.show_lower_action.setChecked(False)
    window.view_menu_actions["view_show_as_minimap"].setChecked(True)
    window._editor_context.session.mode = "selection"

    assert window.editor_new_view_action is not None
    window.editor_new_view_action.trigger()

    assert window._view_tabs.count() == 2
    assert window._view_tabs.currentIndex() == 1
    assert len(window._views) == 2

    first_view = window._views[0]
    second_view = window._views[1]
    assert second_view.editor_context is first_view.editor_context
    assert second_view.editor_context.session is first_view.editor_context.session
    assert (
        second_view.editor_context.session.document.map_model
        is first_view.editor_context.session.document.map_model
    )
    assert second_view.editor_context.session.mode == "selection"
    assert canvases[0].editor_context is first_view.editor_context
    assert canvases[1].editor_context is first_view.editor_context

    assert not hasattr(second_view.shell_state, "current_x")
    assert second_view.viewport.snapshot().previous_position == (32000, 32000, 7)
    assert second_view.shell_state.show_grid_enabled is True
    assert second_view.shell_state.ghost_higher_enabled is True
    assert second_view.shell_state.show_lower_enabled is False
    assert second_view.shell_state.view_flags["view_show_as_minimap"] is True
    assert second_view.viewport.center_x == 32123
    assert second_view.viewport.center_y == 32145
    assert second_view.viewport.floor == 5
    assert second_view.viewport is not first_view.viewport
    assert second_view.viewport.snapshot().zoom_percent == 110
    assert second_view.minimap_viewport.center_x == 32123
    assert second_view.minimap_viewport.center_y == 32145
    assert second_view.minimap_viewport.floor == 5
    assert second_view.minimap_viewport.zoom_percent == 110

    assert window._view_tabs.currentWidget() is canvases[1]
    assert canvases[1].position == (32123, 32145, 5)
    assert canvases[1].floor == 5
    assert canvases[1].zoom_percent == 110
    assert canvases[1].show_grid is True
    assert canvases[1].ghost_higher is True
    assert canvases[1].show_lower is False
    assert canvases[1].view_flags["show_as_minimap"] is True


def test_new_view_viewports_evolve_independently(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view-viewport.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32123, 32145, 5, track_history=True)
    assert window.editor_new_view_action is not None
    window.editor_new_view_action.trigger()

    first_view = window._views[0]
    second_view = window._views[1]
    assert first_view.viewport is not second_view.viewport

    window._set_current_position(33000, 33100, 9, track_history=True)
    assert window.editor_zoom_in_action is not None
    window.editor_zoom_in_action.trigger()

    assert second_view.viewport.center == (33000, 33100, 9)
    assert second_view.viewport.zoom_percent == 110
    assert first_view.viewport.center == (32123, 32145, 5)
    assert first_view.viewport.zoom_percent == 100

    window._view_tabs.setCurrentIndex(0)

    assert window._current_x == 32123
    assert window._current_y == 32145
    assert window._current_z == 5
    assert window._zoom_percent == 100
    assert canvases[0].position == (32123, 32145, 5)
    assert canvases[0].zoom_percent == 100


def test_view_flags_evolve_independently_after_new_view(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view-flags.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.view_menu_actions["view_show_as_minimap"].setChecked(True)
    assert canvases[0].view_flags["show_as_minimap"] is True

    assert window.editor_new_view_action is not None
    window.editor_new_view_action.trigger()

    assert window._view_tabs.currentIndex() == 1
    assert canvases[1].view_flags["show_as_minimap"] is True

    window.view_menu_actions["view_show_as_minimap"].setChecked(False)
    assert canvases[1].view_flags["show_as_minimap"] is False

    window._view_tabs.setCurrentIndex(0)

    assert window.view_menu_actions["view_show_as_minimap"].isChecked() is True
    assert canvases[0].view_flags["show_as_minimap"] is True


def test_new_view_carries_editor_activation_state_to_new_canvas(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view-activation.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.brush_mode_actions["selection"].trigger()
    window._set_active_item_selection("Stone", 1)

    assert window.editor_new_view_action is not None
    window.editor_new_view_action.trigger()

    assert len(canvases) == 2
    assert canvases[0].editor_mode == "selection"
    assert canvases[0].active_brush_name == "Stone"
    assert canvases[0].active_brush_id == "item:1"
    assert canvases[0].active_item_id == 1
    assert canvases[1].editor_mode == "selection"
    assert canvases[1].active_brush_name == "Stone"
    assert canvases[1].active_brush_id == "item:1"
    assert canvases[1].active_item_id == 1


def test_new_view_apply_uses_active_canvas_seam(
    qtbot,
    settings_workspace: Path,
) -> None:
    canvases: list[_FakeCanvasWidget] = []

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        canvases.append(canvas)
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "new-view-apply.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_current_position(32123, 32145, 5, track_history=True)
    window._set_active_item_selection("Stone", 1)
    assert window.editor_new_view_action is not None
    window.editor_new_view_action.trigger()

    changed = window._apply_active_tool_at_cursor()

    assert changed is True
    assert len(canvases) == 2
    assert canvases[0].apply_count == 0
    assert canvases[1].apply_count == 1
    assert window._view_tabs.currentWidget() is canvases[1]
    assert window._editor_context.session.document.is_dirty is True
    assert window._editor_context.session.editor.map_model.get_tile(
        MapPosition(32123, 32145, 5)
    ) == TileState(position=MapPosition(32123, 32145, 5), ground_item_id=1)
    assert window._view_tabs.tabText(0) == "Untitled*"
    assert window._view_tabs.tabText(1) == "Untitled*"
    assert window.statusBar().currentMessage() == "Applied Draw tool at 32123, 32145, 05."
