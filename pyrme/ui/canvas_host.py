from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from pyrme import __app_name__
from pyrme.ui.theme import TYPOGRAPHY

if TYPE_CHECKING:
    from pyrme.ui.editor_context import EditorContext


class CanvasWidgetProtocol(Protocol):
    def bind_editor_context(self, context: EditorContext) -> None: ...
    def set_position(self, x: int, y: int, z: int) -> None: ...
    def set_floor(self, z: int) -> None: ...
    def set_zoom(self, percent: int) -> None: ...
    def set_show_grid(self, enabled: bool) -> None: ...
    def set_ghost_higher(self, enabled: bool) -> None: ...
    def set_show_lower(self, enabled: bool) -> None: ...
    def fit_to_map(self) -> tuple[int, int, int] | None: ...
    def refresh_map_view(self) -> None: ...


class PlaceholderCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor_context: EditorContext | None = None
        self.position = (32000, 32000, 7)
        self.floor = 7
        self.zoom_percent = 100
        self.show_grid = False
        self.ghost_higher = False
        self.show_lower = True
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(TYPOGRAPHY.ui_label(size=13))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        self._refresh_label()

    def bind_editor_context(self, context: EditorContext) -> None:
        self.editor_context = context
        self._refresh_label()

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)
        self.floor = z
        self._refresh_label()

    def set_floor(self, z: int) -> None:
        self.floor = z
        self._refresh_label()

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent
        self._refresh_label()

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled
        self._refresh_label()

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled
        self._refresh_label()

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled
        self._refresh_label()

    def fit_to_map(self) -> tuple[int, int, int]:
        return self.position

    def refresh_map_view(self) -> None:
        self.update()

    def _refresh_label(self) -> None:
        x, y, z = self.position
        title = (
            self.editor_context.session.document.name
            if self.editor_context is not None
            else "Untitled"
        )
        self._label.setText(
            f"🗺️ {__app_name__} Canvas\n\n"
            "Rust-backed wgpu renderer will be integrated in Milestone 4.\n"
            "This placeholder keeps shell state flowing through a stable widget seam.\n\n"
            f"Document: {title}\n"
            f"Position: {x}, {y}, {z:02d}\n"
            f"Zoom: {self.zoom_percent}%\n"
            f"Grid: {'On' if self.show_grid else 'Off'}\n"
            f"Ghost Higher Floors: {'On' if self.ghost_higher else 'Off'}\n"
            f"Show Lower Floors: {'On' if self.show_lower else 'Off'}"
        )
