"""Tile Properties dialog for editing tile items and their properties."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles.contracts import (
    dialog_base_qss,
    dropdown_qss,
    ghost_button_qss,
    input_field_qss,
    item_view_qss,
    primary_button_qss,
    section_heading_qss,
)
from pyrme.ui.theme import THEME

if TYPE_CHECKING:
    from pyrme.core_bridge import EditorShellCoreBridge


class BasePropertyPanel(QWidget):
    """Base panel for item properties."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None):
        super().__init__(parent)
        self.bridge = bridge
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 12, 0, 0)
        self.layout.setSpacing(16)

    def _create_spin_box(self, min_val: int, max_val: int, suffix: str = "") -> QSpinBox:
        sb = QSpinBox()
        sb.setRange(min_val, max_val)
        if suffix:
            sb.setSuffix(f" {suffix}")
        sb.setStyleSheet(input_field_qss("QSpinBox"))
        return sb


class ItemPropertyPanel(BasePropertyPanel):
    """Panel for generic item properties like Action ID and Unique ID."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None):
        super().__init__(bridge, parent)

        # Action ID
        action_label = QLabel("ACTION ID")
        action_label.setStyleSheet(section_heading_qss())
        self.action_spin = self._create_spin_box(0, 65535)

        # Unique ID
        unique_label = QLabel("UNIQUE ID")
        unique_label.setStyleSheet(section_heading_qss())
        self.unique_spin = self._create_spin_box(0, 65535)

        self.layout.addWidget(action_label)
        self.layout.addWidget(self.action_spin)
        self.layout.addWidget(unique_label)
        self.layout.addWidget(self.unique_spin)
        self.layout.addStretch()

    def set_data(self, item_data: dict[str, Any]) -> None:
        self.action_spin.setValue(item_data.get("action_id", 0))
        self.unique_spin.setValue(item_data.get("unique_id", 0))


class DepotPropertyPanel(ItemPropertyPanel):
    """Panel for Depot specific properties."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None):
        super().__init__(bridge, parent)

        # Remove stretch from parent
        self.layout.takeAt(self.layout.count() - 1)

        # Town ID
        town_label = QLabel("TOWN")
        town_label.setStyleSheet(section_heading_qss())
        self.town_combo = QComboBox()
        self.town_combo.setStyleSheet(dropdown_qss())

        self.layout.addWidget(town_label)
        self.layout.addWidget(self.town_combo)
        self.layout.addStretch()

    def set_data(self, item_data: dict[str, Any]) -> None:
        super().set_data(item_data)
        self.town_combo.clear()
        towns = self.bridge.towns()
        for t in towns:
            self.town_combo.addItem(t[1], t[0])

        town_id = item_data.get("town_id", 0)
        index = self.town_combo.findData(town_id)
        if index >= 0:
            self.town_combo.setCurrentIndex(index)


class DoorPropertyPanel(ItemPropertyPanel):
    """Panel for Door specific properties."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None):
        super().__init__(bridge, parent)

        # Remove stretch from parent
        self.layout.takeAt(self.layout.count() - 1)

        # Door ID
        door_label = QLabel("DOOR ID")
        door_label.setStyleSheet(section_heading_qss())
        self.door_spin = self._create_spin_box(0, 255)

        self.layout.addWidget(door_label)
        self.layout.addWidget(self.door_spin)
        self.layout.addStretch()

    def set_data(self, item_data: dict[str, Any]) -> None:
        super().set_data(item_data)
        self.door_spin.setValue(item_data.get("door_id", 0))


class TeleportPropertyPanel(ItemPropertyPanel):
    """Panel for Teleport specific properties."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None):
        super().__init__(bridge, parent)

        # Remove stretch from parent
        self.layout.takeAt(self.layout.count() - 1)

        # Destination
        dest_label = QLabel("DESTINATION POSITION")
        dest_label.setStyleSheet(section_heading_qss())
        self.layout.addWidget(dest_label)

        pos_layout = QHBoxLayout()
        self.x_spin = self._create_spin_box(0, 65535, "X")
        self.y_spin = self._create_spin_box(0, 65535, "Y")
        self.z_spin = self._create_spin_box(0, 15, "Z")

        pos_layout.addWidget(self.x_spin)
        pos_layout.addWidget(self.y_spin)
        pos_layout.addWidget(self.z_spin)
        self.layout.addLayout(pos_layout)

        self.layout.addStretch()

    def set_data(self, item_data: dict[str, Any]) -> None:
        super().set_data(item_data)
        self.x_spin.setValue(item_data.get("dest_x", 0))
        self.y_spin.setValue(item_data.get("dest_y", 0))
        self.z_spin.setValue(item_data.get("dest_z", 0))


class WritablePropertyPanel(ItemPropertyPanel):
    """Panel for Writable specific properties (Text/Description)."""

    def __init__(self, bridge: EditorShellCoreBridge, parent: QWidget | None = None):
        super().__init__(bridge, parent)

        # Remove stretch from parent
        self.layout.takeAt(self.layout.count() - 1)

        # Text
        text_label = QLabel("TEXT DESCRIPTION")
        text_label.setStyleSheet(section_heading_qss())
        self.layout.addWidget(text_label)

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(input_field_qss("QTextEdit"))
        self.layout.addWidget(self.text_edit, 1) # Give it stretch

    def set_data(self, item_data: dict[str, Any]) -> None:
        super().set_data(item_data)
        self.text_edit.setText(item_data.get("text", ""))


