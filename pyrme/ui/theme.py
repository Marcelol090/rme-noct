"""Noct Map Editor - Design Theme Schema.

This module provides the color tokens and typography rules as defined
in the .stitch/DESIGN.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QColor, QFont


@dataclass
class ColorTokens:
    """Color tokens for the Noct Map Editor design system."""

    # Base Surfaces
    void_black = QColor("#1e2227")
    obsidian_glass = QColor(255, 255, 255, int(255 * 0.04))
    lifted_glass = QColor(255, 255, 255, int(255 * 0.07))
    elevated_surface = QColor(255, 255, 255, int(255 * 0.09))

    # Accent & Interactive
    amethyst_core = QColor("#1793d1")
    deep_amethyst = QColor("#116b99")
    amethyst_glow = QColor(23, 147, 209, int(255 * 0.15))
    amethyst_rim = QColor(23, 147, 209, int(255 * 0.5))

    # Text
    moonstone_white = QColor("#E8E6F0")
    ash_lavender = QColor("#9490A8")
    muted_slate = QColor("#4A4860")

    # Borders & Dividers
    ghost_border = QColor(255, 255, 255, int(255 * 0.08))
    active_border = QColor(255, 255, 255, int(255 * 0.14))
    focus_border = QColor(23, 147, 209, int(255 * 0.8))

    # Semantic Status
    ember_red = QColor("#E05C5C")
    verdant_green = QColor("#5CBF8A")
    amber_caution = QColor("#D4A847")
    steel_blue = QColor("#5B8ECC")

@dataclass
class TypographyTokens:
    """Typography tokens for the Noct Map Editor design system."""

    @staticmethod
    def _create_font(family: str, size: int, weight: int = QFont.Weight.Normal) -> QFont:
        font = QFont(family, size)
        font.setWeight(weight)
        return font

    @classmethod
    def ui_label(cls, size: int = 12, weight: int = QFont.Weight.Normal) -> QFont:
        return cls._create_font("Inter", size, weight)

    @classmethod
    def code_label(cls, size: int = 12, weight: int = QFont.Weight.Normal) -> QFont:
        return cls._create_font("JetBrains Mono", size, weight)

    @classmethod
    def dialog_heading(cls) -> QFont:
        return cls.ui_label(14, QFont.Weight.DemiBold)

    @classmethod
    def dock_title(cls) -> QFont:
        f = cls.ui_label(11, QFont.Weight.DemiBold)
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 108) # 0.08em -> roughly 108%
        return f

    @classmethod
    def coordinate_display(cls, large: bool = False) -> QFont:
        return cls.code_label(14 if large else 12)

    @classmethod
    def item_id(cls) -> QFont:
        return cls.code_label(11)

THEME = ColorTokens()
TYPOGRAPHY = TypographyTokens()
