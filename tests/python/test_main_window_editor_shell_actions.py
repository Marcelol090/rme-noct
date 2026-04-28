from __future__ import annotations

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.ui.main_window import MainWindow


def _build_settings(root, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


class _FakeCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.position: tuple[int, int, int] | None = None
        self.floor: int | None = None
        self.zoom_percent: int | None = None
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.show_lower: bool | None = None
        self.view_flags: dict[str, bool] = {}
        self.show_flags: dict[str, bool] = {}
        self.editor_context = None

    def bind_editor_context(self, context) -> None:
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


def test_main_window_editor_actions_drive_editor_shell_state(
    qtbot,
    settings_workspace,
) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        holder["canvas"] = canvas
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "editor-shell.ini"),
        canvas_factory=_canvas_factory,
    )
    qtbot.addWidget(window)

    canvas = holder["canvas"]
    assert canvas.zoom_percent == 100
    assert window.editor_zoom_in_action is not None
    assert window.editor_zoom_out_action is not None
    assert window.editor_zoom_normal_action is not None
    assert window.editor_screenshot_action is not None
    assert window.editor_new_view_action is not None

    window.editor_zoom_in_action.trigger()
    assert window._zoom_percent == 110
    assert canvas.zoom_percent == 110

    window.editor_zoom_out_action.trigger()
    assert window._zoom_percent == 100
    assert canvas.zoom_percent == 100

    window.editor_zoom_normal_action.trigger()
    assert window._zoom_percent == 100
    assert canvas.zoom_percent == 100

    window.editor_screenshot_action.trigger()
    assert "not available" in window.statusBar().currentMessage().lower()

    window.editor_new_view_action.trigger()
    assert window._view_tabs.count() == 2
    assert "opened a new view" in window.statusBar().currentMessage().lower()
