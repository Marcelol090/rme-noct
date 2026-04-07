"""Reusable QSS contracts aligned with `.stitch/DESIGN.md`."""

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

from pyrme.ui.theme import THEME

if TYPE_CHECKING:
    from PyQt6.QtGui import QColor


def qss_color(color: QColor) -> str:
    """Serialize colors for Qt stylesheets without losing alpha channels."""
    if color.alpha() == 255:
        return color.name()
    return (
        f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
    )


def _join_qss(*blocks: str) -> str:
    return "\n".join(
        dedent(block).strip()
        for block in blocks
        if block and dedent(block).strip()
    )


def dialog_base_qss(control_selectors: str | None = None) -> str:
    """Return the shared Tier 2 dialog chrome and optional form control styles."""
    input_surface = "rgba(255, 255, 255, 15)"
    blocks = [
        f"""
        QDialog {{
            background-color: {qss_color(THEME.void_black)};
            color: {qss_color(THEME.moonstone_white)};
        }}
        QLabel {{
            color: {qss_color(THEME.moonstone_white)};
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            background: transparent;
        }}
        """,
    ]
    if control_selectors:
        blocks.append(
            f"""
            {control_selectors} {{
                background-color: {input_surface};
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 4px;
                color: {qss_color(THEME.moonstone_white)};
                padding: 4px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }}
            {control_selectors}:focus {{
                border: 1px solid {qss_color(THEME.focus_border)};
                background-color: {qss_color(THEME.lifted_glass)};
            }}
            """
        )
    return _join_qss(*blocks)


def section_heading_qss() -> str:
    """Return the uppercase dock-style section heading contract."""
    return _join_qss(
        f"""
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: {qss_color(THEME.ash_lavender)};
        """
    )


def secondary_label_qss() -> str:
    """Return the secondary-label text color contract."""
    return f"color: {qss_color(THEME.ash_lavender)};"


def group_box_qss() -> str:
    """Return the shared group box contract used in dense dialogs."""
    return _join_qss(
        f"""
        QGroupBox {{
            border: 1px solid {qss_color(THEME.ghost_border)};
            border-radius: 4px;
            margin-top: 12px;
            padding: 8px 8px 4px 8px;
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: {qss_color(THEME.ash_lavender)};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            padding: 0 6px;
            color: {qss_color(THEME.ash_lavender)};
        }}
        """
    )


def checkbox_qss() -> str:
    """Return the shared checkbox contract used in filter panels."""
    return _join_qss(
        f"""
        QCheckBox {{
            spacing: 6px;
            color: {qss_color(THEME.moonstone_white)};
            font-family: 'Inter', sans-serif;
            font-size: 12px;
        }}
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
            border: 1px solid {qss_color(THEME.ghost_border)};
        }}
        QCheckBox::indicator:checked {{
            background-color: {qss_color(THEME.amethyst_core)};
            border-color: {qss_color(THEME.amethyst_core)};
        }}
        """
    )


def item_view_qss(widget_selector: str, *, include_header: bool = False) -> str:
    """Return the shared list/tree selected-row accent contract."""
    blocks = [
        f"""
        {widget_selector} {{
            background-color: {qss_color(THEME.obsidian_glass)};
            border: 1px solid {qss_color(THEME.ghost_border)};
            border-radius: 4px;
            color: {qss_color(THEME.moonstone_white)};
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            outline: none;
        }}
        {widget_selector}::item {{
            padding: 4px 0;
            border-left: 3px solid transparent;
            min-height: 24px;
        }}
        {widget_selector}::item:selected {{
            background-color: {qss_color(THEME.lifted_glass)};
            border-left: 3px solid {qss_color(THEME.amethyst_core)};
            color: {qss_color(THEME.moonstone_white)};
        }}
        {widget_selector}::item:hover {{
            background-color: {qss_color(THEME.lifted_glass)};
        }}
        """
    ]
    if include_header:
        blocks.append(
            f"""
            QHeaderView::section {{
                background-color: transparent;
                color: {qss_color(THEME.ash_lavender)};
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-bottom: 1px solid {qss_color(THEME.ghost_border)};
                padding: 4px 8px;
                text-transform: uppercase;
            }}
            """
        )
    return _join_qss(*blocks)


def ghost_button_qss() -> str:
    """Return the shared ghost button contract."""
    return _join_qss(
        f"""
        QPushButton {{
            background: none;
            border: 1px solid {qss_color(THEME.ghost_border)};
            border-radius: 6px;
            color: {qss_color(THEME.ash_lavender)};
            padding: 6px 16px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {qss_color(THEME.lifted_glass)};
            border: 1px solid {qss_color(THEME.active_border)};
            color: {qss_color(THEME.moonstone_white)};
        }}
        QPushButton:checked {{
            background-color: {qss_color(THEME.lifted_glass)};
            border: 1px solid {qss_color(THEME.focus_border)};
            color: {qss_color(THEME.moonstone_white)};
        }}
        QPushButton:disabled {{
            color: {qss_color(THEME.muted_slate)};
            border: 1px solid {qss_color(THEME.ghost_border)};
        }}
        """
    )


def primary_button_qss() -> str:
    """Return the shared amethyst CTA button contract."""
    return _join_qss(
        f"""
        QPushButton {{
            background-color: {qss_color(THEME.amethyst_core)};
            border: none;
            border-radius: 6px;
            color: {qss_color(THEME.moonstone_white)};
            padding: 6px 16px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {qss_color(THEME.deep_amethyst)};
        }}
        """
    )


def destructive_button_qss() -> str:
    """Return the shared destructive button contract."""
    return _join_qss(
        f"""
        QPushButton {{
            background: none;
            color: {qss_color(THEME.ember_red)};
            border: 1px solid {qss_color(THEME.ember_red)};
            border-radius: 4px;
            padding: 4px 8px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: rgba(224, 92, 92, 38);
            border: 1px solid {qss_color(THEME.ember_red)};
            color: {qss_color(THEME.moonstone_white)};
        }}
        QPushButton:disabled {{
            color: {qss_color(THEME.muted_slate)};
            border: 1px solid {qss_color(THEME.ghost_border)};
        }}
        """
    )


def subtle_action_qss() -> str:
    """Return the shared quiet inline action style used in dialogs."""
    return _join_qss(
        f"""
        QPushButton {{
            background: none;
            border: none;
            color: {qss_color(THEME.ash_lavender)};
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            padding: 2px 4px;
            text-align: left;
        }}
        QPushButton:hover {{
            color: {qss_color(THEME.moonstone_white)};
        }}
        """
    )


def position_chip_qss() -> str:
    """Return the recent-position chip button contract."""
    return _join_qss(
        f"""
        QPushButton {{
            background: none;
            border: 1px solid {qss_color(THEME.ghost_border)};
            border-radius: 12px;
            color: {qss_color(THEME.ash_lavender)};
            padding: 3px 10px;
            font-size: 11px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {qss_color(THEME.lifted_glass)};
            border-color: {qss_color(THEME.active_border)};
            color: {qss_color(THEME.moonstone_white)};
        }}
        """
    )
