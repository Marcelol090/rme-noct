"""Properties Dock implementation."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.theme import THEME, TYPOGRAPHY


class PropertiesDock(GlassDockWidget):
    """The properties dock for inspecting items and tiles.

    Provides high-density form layouts using editorial JetBrains Mono
    as specified in the Noct Map Editor design.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("TILE PROPERTIES", parent)
        self.setObjectName("tile_properties_dock")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # Heading
        heading = QLabel("Tile Properties")
        heading.setFont(TYPOGRAPHY.ui_label())
        heading.setStyleSheet(f"color: {THEME.ash_lavender.name()}; font-weight: 600;")
        layout.addWidget(heading)

        # Form layout for properties
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(8)

        # We define a helper to create the tech labels
        def create_prop_value(text: str) -> QLabel:
            val_label = QLabel(text)
            val_label.setFont(TYPOGRAPHY.coordinate_display())
            val_label.setStyleSheet("color: #FFFFFF;")
            val_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            return val_label

        def create_prop_key(text: str) -> QLabel:
            key_label = QLabel(text)
            key_label.setFont(TYPOGRAPHY.ui_label())
            key_label.setStyleSheet(f"color: {THEME.ash_lavender.name()};")
            return key_label

        form_layout.addRow(create_prop_key("Position:"), create_prop_value("X:32000 Y:32000 Z:07"))
        form_layout.addRow(create_prop_key("Item ID:"), create_prop_value("2555 (grass)"))
        form_layout.addRow(create_prop_key("Action ID:"), create_prop_value("0"))
        form_layout.addRow(create_prop_key("Unique ID:"), create_prop_value("0"))
        form_layout.addRow(create_prop_key("Text:"), create_prop_value('""'))
        form_layout.addRow(create_prop_key("Sponsor:"), create_prop_value("None"))

        layout.addLayout(form_layout)
        layout.addStretch()

        self.set_inner_layout(layout)
