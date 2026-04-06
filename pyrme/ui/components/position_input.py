"""Reusable position input widget for Noct Map Editor.

Ported from legacy C++ PositionCtrl (ui/positionctrl.h/.cpp).
Composite widget with X, Y, Z coordinate fields.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QWidget,
)

from pyrme.ui.theme import THEME, TYPOGRAPHY

# Floor labels matching Tibia convention (DESIGN.md §7: Floor 7 = Ground)
_FLOOR_LABELS: list[str] = [
    "0 (Roof)",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7 (Ground)",
    "8 (Underground)",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15 (Deep)",
]

# Legacy C++ defaults from positionctrl.h
MAP_MAX_WIDTH = 65000
MAP_MAX_HEIGHT = 65000
MAP_MAX_LAYER = 15
GROUND_LAYER = 7


class PositionInput(QWidget):
    """Composite coordinate input: X, Y (QSpinBox) + Z (QComboBox).

    Emits ``position_changed(x, y, z)`` whenever any field value changes.
    Uses JetBrains Mono 14px for coordinate values per DESIGN.md §3.
    Z is always a dropdown (never free text) per DESIGN.md §4.
    """

    position_changed = pyqtSignal(int, int, int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        x: int = 32000,
        y: int = 32000,
        z: int = GROUND_LAYER,
        max_x: int = MAP_MAX_WIDTH,
        max_y: int = MAP_MAX_HEIGHT,
    ) -> None:
        super().__init__(parent)
        self._build_ui(x, y, z, max_x, max_y)

    def _build_ui(
        self, x: int, y: int, z: int, max_x: int, max_y: int
    ) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        coord_font = TYPOGRAPHY.coordinate_display(large=True)
        label_style = (
            f"color: {THEME.ash_lavender.name()}; "
            "font-family: 'Inter', sans-serif; font-size: 11px;"
        )
        spinbox_style = f"""
            QSpinBox {{
                background-color: rgba(255,255,255,15);
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                padding: 4px 8px;
                min-width: 70px;
            }}
            QSpinBox:focus {{
                border: 1px solid {THEME.focus_border.name()};
            }}
        """
        combo_style = f"""
            QComboBox {{
                background-color: rgba(255,255,255,15);
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                padding: 4px 8px;
                min-width: 90px;
            }}
            QComboBox:focus {{
                border: 1px solid {THEME.focus_border.name()};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {THEME.void_black.name()};
                color: {THEME.moonstone_white.name()};
                border: 1px solid {THEME.ghost_border.name()};
                selection-background-color: {THEME.amethyst_core.name()};
            }}
        """

        # X field
        lbl_x = QLabel("X:")
        lbl_x.setStyleSheet(label_style)
        layout.addWidget(lbl_x)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, max_x)
        self.x_spin.setValue(x)
        self.x_spin.setFont(coord_font)
        self.x_spin.setStyleSheet(spinbox_style)
        self.x_spin.setToolTip("X coordinate (0–65000)")
        self.x_spin.valueChanged.connect(self._emit_position)
        layout.addWidget(self.x_spin)

        # Y field
        lbl_y = QLabel("Y:")
        lbl_y.setStyleSheet(label_style)
        layout.addWidget(lbl_y)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, max_y)
        self.y_spin.setValue(y)
        self.y_spin.setFont(coord_font)
        self.y_spin.setStyleSheet(spinbox_style)
        self.y_spin.setToolTip("Y coordinate (0–65000)")
        self.y_spin.valueChanged.connect(self._emit_position)
        layout.addWidget(self.y_spin)

        # Z field (dropdown, NEVER free text — DESIGN.md §4)
        lbl_z = QLabel("Z:")
        lbl_z.setStyleSheet(label_style)
        layout.addWidget(lbl_z)

        self.z_combo = QComboBox()
        self.z_combo.addItems(_FLOOR_LABELS)
        self.z_combo.setCurrentIndex(z)
        self.z_combo.setFont(coord_font)
        self.z_combo.setStyleSheet(combo_style)
        self.z_combo.setToolTip("Floor level (0=Roof, 7=Ground, 15=Deep)")
        self.z_combo.currentIndexChanged.connect(self._emit_position)
        layout.addWidget(self.z_combo)

    # ── Public API (mirrors legacy C++ PositionCtrl) ──

    def get_x(self) -> int:
        """Return current X value."""
        return self.x_spin.value()

    def get_y(self) -> int:
        """Return current Y value."""
        return self.y_spin.value()

    def get_z(self) -> int:
        """Return current Z (floor) value."""
        return self.z_combo.currentIndex()

    def get_position(self) -> tuple[int, int, int]:
        """Return (x, y, z) tuple."""
        return (self.get_x(), self.get_y(), self.get_z())

    def set_position(self, x: int, y: int, z: int) -> None:
        """Set all three coordinate values."""
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.z_combo.blockSignals(True)

        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
        self.z_combo.setCurrentIndex(z)

        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.z_combo.blockSignals(False)

        self._emit_position()

    # ── Internal ──

    def _emit_position(self) -> None:
        self.position_changed.emit(self.get_x(), self.get_y(), self.get_z())
