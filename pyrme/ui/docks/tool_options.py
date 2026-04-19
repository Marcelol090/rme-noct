"""Tool Options dock implementation."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.theme import TYPOGRAPHY


class ToolOptionsDock(GlassDockWidget):
    """Dock that mirrors the legacy Tool Options window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("TOOL OPTIONS", parent)
        self.setObjectName("tool_options_dock")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        heading = QLabel("Tool Options")
        heading.setFont(TYPOGRAPHY.ui_label())
        layout.addWidget(heading)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._brush_label = QLabel("Select")
        self._brush_label.setFont(TYPOGRAPHY.coordinate_display())
        self._brush_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self._mode_label = QLabel("Draw")
        self._mode_label.setFont(TYPOGRAPHY.coordinate_display())
        self._mode_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self._position_label = QLabel("X: 32000 Y: 32000 Z: 07")
        self._position_label.setFont(TYPOGRAPHY.coordinate_display())
        self._position_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self._zoom_label = QLabel("100%")
        self._zoom_label.setFont(TYPOGRAPHY.coordinate_display())

        form.addRow("Mode:", self._mode_label)
        form.addRow("Brush:", self._brush_label)
        form.addRow("Position:", self._position_label)
        form.addRow("Zoom:", self._zoom_label)

        layout.addLayout(form)
        layout.addStretch()
        self.set_inner_layout(layout)

    def set_shell_state(
        self,
        *,
        mode_name: str,
        brush_name: str,
        position: tuple[int, int, int],
        zoom_percent: int,
    ) -> None:
        """Mirror the current shell state in the dock."""
        x, y, z = position
        self._mode_label.setText(mode_name)
        self._brush_label.setText(brush_name)
        self._position_label.setText(f"X: {x} Y: {y} Z: {z:02d}")
        self._zoom_label.setText(f"{zoom_percent}%")
