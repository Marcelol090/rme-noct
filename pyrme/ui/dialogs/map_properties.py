"""Map Properties Dialog.

Ported from legacy C++ MapPropertiesWindow (ui/map/map_properties_window.cpp).
Follows the Noct Map Editor Design System (DESIGN.md) for dialog styling.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

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

from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY

DEFAULT_MAP_VERSION = "OTServ 0.6.1"
DEFAULT_CLIENT_VERSION = "10.98"
DEFAULT_MAP_WIDTH = 256
DEFAULT_MAP_HEIGHT = 256


@dataclass(slots=True)
class MapPropertiesState:
    """Local state object for the Map Properties dialog."""

    description: str = ""
    map_version: str = DEFAULT_MAP_VERSION
    client_version: str = DEFAULT_CLIENT_VERSION
    width: int = DEFAULT_MAP_WIDTH
    height: int = DEFAULT_MAP_HEIGHT
    house_file: str = ""
    spawn_file: str = ""
    waypoint_file: str = ""


class MapPropertiesDialog(QDialog):
    """Dialog for editing map meta-properties."""

    # DESIGN.md: Map Properties dialog = 520 × 420
    DIALOG_SIZE = QSize(520, 420)

    def __init__(
        self,
        parent: QWidget | None = None,
        state: MapPropertiesState | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Map Properties")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._state = replace(state) if state is not None else MapPropertiesState()
        self._apply_dialog_style()
        self._build_layout()
        self.set_state(self._state)

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Elevation 3 dialog styling."""
        self.setStyleSheet(
            dialog_base_qss("QLineEdit, QSpinBox, QComboBox, QTextEdit")
        )

    def _build_layout(self) -> None:
        """Construct the dialog layout matching legacy C++ MapPropertiesWindow."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        heading = QLabel("Map Properties")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        form = QFormLayout()
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        form.setSpacing(12)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMinimumHeight(60)
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setToolTip("Enter a description for the map")
        form.addRow("Description:", self.desc_edit)

        self.otbm_combo = QComboBox()
        self.otbm_combo.addItems([
            "OTServ 0.5.0",
            "OTServ 0.6.0",
            "OTServ 0.6.1",
            "OTServ 0.7.0 (revscriptsys)",
        ])
        self.otbm_combo.setToolTip(
            "Select the OTBM version (Determines feature support)"
        )
        form.addRow("Map Version:", self.otbm_combo)

        self.client_combo = QComboBox()
        self.client_combo.addItems(["10.98", "8.60", "7.60"])
        self.client_combo.setToolTip("Select the target client version")
        form.addRow("Client Version:", self.client_combo)

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

        footer = QHBoxLayout()
        footer.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("Discard changes")
        self.cancel_btn.setStyleSheet(ghost_button_qss())
        self.cancel_btn.clicked.connect(self.reject)
        footer.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("Save")
        self.ok_btn.setToolTip("Confirm changes")
        self.ok_btn.setStyleSheet(primary_button_qss())
        self.ok_btn.clicked.connect(self.accept)
        footer.addWidget(self.ok_btn)

        layout.addLayout(footer)

    def set_state(self, state: MapPropertiesState) -> None:
        """Load a state object into the dialog controls."""
        self._state = replace(state)
        self.desc_edit.setPlainText(state.description)
        self._set_combo_value(self.otbm_combo, state.map_version)
        self._set_combo_value(self.client_combo, state.client_version)
        self.width_spin.setValue(state.width)
        self.height_spin.setValue(state.height)
        self.house_edit.setText(state.house_file)
        self.spawn_edit.setText(state.spawn_file)
        self.waypoint_edit.setText(state.waypoint_file)

    def state(self) -> MapPropertiesState:
        """Return the current dialog state."""
        return self._snapshot_state()

    def accept(self) -> None:  # noqa: D401
        """Accept the dialog and persist the current widget values."""
        self._state = self._snapshot_state()
        super().accept()

    def _snapshot_state(self) -> MapPropertiesState:
        """Collect the current widget values into a state object."""
        return MapPropertiesState(
            description=self.desc_edit.toPlainText(),
            map_version=self.otbm_combo.currentText(),
            client_version=self.client_combo.currentText(),
            width=self.width_spin.value(),
            height=self.height_spin.value(),
            house_file=self.house_edit.text(),
            spawn_file=self.spawn_edit.text(),
            waypoint_file=self.waypoint_edit.text(),
        )

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: str) -> None:
        """Select a combo-box entry, adding it if it is not already present."""
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
            return

        combo.addItem(value)
        combo.setCurrentIndex(combo.count() - 1)
