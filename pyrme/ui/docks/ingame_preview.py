"""In-game Preview dock implementation."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.theme import TYPOGRAPHY


class IngamePreviewDock(GlassDockWidget):
    """Dock mirroring the legacy in-game preview window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("IN-GAME PREVIEW", parent)
        self.setObjectName("ingame_preview_dock")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        self._preview_label = QLabel("In-game preview is not wired in this slice.")
        self._preview_label.setWordWrap(True)
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFont(TYPOGRAPHY.ui_label())

        layout.addWidget(self._preview_label)
        layout.addStretch()
        self.set_inner_layout(layout)

    def set_preview_state(self, text: str) -> None:
        """Update the preview placeholder text."""
        self._preview_label.setText(text)
