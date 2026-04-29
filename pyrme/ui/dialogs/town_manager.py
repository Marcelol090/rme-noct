"""Town Manager Dialog.

Ported from legacy C++ TownsWindow (ui/map/towns_window.cpp).
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
)

from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY

if TYPE_CHECKING:
    from pyrme.ui.main_window import MainWindow


@dataclass(slots=True)
class TownData:
    """Local data representation for a town."""
    id: int
    name: str
    x: int
    y: int
    z: int


class TownManagerDialog(QDialog):
    """Dialog for managing towns and their temple positions."""

    # DESIGN.md: Preferred size for split-view dialogs
    DIALOG_SIZE = QSize(640, 480)

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        self.setWindowTitle("Town Manager")
        self.setMinimumSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._main_window = parent
        self._editor = parent._editor_context.session.editor
        self._towns: dict[int, TownData] = {}
        self._selected_town_id: int | None = None

        self._apply_dialog_style()
        self._build_layout()
        self._refresh_town_list()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Glassmorphism styling."""
        self.setStyleSheet(
            dialog_base_qss("QLineEdit, QSpinBox, QListWidget")
        )

    def _build_layout(self) -> None:
        """Construct the split-view layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar (Town List) ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: rgba(27, 27, 37, 0.5);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(12)

        sidebar_title = QLabel("TOWNS")
        sidebar_title.setFont(TYPOGRAPHY.label_sm())
        sidebar_title.setStyleSheet("color: rgba(201, 196, 215, 0.7);")
        sidebar_layout.addWidget(sidebar_title)

        self.town_list = QListWidget()
        self.town_list.itemSelectionChanged.connect(self._on_selection_changed)
        sidebar_layout.addWidget(self.town_list)

        self.add_btn = QPushButton("Add Town")
        self.add_btn.setStyleSheet(ghost_button_qss())
        self.add_btn.clicked.connect(self._on_add_town)
        sidebar_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("Remove Town")
        self.remove_btn.setStyleSheet(ghost_button_qss())
        self.remove_btn.clicked.connect(self._on_remove_town)
        self.remove_btn.setEnabled(False)
        sidebar_layout.addWidget(self.remove_btn)

        main_layout.addWidget(sidebar)

        # --- Main Content Area ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 24)
        content_layout.setSpacing(24)

        header = QLabel("TOWN PROPERTIES")
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

        # ID (ReadOnly)
        id_label = QLabel("Town ID")
        id_label.setFont(TYPOGRAPHY.label_sm())
        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)
        self.id_edit.setStyleSheet(self.id_edit.styleSheet() + "color: rgba(255, 255, 255, 0.4); font-family: 'JetBrains Mono';")
        form_layout.addWidget(id_label)
        form_layout.addWidget(self.id_edit)

        # Temple Position
        pos_label = QLabel("TEMPLE COORDINATES")
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
        self.jump_btn.setToolTip("Go to Temple")
        self.jump_btn.setFixedWidth(60)
        self.jump_btn.setStyleSheet(ghost_button_qss())
        self.jump_btn.clicked.connect(self._on_jump_to_temple)
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

    def _refresh_town_list(self) -> None:
        """Reload towns from the editor core."""
        self.town_list.clear()
        towns_raw = self._editor.get_towns()
        self._towns = {}
        
        for tid, name, x, y, z in towns_raw:
            town = TownData(tid, name, x, y, z)
            self._towns[tid] = town
            
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, tid)
            self.town_list.addItem(item)

        if self._selected_town_id is not None:
            # Re-select if still exists
            for i in range(self.town_list.count()):
                item = self.town_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self._selected_town_id:
                    self.town_list.setCurrentItem(item)
                    break

    def _on_selection_changed(self) -> None:
        """Handle town selection from the list."""
        items = self.town_list.selectedItems()
        if not items:
            self._selected_town_id = None
            self._enable_details(False)
            self.remove_btn.setEnabled(False)
            return

        tid = items[0].data(Qt.ItemDataRole.UserRole)
        self._selected_town_id = tid
        town = self._towns[tid]

        # Block signals to avoid feedback loops while updating fields
        self.name_edit.blockSignals(True)
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.z_spin.blockSignals(True)

        self.name_edit.setText(town.name)
        self.id_edit.setText(str(town.id))
        self.x_spin.setValue(town.x)
        self.y_spin.setValue(town.y)
        self.z_spin.setValue(town.z)

        self.name_edit.blockSignals(False)
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.z_spin.blockSignals(False)

        self._enable_details(True)
        self.remove_btn.setEnabled(True)

    def _enable_details(self, enabled: bool) -> None:
        self.name_edit.setEnabled(enabled)
        self.x_spin.setEnabled(enabled)
        self.y_spin.setEnabled(enabled)
        self.z_spin.setEnabled(enabled)
        self.jump_btn.setEnabled(enabled)

    def _on_data_changed(self) -> None:
        """Sync local changes back to the editor core."""
        if self._selected_town_id is None:
            return

        name = self.name_edit.text()
        x = self.x_spin.value()
        y = self.y_spin.value()
        z = self.z_spin.value()

        # Update Rust Core
        success = self._editor.update_town(self._selected_town_id, name, x, y, z)
        if success:
            # Update local list label if name changed
            items = self.town_list.selectedItems()
            if items and items[0].text() != name:
                items[0].setText(name)
            # Update local cache
            self._towns[self._selected_town_id] = TownData(self._selected_town_id, name, x, y, z)

    def _on_add_town(self) -> None:
        """Create a new town with default values."""
        new_id = self._editor.add_town("New Town", 32000, 32000, 7)
        self._selected_town_id = new_id
        self._refresh_town_list()
        
        # Select the new town
        for i in range(self.town_list.count()):
            item = self.town_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == new_id:
                self.town_list.setCurrentItem(item)
                self.name_edit.setFocus()
                self.name_edit.selectAll()
                break

    def _on_remove_town(self) -> None:
        """Remove the selected town."""
        if self._selected_town_id is None:
            return
            
        success = self._editor.remove_town(self._selected_town_id)
        if success:
            self._selected_town_id = None
            self._refresh_town_list()

    def _on_jump_to_temple(self) -> None:
        """Teleport editor camera to the selected town's temple."""
        if self._selected_town_id is None:
            return
            
        town = self._towns[self._selected_town_id]
        self._main_window._set_current_position(town.x, town.y, town.z)
