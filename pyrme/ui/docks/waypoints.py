"""Waypoints Dock.

Manages local waypoint entries with a compact multi-column dock layout.
The dock keeps its own in-memory waypoint list for Tier 2 and can be
connected to map/editor state later without changing the UI contract.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.styles import destructive_button_qss, ghost_button_qss, item_view_qss
from pyrme.ui.theme import TYPOGRAPHY

DEFAULT_WAYPOINT_NAME = "Waypoint"
DEFAULT_WAYPOINT_X = 32000
DEFAULT_WAYPOINT_Y = 32000
DEFAULT_WAYPOINT_Z = 7


@dataclass(slots=True)
class WaypointEntry:
    """A local waypoint model row."""

    name: str
    x: int
    y: int
    z: int
    linked_spawn: str | None = None


class WaypointsDock(GlassDockWidget):
    """Dock widget to manage waypoints."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Waypoints", parent)
        self.setObjectName("WaypointsDock")
        self._waypoints: list[WaypointEntry] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the dock UI within the glass container."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(3)
        self.tree_widget.setHeaderLabels(["Name", "Coordinates", "Linked Spawn"])
        self.tree_widget.setRootIsDecorated(False)
        self.tree_widget.setIndentation(0)
        self.tree_widget.setAlternatingRowColors(False)
        self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree_widget.setUniformRowHeights(True)
        self.tree_widget.currentItemChanged.connect(self._sync_action_state)

        header = self.tree_widget.header()
        if header is not None:
            header.setFont(TYPOGRAPHY.dock_title())
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.resizeSection(1, 150)

        self.tree_widget.setStyleSheet(item_view_qss("QTreeWidget", include_header=True))

        layout.addWidget(self.tree_widget)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(4)

        self.btn_add = QPushButton("Add")
        self.btn_rename = QPushButton("Rename")
        self.btn_remove = QPushButton("Remove")

        self.btn_add.setStyleSheet(ghost_button_qss())
        self.btn_rename.setStyleSheet(ghost_button_qss())
        self.btn_remove.setStyleSheet(destructive_button_qss())

        self.btn_add.clicked.connect(self._add_default_waypoint)
        self.btn_rename.clicked.connect(self._rename_selected_waypoint)
        self.btn_remove.clicked.connect(self._remove_selected_waypoint)

        action_layout.addWidget(self.btn_add)
        action_layout.addWidget(self.btn_rename)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_remove)

        layout.addLayout(action_layout)

        self.set_inner_layout(layout)
        self._sync_action_state()

    def waypoints(self) -> list[WaypointEntry]:
        """Return a snapshot of the current waypoint list."""
        return [replace(entry) for entry in self._waypoints]

    def set_waypoints(self, waypoints: list[WaypointEntry]) -> None:
        """Replace the local waypoint model with the provided entries."""
        self._waypoints = [replace(entry) for entry in waypoints]
        self._refresh_tree()

    def add_waypoint(self, waypoint: WaypointEntry | None = None) -> WaypointEntry:
        """Append a waypoint to the local model and return a copy of it."""
        entry = waypoint or WaypointEntry(
            name=f"{DEFAULT_WAYPOINT_NAME} {len(self._waypoints) + 1}",
            x=DEFAULT_WAYPOINT_X,
            y=DEFAULT_WAYPOINT_Y,
            z=DEFAULT_WAYPOINT_Z,
            linked_spawn=None,
        )
        self._waypoints.append(replace(entry))
        self._refresh_tree(selected_index=len(self._waypoints) - 1)
        return replace(self._waypoints[-1])

    def rename_waypoint(self, index: int, name: str) -> WaypointEntry:
        """Rename a waypoint in the local model."""
        self._validate_index(index)
        current = self._waypoints[index]
        self._waypoints[index] = replace(current, name=name)
        self._refresh_tree(selected_index=index)
        return replace(self._waypoints[index])

    def remove_waypoint(self, index: int) -> WaypointEntry:
        """Remove a waypoint from the local model and return it."""
        self._validate_index(index)
        entry = self._waypoints.pop(index)
        selected_index = min(index, len(self._waypoints) - 1) if self._waypoints else None
        self._refresh_tree(selected_index=selected_index)
        return replace(entry)

    def select_waypoint(self, index: int) -> WaypointEntry:
        """Select a waypoint row and return the selected entry."""
        self._validate_index(index)
        item = self.tree_widget.topLevelItem(index)
        assert item is not None
        self.tree_widget.setCurrentItem(item)
        return replace(self._waypoints[index])

    def selected_waypoint(self) -> WaypointEntry | None:
        """Return the currently selected waypoint, if any."""
        current_item = self.tree_widget.currentItem()
        if current_item is None:
            return None

        index = self.tree_widget.indexOfTopLevelItem(current_item)
        if index < 0 or index >= len(self._waypoints):
            return None
        return replace(self._waypoints[index])

    def _add_default_waypoint(self) -> None:
        """Add a default waypoint placeholder for Tier 2."""
        self.add_waypoint()

    def _rename_selected_waypoint(self) -> None:
        """Rename the currently selected waypoint through a simple prompt."""
        index = self._selected_index()
        if index is None:
            return

        current_name = self._waypoints[index].name
        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Waypoint",
            "Waypoint name:",
            text=current_name,
        )
        if accepted:
            cleaned = new_name.strip()
            if cleaned:
                self.rename_waypoint(index, cleaned)

    def _remove_selected_waypoint(self) -> None:
        """Remove the currently selected waypoint."""
        index = self._selected_index()
        if index is not None:
            self.remove_waypoint(index)

    def _selected_index(self) -> int | None:
        """Return the current top-level selection index."""
        current_item = self.tree_widget.currentItem()
        if current_item is None:
            return None
        index = self.tree_widget.indexOfTopLevelItem(current_item)
        return index if index >= 0 else None

    def _refresh_tree(self, selected_index: int | None = None) -> None:
        """Rebuild the widget rows from the local model."""
        self.tree_widget.blockSignals(True)
        self.tree_widget.clear()

        for entry in self._waypoints:
            item = QTreeWidgetItem(
                [
                    entry.name,
                    self._format_coordinates(entry),
                    self._format_linked_spawn(entry.linked_spawn),
                ]
            )
            item.setFont(0, TYPOGRAPHY.ui_label())
            item.setFont(1, TYPOGRAPHY.coordinate_display())
            item.setFont(2, TYPOGRAPHY.ui_label())
            self.tree_widget.addTopLevelItem(item)

        if (
            selected_index is not None
            and 0 <= selected_index < self.tree_widget.topLevelItemCount()
        ):
            selected_item = self.tree_widget.topLevelItem(selected_index)
            assert selected_item is not None
            self.tree_widget.setCurrentItem(selected_item)
        else:
            self.tree_widget.clearSelection()

        self.tree_widget.blockSignals(False)
        self._sync_action_state()

    def _sync_action_state(self, *_args) -> None:
        """Enable or disable edit actions based on current selection."""
        has_selection = self._selected_index() is not None
        self.btn_rename.setEnabled(has_selection)
        self.btn_remove.setEnabled(has_selection)

    @staticmethod
    def _format_coordinates(entry: WaypointEntry) -> str:
        """Format coordinates using the DESIGN.md zero-padded Z representation."""
        return f"{entry.x}, {entry.y}, {entry.z:02d}"

    @staticmethod
    def _format_linked_spawn(linked_spawn: str | None) -> str:
        """Render linked spawn text for the table."""
        return linked_spawn or ""

    def _validate_index(self, index: int) -> None:
        if index < 0 or index >= len(self._waypoints):
            raise IndexError(f"Waypoint index {index} out of range")
