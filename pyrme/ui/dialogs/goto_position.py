"""Jump to Position Dialog for Noct Map Editor.

Ported from legacy C++ GotoPositionDialog (ui/dialogs/goto_position_dialog.cpp).
Uses the reusable PositionInput component for X/Y/Z coordinate entry.
Recent positions persisted via QSettings (group: recent_positions, max 5, FIFO).
"""

from __future__ import annotations

import json

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.position_input import PositionInput
from pyrme.ui.styles import (
    dialog_base_qss,
    ghost_button_qss,
    position_chip_qss,
    primary_button_qss,
    section_heading_qss,
    subtle_action_qss,
)
from pyrme.ui.theme import TYPOGRAPHY

# Max recent positions to keep (FIFO)
_MAX_RECENT = 5


class GotoPositionDialog(QDialog):
    """Dialog to jump to a specific map position.

    Mirrors legacy C++ GotoPositionDialog with:
    - X, Y, Z coordinate inputs via PositionInput
    - Recent positions list (5, persisted via QSettings)
    - Ghost Cancel + Amethyst Jump CTA buttons
    """

    # DESIGN.md: Jump to Position = 340 × 220px
    DIALOG_SIZE = QSize(340, 280)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Go To Position")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._settings = QSettings("Noct Map Editor", "Noct")
        self._apply_dialog_style()
        self._build_layout()
        self._load_recent_positions()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Elevation 3 dialog styling."""
        self.setStyleSheet(dialog_base_qss())

    def _build_layout(self) -> None:
        """Construct the dialog layout matching legacy C++ GotoPositionDialog."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Dialog heading (DESIGN.md: Inter 14px weight 600 Moonstone White)
        heading = QLabel("Go To Position")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        # Position input (reusable component)
        self.position_input = PositionInput(self)
        layout.addWidget(self.position_input)

        # Recent positions section
        self.recent_header = QLabel("RECENT POSITIONS")
        self.recent_header.setFont(TYPOGRAPHY.dock_title())
        self.recent_header.setStyleSheet(section_heading_qss())
        layout.addWidget(self.recent_header)

        # Recent position chips container
        self._recent_container = QVBoxLayout()
        self._recent_container.setSpacing(4)
        layout.addLayout(self._recent_container)

        # Clear recent button
        self._clear_btn = QPushButton("Clear Recent")
        self._clear_btn.setStyleSheet(subtle_action_qss())
        self._clear_btn.clicked.connect(self._clear_recent)
        self._clear_btn.setVisible(False)
        layout.addWidget(self._clear_btn)

        layout.addStretch()

        # Footer: Ghost Cancel + Amethyst Jump CTA
        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setToolTip("Close this window")
        cancel_btn.setStyleSheet(ghost_button_qss())
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        jump_btn = QPushButton("Jump")
        jump_btn.setToolTip("Go to position (Enter)")
        jump_btn.setStyleSheet(primary_button_qss())
        jump_btn.setDefault(True)
        jump_btn.clicked.connect(self._on_jump)
        footer.addWidget(jump_btn)

        layout.addLayout(footer)

    # ── Recent positions ──

    def _load_recent_positions(self) -> None:
        """Load recent positions from QSettings."""
        raw = self._settings.value("recent_positions/list", "[]")
        try:
            parsed = json.loads(str(raw))
            self._recent: list[tuple[int, int, int]] = []
            for p in parsed:
                if not isinstance(p, list) or len(p) != 3:
                    raise ValueError("Invalid format")
                if not all(isinstance(x, int) for x in p):
                    raise TypeError("Expected ints")
                self._recent.append(tuple(p))
        except (json.JSONDecodeError, TypeError, ValueError):
            self._recent = []
        self._rebuild_recent_chips()

    def _save_recent_positions(self) -> None:
        """Persist recent positions to QSettings."""
        self._settings.setValue(
            "recent_positions/list", json.dumps(self._recent)
        )

    def _add_recent(self, x: int, y: int, z: int) -> None:
        """Add a position to recent list (FIFO, max 5)."""
        pos = (x, y, z)
        # Remove duplicate if exists
        if pos in self._recent:
            self._recent.remove(pos)
        self._recent.insert(0, pos)
        # Enforce max size
        self._recent = self._recent[:_MAX_RECENT]
        self._save_recent_positions()
        self._rebuild_recent_chips()

    def _clear_recent(self) -> None:
        """Clear all recent positions."""
        self._recent = []
        self._save_recent_positions()
        self._rebuild_recent_chips()

    def _rebuild_recent_chips(self) -> None:
        """Rebuild the recent position chip buttons."""
        # Clear existing
        while self._recent_container.count():
            item = self._recent_container.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()

        for pos in self._recent:
            x, y, z = pos
            chip = QPushButton(f"{x}, {y}, {z:02d}")
            chip.setFont(TYPOGRAPHY.item_id())
            chip.setStyleSheet(position_chip_qss())
            chip.clicked.connect(
                lambda checked, px=x, py=y, pz=z: self._select_recent(px, py, pz)
            )
            self._recent_container.addWidget(chip)

        self._clear_btn.setVisible(len(self._recent) > 0)

    def _select_recent(self, x: int, y: int, z: int) -> None:
        """Apply a recent position to the input fields."""
        self.position_input.set_position(x, y, z)

    # ── Actions ──

    def _on_jump(self) -> None:
        """Handle Jump button click."""
        x, y, z = self.position_input.get_position()
        self._add_recent(x, y, z)
        self.accept()

    def get_position(self) -> tuple[int, int, int]:
        """Return the selected position after dialog closes."""
        return self.position_input.get_position()
