"""Waypoints Dock.

Manages map waypoints with coordinate display in JetBrains Mono
and Noct Map Editor glassmorphism styling.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.theme import THEME, TYPOGRAPHY


class WaypointsDock(GlassDockWidget):
    """Dock widget to manage waypoints.

    Displays waypoint name and coordinates (JetBrains Mono),
    with Add/Remove controls and amethyst accent on selection.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Waypoints", parent)
        self.setObjectName("WaypointsDock")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the dock UI within the GlassPanel container."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # QTreeWidget with Name + Coordinates columns
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Position"])
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setRootIsDecorated(False)
        self.tree_widget.setAlternatingRowColors(False)
        self.tree_widget.setIndentation(0)

        # Set header font
        header = self.tree_widget.header()
        if header is not None:
            header.setFont(TYPOGRAPHY.dock_title())
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(1, 140)

        # DESIGN.md-aligned styling with amethyst left accent bar on selection
        self.tree_widget.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {THEME.obsidian_glass.name()};
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 4px 0;
                border-left: 3px solid transparent;
                min-height: 24px;
            }}
            QTreeWidget::item:selected {{
                background-color: {THEME.lifted_glass.name()};
                border-left: 3px solid {THEME.amethyst_core.name()};
                color: {THEME.moonstone_white.name()};
            }}
            QTreeWidget::item:hover {{
                background-color: {THEME.lifted_glass.name()};
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {THEME.ash_lavender.name()};
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-bottom: 1px solid {THEME.ghost_border.name()};
                padding: 4px 8px;
                text-transform: uppercase;
            }}
        """)

        # Populate with dummy waypoints (like legacy RME)
        dummy_points = [
            ("Temple", "32000, 32000, 07"),
            ("Depot", "32050, 32100, 07"),
            ("Dragon Lair", "32200, 31800, 08"),
        ]
        for name, pos in dummy_points:
            item = QTreeWidgetItem([name, pos])
            # Name column: Inter (default)
            # Position column: JetBrains Mono
            item.setFont(1, TYPOGRAPHY.coordinate_display())
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.tree_widget.addTopLevelItem(item)

        layout.addWidget(self.tree_widget)

        # Action buttons row
        action_layout = QHBoxLayout()
        action_layout.setSpacing(4)

        self.btn_add = QPushButton("Add")
        self.btn_remove = QPushButton("Remove")

        # Ghost button style (secondary action)
        ghost_style = f"""
            QPushButton {{
                background: none;
                color: {THEME.ash_lavender.name()};
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                padding: 4px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {THEME.lifted_glass.name()};
                border: 1px solid {THEME.active_border.name()};
                color: {THEME.moonstone_white.name()};
            }}
        """
        self.btn_add.setStyleSheet(ghost_style)

        # Destructive button style (Ember Red per DESIGN.md)
        self.btn_remove.setStyleSheet(f"""
            QPushButton {{
                background: none;
                color: {THEME.ember_red.name()};
                border: 1px solid {THEME.ember_red.name()};
                border-radius: 4px;
                padding: 4px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(224, 92, 92, 38);
                border: 1px solid {THEME.ember_red.name()};
                color: {THEME.moonstone_white.name()};
            }}
        """)

        action_layout.addWidget(self.btn_add)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_remove)

        layout.addLayout(action_layout)

        # Use the GlassDockWidget's container
        self.set_inner_layout(layout)
