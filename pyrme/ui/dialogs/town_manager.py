"""Town Manager dialog for editing map towns."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from pyrme.ui.styles.contracts import (
    dialog_base_qss,
    ghost_button_qss,
    item_view_qss,
    primary_button_qss,
    section_heading_qss,
)
from pyrme.ui.theme import THEME

if TYPE_CHECKING:
    from pyrme.core_bridge import EditorShellCoreBridge


class TownManagerDialog(QDialog):
    """Dialog for managing map towns (Thistlewood, Ironforge, etc.)."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bridge = bridge
        self.setWindowTitle("Town Manager")
        self.setMinimumSize(600, 400)
        self.setStyleSheet(dialog_base_qss())

        self._setup_ui()
        self._load_towns()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Split Content Area
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(24)

        # Left Panel: Town List
        left_panel = QVBoxLayout()
        list_label = QLabel("TOWNS")
        list_label.setStyleSheet(section_heading_qss())
        left_panel.addWidget(list_label)

        self.town_list = QListWidget()
        self.town_list.setStyleSheet(item_view_qss("QListWidget"))
        self.town_list.currentRowChanged.connect(self._on_town_selected)
        left_panel.addWidget(self.town_list)
        content_layout.addLayout(left_panel, 1)

        # Right Panel: Town Details
        right_panel = QVBoxLayout()
        details_label = QLabel("SELECTED ENTITY DETAILS")
        details_label.setStyleSheet(section_heading_qss())
        right_panel.addWidget(details_label)

        # Form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 12, 0, 0)
        form_layout.setSpacing(16)

        # Name Field
        name_label = QLabel("TOWN NAME")
        name_label.setStyleSheet(section_heading_qss())
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_data_changed)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_edit)

        # Temple Position
        pos_label = QLabel("TEMPLE POSITION")
        pos_label.setStyleSheet(section_heading_qss())
        form_layout.addWidget(pos_label)

        pos_layout = QHBoxLayout()
        self.x_spin = self._create_spin_box(0, 65535, "X")
        self.y_spin = self._create_spin_box(0, 65535, "Y")
        self.z_spin = self._create_spin_box(0, 15, "Z")
        
        pos_layout.addWidget(self.x_spin)
        pos_layout.addWidget(self.y_spin)
        pos_layout.addWidget(self.z_spin)
        form_layout.addLayout(pos_layout)

        form_layout.addStretch()
        right_panel.addWidget(form_widget)
        content_layout.addLayout(right_panel, 2)

        main_layout.addWidget(content_frame)

        # Bottom Bar: Actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet(f"background-color: {THEME.surface_container_low.name()};")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(16, 12, 16, 12)

        self.add_btn = QPushButton("+ Add Town")
        self.add_btn.setStyleSheet(ghost_button_qss())
        self.add_btn.clicked.connect(self._add_town)

        self.remove_btn = QPushButton("Delete Town")
        self.remove_btn.setStyleSheet(ghost_button_qss())
        self.remove_btn.clicked.connect(self._remove_town)

        self.close_btn = QPushButton("Close Editor")
        self.close_btn.setStyleSheet(primary_button_qss())
        self.close_btn.clicked.connect(self.accept)

        actions_layout.addWidget(self.add_btn)
        actions_layout.addWidget(self.remove_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.close_btn)

        main_layout.addWidget(actions_frame)

    def _create_spin_box(self, min_val: int, max_val: int, suffix: str) -> QSpinBox:
        sb = QSpinBox()
        sb.setRange(min_val, max_val)
        sb.setPrefix(f"{suffix}: ")
        sb.setStyleSheet(dialog_base_qss("QSpinBox"))
        sb.valueChanged.connect(self._on_data_changed)
        return sb

    def _load_towns(self) -> None:
        self.town_list.clear()
        towns = self.bridge.towns()
        for town in towns:
            item = QListWidgetItem(town["name"])
            item.setData(Qt.ItemDataRole.UserRole, town)
            self.town_list.addItem(item)
        
        if self.town_list.count() > 0:
            self.town_list.setCurrentRow(0)
        else:
            self._update_form(None)

    def _on_town_selected(self, row: int) -> None:
        if row < 0:
            self._update_form(None)
            return
        
        item = self.town_list.item(row)
        town = item.data(Qt.ItemDataRole.UserRole)
        self._update_form(town)

    def _update_form(self, town: dict | None) -> None:
        self.name_edit.blockSignals(True)
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.z_spin.blockSignals(True)

        if town:
            self.name_edit.setText(town["name"])
            self.x_spin.setValue(town["temple_x"])
            self.y_spin.setValue(town["temple_y"])
            self.z_spin.setValue(town["temple_z"])
            self.name_edit.setEnabled(True)
            self.x_spin.setEnabled(True)
            self.y_spin.setEnabled(True)
            self.z_spin.setEnabled(True)
            self.remove_btn.setEnabled(True)
        else:
            self.name_edit.clear()
            self.x_spin.setValue(0)
            self.y_spin.setValue(0)
            self.z_spin.setValue(0)
            self.name_edit.setEnabled(False)
            self.x_spin.setEnabled(False)
            self.y_spin.setEnabled(False)
            self.z_spin.setEnabled(False)
            self.remove_btn.setEnabled(False)

        self.name_edit.blockSignals(False)
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.z_spin.blockSignals(False)

    def _on_data_changed(self) -> None:
        row = self.town_list.currentRow()
        if row < 0:
            return

        item = self.town_list.item(row)
        town = item.data(Qt.ItemDataRole.UserRole)
        
        # Update local data and UI list item
        new_name = self.name_edit.text()
        town["name"] = new_name
        town["temple_x"] = self.x_spin.value()
        town["temple_y"] = self.y_spin.value()
        town["temple_z"] = self.z_spin.value()
        
        item.setText(new_name)
        
        # Push to backend (add_town overwrites if ID exists)
        self.bridge.add_town(
            town["id"],
            town["name"],
            town["temple_x"],
            town["temple_y"],
            town["temple_z"],
        )

    def _add_town(self) -> None:
        # Generate a new unique ID
        existing_ids = [self.town_list.item(i).data(Qt.ItemDataRole.UserRole)["id"] 
                       for i in range(self.town_list.count())]
        new_id = max(existing_ids) + 1 if existing_ids else 1
        
        new_town = {
            "id": new_id,
            "name": f"New Town {new_id}",
            "temple_x": 1000,
            "temple_y": 1000,
            "temple_z": 7,
        }
        
        self.bridge.add_town(
            new_town["id"],
            new_town["name"],
            new_town["temple_x"],
            new_town["temple_y"],
            new_town["temple_z"],
        )
        self._load_towns()
        
        # Select the new town
        for i in range(self.town_list.count()):
            if self.town_list.item(i).data(Qt.ItemDataRole.UserRole)["id"] == new_id:
                self.town_list.setCurrentRow(i)
                break

    def _remove_town(self) -> None:
        row = self.town_list.currentRow()
        if row < 0:
            return
            
        item = self.town_list.item(row)
        town = item.data(Qt.ItemDataRole.UserRole)
        
        self.bridge.remove_town(town["id"])
        self._load_towns()
