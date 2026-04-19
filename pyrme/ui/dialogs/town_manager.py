"""Town Manager Dialog.

Ported from legacy C++ EditTownsDialog (ui/map/towns_window.cpp).
Follows the Noct Map Editor Design System (DESIGN.md) for dialog styling.
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.position_input import PositionInput
from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY


@dataclass(slots=True)
class TownData:
    """Represents a town in the town manager."""

    id_: int
    name: str = "Unnamed Town"
    temple_x: int = 0
    temple_y: int = 0
    temple_z: int = 7


class TownManagerDialog(QDialog):
    """Dialog for managing map towns."""

    goto_requested = pyqtSignal(int, int, int)
    DIALOG_SIZE = QSize(400, 500)

    def __init__(
        self,
        parent: QWidget | None = None,
        towns: list[TownData] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Towns")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        # Internal state
        self._towns = list(towns) if towns is not None else []
        self._current_index = -1
        self._next_id = max((t.id_ for t in self._towns), default=0) + 1

        self._apply_dialog_style()
        self._build_layout()
        self._populate_list()
        self._update_ui_state()

        # Connections
        self.town_list.currentRowChanged.connect(self._on_town_selected)
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.pos_input.position_changed.connect(self._on_position_changed)
        self.btn_add.clicked.connect(self._on_add_town)
        self.btn_remove.clicked.connect(self._on_remove_town)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor dialog styling."""
        self.setStyleSheet(dialog_base_qss("QLineEdit, QListWidget"))

    def _build_layout(self) -> None:
        """Construct the dialog layout matching legacy EditTownsDialog."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        heading = QLabel("Town Manager")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        # List and Add/Remove buttons
        list_container = QVBoxLayout()
        list_container.setSpacing(8)

        self.town_list = QListWidget()
        list_container.addWidget(self.town_list)

        list_actions = QHBoxLayout()
        list_actions.setSpacing(8)
        self.btn_add = QPushButton("Add")
        self.btn_add.setStyleSheet(ghost_button_qss())
        self.btn_remove = QPushButton("Remove")
        self.btn_remove.setStyleSheet(ghost_button_qss())
        list_actions.addWidget(self.btn_add)
        list_actions.addWidget(self.btn_remove)
        list_actions.addStretch()

        list_container.addLayout(list_actions)
        layout.addLayout(list_container, 1)

        # Edit Section
        self.edit_container = QWidget()
        edit_layout = QVBoxLayout(self.edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(16)

        form = QFormLayout()
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        form.setSpacing(12)

        self.name_edit = QLineEdit()
        self.name_edit.setToolTip("Town name")
        form.addRow("Name:", self.name_edit)

        self.id_edit = QLineEdit()
        self.id_edit.setToolTip("Town ID")
        self.id_edit.setReadOnly(True)
        form.addRow("ID:", self.id_edit)

        edit_layout.addLayout(form)

        # Temple Position
        pos_layout = QVBoxLayout()
        pos_layout.setSpacing(8)
        pos_layout.addWidget(QLabel("Temple Position:"))
        self.pos_input = PositionInput()
        pos_layout.addWidget(self.pos_input)

        self.btn_goto = QPushButton("Go To")
        self.btn_goto.setStyleSheet(ghost_button_qss())
        self.btn_goto.setToolTip("Jump to temple position")
        self.btn_goto.clicked.connect(self._on_goto_clicked)
        pos_layout.addWidget(self.btn_goto, 0, Qt.AlignmentFlag.AlignRight)

        edit_layout.addLayout(pos_layout)
        layout.addWidget(self.edit_container)

        layout.addStretch()

        # Dialog Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet(ghost_button_qss())
        self.btn_ok = QPushButton("Save Changes")
        self.btn_ok.setStyleSheet(primary_button_qss())

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)

    def _populate_list(self) -> None:
        """Populate the list widget from internal state."""
        self.town_list.clear()
        for town in self._towns:
            item = QListWidgetItem(f"{town.id_} - {town.name}")
            self.town_list.addItem(item)
        if self._towns:
            self.town_list.setCurrentRow(0)

    def _update_ui_state(self) -> None:
        """Update enabled states and inputs based on selection."""
        has_selection = self._current_index >= 0 and self._current_index < len(
            self._towns
        )

        self.edit_container.setEnabled(has_selection)
        self.btn_remove.setEnabled(has_selection)

        if has_selection:
            town = self._towns[self._current_index]
            self.name_edit.blockSignals(True)
            self.pos_input.blockSignals(True)

            self.name_edit.setText(town.name)
            self.id_edit.setText(str(town.id_))
            self.pos_input.set_position(town.temple_x, town.temple_y, town.temple_z)

            self.name_edit.blockSignals(False)
            self.pos_input.blockSignals(False)
        else:
            self.name_edit.clear()
            self.id_edit.clear()

    def _on_town_selected(self, index: int) -> None:
        self._current_index = index
        self._update_ui_state()

    def _on_name_changed(self, text: str) -> None:
        if 0 <= self._current_index < len(self._towns):
            self._towns[self._current_index].name = text
            # Update list item text without triggering selection logic
            item = self.town_list.item(self._current_index)
            if item:
                item.setText(f"{self._towns[self._current_index].id_} - {text}")

    def _on_position_changed(self, x: int, y: int, z: int) -> None:
        if 0 <= self._current_index < len(self._towns):
            town = self._towns[self._current_index]
            town.temple_x = x
            town.temple_y = y
            town.temple_z = z

    def _on_add_town(self) -> None:
        new_town = TownData(id_=self._next_id)
        self._next_id += 1
        self._towns.append(new_town)

        item = QListWidgetItem(f"{new_town.id_} - {new_town.name}")
        self.town_list.addItem(item)
        self.town_list.setCurrentRow(len(self._towns) - 1)

    def _on_remove_town(self) -> None:
        if 0 <= self._current_index < len(self._towns):
            self._towns.pop(self._current_index)
            self.town_list.takeItem(self._current_index)
            # Row changed signal will update index

    def _on_goto_clicked(self) -> None:
        """Emulate 'Go To' feature by centering editor on town."""
        if 0 <= self._current_index < len(self._towns):
            town = self._towns[self._current_index]
            self.goto_requested.emit(town.temple_x, town.temple_y, town.temple_z)

    def get_towns(self) -> list[TownData]:
        """Return the modified towns."""
        return list(self._towns)
