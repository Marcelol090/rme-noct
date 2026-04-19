"""Minimap Dock implementation."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.theme import THEME, TYPOGRAPHY


class MinimapDock(GlassDockWidget):
    """The minimap dock for map navigation.

    Provides map overview and Z-level controls, styled
    in the Noct Map Editor aesthetic.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("MINIMAP", parent)
        self.setObjectName("minimap_dock")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Minimap view placeholder
        self.map_view = QLabel()
        self.map_view.setMinimumSize(200, 200)
        self.map_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_view.setText("Minimap Render")
        self.map_view.setStyleSheet(f"""
            background-color: #000000;
            border: 1px solid {THEME.ghost_border.name()};
            border-radius: 4px;
            color: {THEME.ash_lavender.name()};
        """)
        layout.addWidget(self.map_view)

        # Controls layout
        controls_layout = QHBoxLayout()

        # Z controls
        self.z_up_btn = self._create_control_btn("▲ +")
        self.z_down_btn = self._create_control_btn("▼ -")

        # Position label
        self.pos_label = QLabel("Z: 07")
        self.pos_label.setFont(TYPOGRAPHY.coordinate_display())
        self.pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pos_label.setStyleSheet("color: #FFFFFF;")
        controls_layout.addWidget(self.z_up_btn)
        controls_layout.addWidget(self.pos_label)
        controls_layout.addWidget(self.z_down_btn)

        layout.addLayout(controls_layout)

        self.set_inner_layout(layout)

    def _create_control_btn(self, text: str) -> QPushButton:
        """Helper to create small control buttons."""
        btn = QPushButton(text)
        btn.setFixedSize(32, 24)
        btn.setFont(TYPOGRAPHY.ui_label())
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.ash_lavender.name()};
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                border: 1px solid {THEME.active_border.name()};
            }}
            QPushButton:pressed {{
                background-color: {THEME.amethyst_core.name()};
            }}
        """)
        return btn
