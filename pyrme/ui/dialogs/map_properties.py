"""Map Properties Dialog.

Ported from legacy C++ MapPropertiesWindow (ui/map/map_properties_window.cpp).
Follows the Noct Map Editor Design System (DESIGN.md) for dialog styling.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.theme import THEME, TYPOGRAPHY


class MapPropertiesDialog(QDialog):
    """Dialog for editing map meta-properties.

    Mirrors legacy C++ MapPropertiesWindow with:
    - Description, OTBM Version, Client Version
    - Map Width/Height
    - External House/Spawn/Waypoint file paths
    """

    # DESIGN.md: Map Properties dialog = 520 × 420
    DIALOG_SIZE = QSize(520, 420)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Map Properties")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._apply_dialog_style()
        self._build_layout()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Elevation 3 dialog styling."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME.void_black.name()};
                color: {THEME.moonstone_white.name()};
            }}
            QLabel {{
                color: {THEME.moonstone_white.name()};
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }}
            QLineEdit, QSpinBox, QComboBox, QTextEdit {{
                background-color: {THEME.obsidian_glass.name()};
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                padding: 4px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
                border: 1px solid {THEME.focus_border.name()};
            }}
        """)

    def _build_layout(self) -> None:
        """Construct the dialog layout matching legacy C++ MapPropertiesWindow."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Dialog heading (DESIGN.md: Inter 14px weight 600 Moonstone White)
        heading = QLabel("Map Properties")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        heading.setStyleSheet(f"color: {THEME.moonstone_white.name()}; font-weight: 600;")
        layout.addWidget(heading)

        # Form layout
        form = QFormLayout()
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        form.setSpacing(12)

        # Description (legacy: wxTextCtrl, multiline)
        self.desc_edit = QTextEdit()
        self.desc_edit.setMinimumHeight(60)
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setToolTip("Enter a description for the map")
        form.addRow("Description:", self.desc_edit)

        # OTBM Version (legacy: wxChoice with OTServ labels)
        self.otbm_combo = QComboBox()
        self.otbm_combo.addItems([
            "OTServ 0.5.0",
            "OTServ 0.6.0",
            "OTServ 0.6.1",
            "OTServ 0.7.0 (revscriptsys)",
        ])
        self.otbm_combo.setCurrentIndex(2)  # Default: OTBM 3
        self.otbm_combo.setToolTip(
            "Select the OTBM version (Determines feature support)"
        )
        form.addRow("Map Version:", self.otbm_combo)

        # Client Version (legacy: wxChoice, populated dynamically)
        self.client_combo = QComboBox()
        self.client_combo.addItems(["10.98", "8.60", "7.60"])
        self.client_combo.setToolTip("Select the target client version")
        form.addRow("Client Version:", self.client_combo)

        # Map Dimensions – side by side like legacy C++
        dim_widget = QWidget()
        dim_layout = QHBoxLayout(dim_widget)
        dim_layout.setContentsMargins(0, 0, 0, 0)
        dim_layout.setSpacing(8)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(256, 65000)
        self.width_spin.setSingleStep(256)
        self.width_spin.setToolTip("Map width in tiles")

        self.height_spin = QSpinBox()
        self.height_spin.setRange(256, 65000)
        self.height_spin.setSingleStep(256)
        self.height_spin.setToolTip("Map height in tiles")

        dim_layout.addWidget(QLabel("W:"))
        dim_layout.addWidget(self.width_spin, 1)
        dim_layout.addWidget(QLabel("H:"))
        dim_layout.addWidget(self.height_spin, 1)

        form.addRow("Dimensions:", dim_widget)

        # External files (legacy: wxTextCtrl for each)
        self.house_edit = QLineEdit()
        self.house_edit.setToolTip(
            "External house XML file (leave empty for internal)"
        )
        form.addRow("House File:", self.house_edit)

        self.spawn_edit = QLineEdit()
        self.spawn_edit.setToolTip(
            "External spawn XML file (leave empty for internal)"
        )
        form.addRow("Spawn File:", self.spawn_edit)

        self.waypoint_edit = QLineEdit()
        self.waypoint_edit.setToolTip(
            "External waypoint XML file (leave empty for internal)"
        )
        form.addRow("Waypoint File:", self.waypoint_edit)

        layout.addLayout(form)
        layout.addStretch()

        # Footer buttons (DESIGN.md: Ghost Cancel + Amethyst Primary OK)
        footer = QHBoxLayout()
        footer.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("Discard changes")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: none;
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 6px;
                color: {THEME.ash_lavender.name()};
                padding: 6px 16px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {THEME.lifted_glass.name()};
                border: 1px solid {THEME.active_border.name()};
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        footer.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("Save")
        self.ok_btn.setToolTip("Confirm changes")
        self.ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME.amethyst_core.name()};
                border: none;
                border-radius: 6px;
                color: {THEME.moonstone_white.name()};
                padding: 6px 16px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {THEME.deep_amethyst.name()};
            }}
        """)
        self.ok_btn.clicked.connect(self.accept)
        footer.addWidget(self.ok_btn)

        layout.addLayout(footer)
