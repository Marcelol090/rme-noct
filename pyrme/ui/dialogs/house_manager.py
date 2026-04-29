"""House Manager Dialog.

Ported from legacy C++ HousePalette (palette/house/house_palette.cpp).
Follows the Noct Map Editor Design System (DESIGN.md) for dialog styling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSize, Qt
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
    QComboBox,
    QCheckBox,
)

from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY

if TYPE_CHECKING:
    from pyrme.ui.main_window import MainWindow


@dataclass(slots=True)
class HouseData:
    """Local data representation for a house."""
    id: int
    name: str
    town_id: int
    rent: int
    is_guildhall: bool
    entry_x: int
    entry_y: int
    entry_z: int


class HouseManagerDialog(QDialog):
    """Dialog for managing houses, their properties and positions."""

    # DESIGN.md: Preferred size for split-view dialogs
    DIALOG_SIZE = QSize(720, 520)

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        self.setWindowTitle("House Manager")
        self.setMinimumSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._main_window = parent
        self._editor = parent._editor_context.session.editor
        self._houses: dict[int, HouseData] = {}
        self._selected_house_id: int | None = None

        self._apply_dialog_style()
        self._build_layout()
        self._refresh_town_filter()
        self._refresh_house_list()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Glassmorphism styling."""
        self.setStyleSheet(
            dialog_base_qss("QLineEdit, QSpinBox, QListWidget, QComboBox, QCheckBox")
        )

    def _build_layout(self) -> None:
        """Construct the split-view layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar (House List + Filters) ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: rgba(27, 27, 37, 0.5);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(12)

        sidebar_title = QLabel("HOUSES")
        sidebar_title.setFont(TYPOGRAPHY.label_sm())
        sidebar_title.setStyleSheet("color: rgba(201, 196, 215, 0.7);")
        sidebar_layout.addWidget(sidebar_title)

        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search houses...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        sidebar_layout.addWidget(self.search_edit)

        # Town Filter
        self.town_filter = QComboBox()
        self.town_filter.addItem("All Towns", 0)
        self.town_filter.currentIndexChanged.connect(self._on_search_changed)
        sidebar_layout.addWidget(self.town_filter)

        self.house_list = QListWidget()
        self.house_list.itemSelectionChanged.connect(self._on_selection_changed)
        sidebar_layout.addWidget(self.house_list)

        self.add_btn = QPushButton("Add House")
        self.add_btn.setStyleSheet(ghost_button_qss())
        self.add_btn.clicked.connect(self._on_add_house)
        sidebar_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("Remove House")
        self.remove_btn.setStyleSheet(ghost_button_qss())
        self.remove_btn.clicked.connect(self._on_remove_house)
        self.remove_btn.setEnabled(False)
        sidebar_layout.addWidget(self.remove_btn)

        main_layout.addWidget(sidebar)

        # --- Main Content Area ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 24)
        content_layout.setSpacing(24)

        header = QLabel("HOUSE PROPERTIES")
        header.setFont(TYPOGRAPHY.dialog_heading())
        content_layout.addWidget(header)

        # Details Form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)

        # Name
        name_label = QLabel("Name")
        name_label.setFont(TYPOGRAPHY.label_sm())
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_data_changed)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_edit)

        # House ID
        id_layout = QHBoxLayout()
        id_inner_layout = QVBoxLayout()
        id_label = QLabel("House ID")
        id_label.setFont(TYPOGRAPHY.label_sm())
        self.id_spin = QSpinBox()
        self.id_spin.setRange(1, 999999)
        self.id_spin.setEnabled(False) # ID is immutable in legacy usually, or needs special care
        id_inner_layout.addWidget(id_label)
        id_inner_layout.addWidget(self.id_spin)
        id_layout.addLayout(id_inner_layout)

        # Rent
        rent_inner_layout = QVBoxLayout()
        rent_label = QLabel("Monthly Rent")
        rent_label.setFont(TYPOGRAPHY.label_sm())
        self.rent_spin = QSpinBox()
        self.rent_spin.setRange(0, 2000000000)
        self.rent_spin.setSuffix(" gp")
        self.rent_spin.valueChanged.connect(self._on_data_changed)
        rent_inner_layout.addWidget(rent_label)
        rent_inner_layout.addWidget(self.rent_spin)
        id_layout.addLayout(rent_inner_layout)
        form_layout.addLayout(id_layout)

        # Town Selection
        town_label = QLabel("Town")
        town_label.setFont(TYPOGRAPHY.label_sm())
        self.town_combo = QComboBox()
        self.town_combo.currentIndexChanged.connect(self._on_data_changed)
        form_layout.addWidget(town_label)
        form_layout.addWidget(self.town_combo)

        # Guildhall
        self.guildhall_check = QCheckBox("Guildhall")
        self.guildhall_check.setFont(TYPOGRAPHY.label_sm())
        self.guildhall_check.stateChanged.connect(self._on_data_changed)
        form_layout.addWidget(self.guildhall_check)

        # Entry Position
        pos_label = QLabel("ENTRY COORDINATES")
        pos_label.setFont(TYPOGRAPHY.label_sm())
        pos_label.setStyleSheet("margin-top: 8px;")
        content_layout.addWidget(pos_label)

        pos_widget = QWidget()
        pos_layout = QHBoxLayout(pos_widget)
        pos_layout.setContentsMargins(0, 0, 0, 0)
        pos_layout.setSpacing(12)

        self.x_spin = self._create_coord_spin()
        self.y_spin = self._create_coord_spin()
        self.z_spin = self._create_coord_spin(max_val=15)

        pos_layout.addWidget(QLabel("X"))
        pos_layout.addWidget(self.x_spin)
        pos_layout.addWidget(QLabel("Y"))
        pos_layout.addWidget(self.y_spin)
        pos_layout.addWidget(QLabel("Z"))
        pos_layout.addWidget(self.z_spin)

        self.jump_btn = QPushButton("Jump")
        self.jump_btn.setToolTip("Go to Entry")
        self.jump_btn.setFixedWidth(60)
        self.jump_btn.setStyleSheet(ghost_button_qss())
        self.jump_btn.clicked.connect(self._on_jump_to_entry)
        pos_layout.addWidget(self.jump_btn)

        form_layout.addWidget(pos_widget)
        content_layout.addLayout(form_layout)
        content_layout.addStretch()

        # Footer Actions
        footer = QHBoxLayout()
        footer.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(primary_button_qss())
        self.close_btn.clicked.connect(self.accept)
        footer.addWidget(self.close_btn)

        content_layout.addLayout(footer)
        main_layout.addWidget(content, 1)

        self._enable_details(False)

    def _create_coord_spin(self, max_val: int = 65535) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(0, max_val)
        spin.setStyleSheet("font-family: 'JetBrains Mono';")
        spin.valueChanged.connect(self._on_data_changed)
        return spin

    def _refresh_town_filter(self) -> None:
        """Populate town combos."""
        self.town_filter.blockSignals(True)
        self.town_combo.blockSignals(True)
        
        self.town_filter.clear()
        self.town_combo.clear()
        
        self.town_filter.addItem("All Towns", 0)
        self.town_combo.addItem("None", 0)
        
        towns = self._editor.get_towns()
        for tid, name, _, _, _ in towns:
            self.town_filter.addItem(name, tid)
            self.town_combo.addItem(name, tid)
            
        self.town_filter.blockSignals(False)
        self.town_combo.blockSignals(False)

    def _refresh_house_list(self) -> None:
        """Reload houses from the editor core and apply filters."""
        self.house_list.clear()
        houses_raw = self._editor.get_houses()
        self._houses = {}
        
        search_text = self.search_edit.text().lower()
        town_id_filter = self.town_filter.currentData()

        for hid, name, tid, rent, is_gh, x, y, z in houses_raw:
            house = HouseData(hid, name, tid, rent, is_gh, x, y, z)
            self._houses[hid] = house
            
            # Apply filters
            if search_text and search_text not in name.lower() and search_text not in str(hid):
                continue
            if town_id_filter != 0 and tid != town_id_filter:
                continue

            item = QListWidgetItem(f"[{hid}] {name}")
            item.setData(Qt.ItemDataRole.UserRole, hid)
            self.house_list.addItem(item)

        if self._selected_house_id is not None:
            # Re-select if still exists and visible
            for i in range(self.house_list.count()):
                item = self.house_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self._selected_house_id:
                    self.house_list.setCurrentItem(item)
                    break

    def _on_selection_changed(self) -> None:
        """Handle house selection from the list."""
        items = self.house_list.selectedItems()
        if not items:
            self._selected_house_id = None
            self._enable_details(False)
            self.remove_btn.setEnabled(False)
            return

        hid = items[0].data(Qt.ItemDataRole.UserRole)
        self._selected_house_id = hid
        house = self._houses[hid]

        # Block signals to avoid feedback loops
        self.name_edit.blockSignals(True)
        self.id_spin.blockSignals(True)
        self.rent_spin.blockSignals(True)
        self.town_combo.blockSignals(True)
        self.guildhall_check.blockSignals(True)
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.z_spin.blockSignals(True)

        self.name_edit.setText(house.name)
        self.id_spin.setValue(house.id)
        self.rent_spin.setValue(house.rent)
        
        # Set town combo
        idx = self.town_combo.findData(house.town_id)
        self.town_combo.setCurrentIndex(idx if idx >= 0 else 0)
        
        self.guildhall_check.setChecked(house.is_guildhall)
        self.x_spin.setValue(house.entry_x)
        self.y_spin.setValue(house.entry_y)
        self.z_spin.setValue(house.entry_z)

        self.name_edit.blockSignals(False)
        self.id_spin.blockSignals(False)
        self.rent_spin.blockSignals(False)
        self.town_combo.blockSignals(False)
        self.guildhall_check.blockSignals(False)
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.z_spin.blockSignals(False)

        self._enable_details(True)
        self.remove_btn.setEnabled(True)

    def _enable_details(self, enabled: bool) -> None:
        self.name_edit.setEnabled(enabled)
        self.rent_spin.setEnabled(enabled)
        self.town_combo.setEnabled(enabled)
        self.guildhall_check.setEnabled(enabled)
        self.x_spin.setEnabled(enabled)
        self.y_spin.setEnabled(enabled)
        self.z_spin.setEnabled(enabled)
        self.jump_btn.setEnabled(enabled)

    def _on_data_changed(self) -> None:
        """Sync local changes back to the editor core."""
        if self._selected_house_id is None:
            return

        name = self.name_edit.text()
        town_id = self.town_combo.currentData()
        rent = self.rent_spin.value()
        is_gh = self.guildhall_check.isChecked()
        x = self.x_spin.value()
        y = self.y_spin.value()
        z = self.z_spin.value()

        # Update Rust Core
        success = self._editor.update_house(self._selected_house_id, name, town_id, rent, is_gh, x, y, z)
        if success:
            # Update local list label if name changed
            items = self.house_list.selectedItems()
            if items:
                new_label = f"[{self._selected_house_id}] {name}"
                if items[0].text() != new_label:
                    items[0].setText(new_label)
            # Update local cache
            self._houses[self._selected_house_id] = HouseData(
                self._selected_house_id, name, town_id, rent, is_gh, x, y, z
            )

    def _on_search_changed(self) -> None:
        """Handle search or filter changes."""
        self._refresh_house_list()

    def _on_add_house(self) -> None:
        """Create a new house."""
        # Find next available ID
        ids = self._houses.keys()
        next_id = max(ids) + 1 if ids else 1
        
        success = self._editor.add_house(next_id, "New House", 0)
        if success:
            self._selected_house_id = next_id
            self._refresh_house_list()
            
            # Select the new house
            for i in range(self.house_list.count()):
                item = self.house_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == next_id:
                    self.house_list.setCurrentItem(item)
                    self.name_edit.setFocus()
                    self.name_edit.selectAll()
                    break

    def _on_remove_house(self) -> None:
        """Remove the selected house."""
        if self._selected_house_id is None:
            return
            
        success = self._editor.remove_house(self._selected_house_id)
        if success:
            self._selected_house_id = None
            self._refresh_house_list()

    def _on_jump_to_entry(self) -> None:
        """Teleport editor camera to the selected house's entry."""
        if self._selected_house_id is None:
            return
            
        house = self._houses[self._selected_house_id]
        self._main_window._set_current_position(house.entry_x, house.entry_y, house.entry_z)
