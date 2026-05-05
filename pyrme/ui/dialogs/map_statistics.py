"""Map Statistics Dialog.

Follows the Noct Map Editor Design System (DESIGN.md) for glassmorphic styling.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles import (
    dialog_base_qss,
    ghost_button_qss,
    primary_button_qss,
    qss_color,
)
from pyrme.ui.theme import THEME, TYPOGRAPHY


class StatCard(QFrame):
    """A glassmorphic card for displaying a group of statistics."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {qss_color(THEME.obsidian_glass)};
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 12px;
            }}
        """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title.upper())
        self.title_label.setFont(TYPOGRAPHY.ui_label(11, 700))
        self.title_label.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        layout.addWidget(self.title_label)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        layout.addLayout(self.grid)
        self.row = 0

    def add_stat(self, label: str, value: str) -> QLabel:
        lbl = QLabel(label)
        lbl.setFont(TYPOGRAPHY.ui_label(12))
        lbl.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")

        val = QLabel(value)
        val.setFont(TYPOGRAPHY.code_label(13, 600))
        val.setStyleSheet(f"color: {qss_color(THEME.moonstone_white)};")
        val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.grid.addWidget(lbl, self.row, 0)
        self.grid.addWidget(val, self.row, 1)
        self.row += 1
        return val


class MapStatisticsDialog(QDialog):
    """Dashboard for displaying map statistics aggregated from Rust core."""

    DIALOG_SIZE = QSize(640, 520)

    def __init__(
        self,
        parent: QWidget | None = None,
        shell_state=None,
        *,
        statistics=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Map Statistics")
        self.setFixedSize(self.DIALOG_SIZE)
        self._shell_state = shell_state
        self._statistics = statistics

        self._apply_dialog_style()
        self._build_layout()
        self.refresh_stats()

    def _apply_dialog_style(self) -> None:
        self.setStyleSheet(dialog_base_qss())

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        heading = QLabel("Map Statistics")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Section 1: Environment
        self.env_card = StatCard("Environment")
        self.tile_count = self.env_card.add_stat("Tile Count:", "0")
        self.item_count = self.env_card.add_stat("Item Count:", "0")
        self.blocking_tiles = self.env_card.add_stat("Blocking Tiles:", "0")
        self.walkable_tiles = self.env_card.add_stat("Walkable Tiles:", "0")
        grid.addWidget(self.env_card, 0, 0)

        # Section 2: Population
        self.pop_card = StatCard("Population")
        self.spawn_count = self.pop_card.add_stat("Spawn Count:", "0")
        self.creature_count = self.pop_card.add_stat("Creature Count:", "0")
        self.waypoint_count = self.pop_card.add_stat("Waypoints:", "0")
        grid.addWidget(self.pop_card, 0, 1)

        # Section 3: Treasury
        self.treasury_card = StatCard("Treasury")
        self.house_count = self.treasury_card.add_stat("House Count:", "0")
        self.house_sqm = self.treasury_card.add_stat("Total House SQM:", "0")
        self.town_count = self.treasury_card.add_stat("Towns:", "0")
        grid.addWidget(self.treasury_card, 1, 0)

        # Section 4: Civics
        self.civics_card = StatCard("Civics")
        self.pathable_perc = self.civics_card.add_stat("Pathable Tiles:", "0%")
        self.sqm_per_house = self.civics_card.add_stat("Avg SQM / House:", "0")
        grid.addWidget(self.civics_card, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(ghost_button_qss())
        self.close_btn.clicked.connect(self.accept)
        footer.addWidget(self.close_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(primary_button_qss())
        self.refresh_btn.clicked.connect(self.refresh_stats)
        footer.addWidget(self.refresh_btn)

        layout.addLayout(footer)

    def refresh_stats(self) -> None:
        if self._statistics is not None:
            stats = self._statistics
        elif self._shell_state:
            stats = self._shell_state.collect_statistics()
        else:
            return

        if not stats:
            return

        self.tile_count.setText(f"{stats.tile_count:,}")
        self.item_count.setText(f"{stats.item_count:,}")
        self.blocking_tiles.setText(f"{stats.blocking_tile_count:,}")
        self.walkable_tiles.setText(f"{stats.walkable_tile_count:,}")

        self.spawn_count.setText(f"{stats.spawn_count:,}")
        self.creature_count.setText(f"{stats.creature_count:,}")
        self.waypoint_count.setText(f"{stats.waypoint_count:,}")

        self.house_count.setText(f"{stats.house_count:,}")
        self.house_sqm.setText(f"{stats.total_house_sqm:,}")
        self.town_count.setText(f"{stats.town_count:,}")

        pathable = stats.walkable_tile_count / stats.tile_count * 100 if stats.tile_count > 0 else 0
        self.pathable_perc.setText(f"{pathable:.1f}%")

        avg_sqm = stats.total_house_sqm / stats.house_count if stats.house_count > 0 else 0
        self.sqm_per_house.setText(f"{avg_sqm:.1f}")
