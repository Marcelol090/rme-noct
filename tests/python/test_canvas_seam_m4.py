from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from pyrme.ui.canvas_host import PlaceholderCanvasWidget
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path


def _build_settings(tmp_path: Path, name: str) -> QSettings:
    return QSettings(str(tmp_path / name), QSettings.Format.IniFormat)


class _FakeCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
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


def test_main_window_uses_injected_canvas_factory_and_forwards_shell_state(
    qtbot, tmp_path: Path
) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        holder["canvas"] = canvas
        return canvas

    window = MainWindow(
        settings=_build_settings(tmp_path, "canvas.ini"),
        canvas_factory=_canvas_factory,
    )
    qtbot.addWidget(window)

    canvas = holder["canvas"]
    assert window.centralWidget() is canvas
    assert canvas.position == (32000, 32000, 7)
    assert canvas.floor == 7
    assert canvas.zoom_percent == 100

    placeholder = PlaceholderCanvasWidget()
    qtbot.addWidget(placeholder)
    assert placeholder.position == (32000, 32000, 7)