class TilePropertiesDialog(QDialog):
    """Dialog for inspecting and modifying properties of items on a specific tile."""

    def __init__(self, bridge: EditorShellCoreBridge, x: int, y: int, z: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bridge = bridge
        self.tile_x = x
        self.tile_y = y
        self.tile_z = z

        self.setWindowTitle(f"Tile Properties (X: {x}, Y: {y}, Z: {z})")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(dialog_base_qss())

        self._setup_ui()
        self._load_tile_items()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Split Content Area
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {THEME.void_black.name()};
            }}
        """)

        # Left Panel: Object Stack (Items/Creatures)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 8, 16)

        stack_label = QLabel("OBJECT STACK")
        stack_label.setStyleSheet(section_heading_qss())
        left_layout.addWidget(stack_label)

        self.item_list = QListWidget()
        self.item_list.setStyleSheet(item_view_qss("QListWidget"))
        self.item_list.currentRowChanged.connect(self._on_item_selected)
        left_layout.addWidget(self.item_list)

        self.splitter.addWidget(left_panel)

        # Right Panel: Properties Editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 16, 16, 16)

        self.details_label = QLabel("PROPERTIES")
        self.details_label.setStyleSheet(section_heading_qss())
        right_layout.addWidget(self.details_label)

        # We will use a QStackedWidget to swap between different property panels (Depot, Teleport, etc.)
        self.properties_stack = QStackedWidget()

        # Placeholder panel when nothing is selected
        self.placeholder_panel = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_panel)
        placeholder_text = QLabel("Select an item to view properties")
        placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_text.setStyleSheet(f"color: {THEME.ash_lavender.name()};")
        placeholder_layout.addWidget(placeholder_text)
        self.properties_stack.addWidget(self.placeholder_panel)

        # Add property panels
        self.item_panel = ItemPropertyPanel(self.bridge)
        self.depot_panel = DepotPropertyPanel(self.bridge)
        self.door_panel = DoorPropertyPanel(self.bridge)
        self.teleport_panel = TeleportPropertyPanel(self.bridge)
        self.writable_panel = WritablePropertyPanel(self.bridge)

        self.properties_stack.addWidget(self.item_panel)
        self.properties_stack.addWidget(self.depot_panel)
        self.properties_stack.addWidget(self.door_panel)
        self.properties_stack.addWidget(self.teleport_panel)
        self.properties_stack.addWidget(self.writable_panel)

        right_layout.addWidget(self.properties_stack)

        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([250, 450])
        main_layout.addWidget(self.splitter)

        # Bottom Bar: Actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet(f"background-color: {THEME.void_black.name()};")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(16, 12, 16, 12)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(ghost_button_qss())
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(primary_button_qss())
        self.save_btn.clicked.connect(self.accept)

        actions_layout.addStretch()
        actions_layout.addWidget(self.cancel_btn)
        actions_layout.addWidget(self.save_btn)

        main_layout.addWidget(actions_frame)

    def _load_tile_items(self) -> None:
        self.item_list.clear()
        # TODO: Fetch items from the bridge for the specific coordinate.
        # For now, we mock it based on the design mockup.
        mock_items = [
            {"id": 100, "name": "Grass", "type": "ground"},
            {"id": 102, "name": "Stone Wall", "type": "wall"},
            {"id": 2000, "name": "Depot Box", "type": "depot", "action_id": 0, "unique_id": 0, "town_id": 1},
            {"id": 1210, "name": "Locked Door", "type": "door", "door_id": 15},
            {"id": 1387, "name": "Teleport", "type": "teleport", "dest_x": 1024, "dest_y": 1024, "dest_z": 7},
            {"id": 1948, "name": "Parchment", "type": "writable", "text": "A mysterious scroll."},
        ]

        for item_data in mock_items:
            item = QListWidgetItem(f"{item_data['name']} (ID: {item_data['id']})")
            item.setData(Qt.ItemDataRole.UserRole, item_data)
            self.item_list.addItem(item)

        if self.item_list.count() > 0:
            self.item_list.setCurrentRow(0)

    def _on_item_selected(self, row: int) -> None:
        if row < 0:
            self.properties_stack.setCurrentWidget(self.placeholder_panel)
            self.details_label.setText("PROPERTIES")
            return

        item = self.item_list.item(row)
        item_data = item.data(Qt.ItemDataRole.UserRole)

        self.details_label.setText(f"{item_data['name'].upper()} PROPERTIES")

        item_type = item_data.get("type", "")
        if item_type == "depot":
            self.depot_panel.set_data(item_data)
            self.properties_stack.setCurrentWidget(self.depot_panel)
        elif item_type == "door":
            self.door_panel.set_data(item_data)
            self.properties_stack.setCurrentWidget(self.door_panel)
        elif item_type == "teleport":
            self.teleport_panel.set_data(item_data)
            self.properties_stack.setCurrentWidget(self.teleport_panel)
        elif item_type == "writable":
            self.writable_panel.set_data(item_data)
            self.properties_stack.setCurrentWidget(self.writable_panel)
        elif item_type in ("ground", "wall"):
            # Simple items just show Action ID / Unique ID
            self.item_panel.set_data(item_data)
            self.properties_stack.setCurrentWidget(self.item_panel)
        else:
            self.properties_stack.setCurrentWidget(self.placeholder_panel)
