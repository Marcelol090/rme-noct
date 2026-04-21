"""Brush Palette Doc implementation."""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.theme import THEME, TYPOGRAPHY


class BrushPaletteDock(GlassDockWidget):
    """The brush palette replacing legacy RME's PaletteWindow.

    Provides tabs for Terrain, Doodads, Items, Creatures, etc.
    Styled with the Noct Map Editor aesthetic.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("BRUSH PALETTE", parent)
        self.setObjectName("brush_palette_dock")
        self._setup_ui()

    def current_palette(self) -> str:
        return self.tabs.tabText(self.tabs.currentIndex())

    def select_palette(self, name: str) -> bool:
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == name:
                self.tabs.setCurrentIndex(index)
                return True
        return False

    def clear_search(self) -> None:
        """No-op until the shared brush search bar lands in the dock."""
        return

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()
        # QTabWidget styling for Noct Glassmorphism
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {THEME.ghost_border.name()};
                background: transparent;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {THEME.ash_lavender.name()};
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                padding: 6px 12px;
                border: 1px solid transparent;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: #FFFFFF;
                border-bottom: 2px solid {THEME.amethyst_core.name()};
            }}
            QTabBar::tab:hover {{
                background: rgba(255, 255, 255, 0.05);
            }}
        """)

        # Add basic tabs like legacy PaletteWindow
        self.tabs.addTab(self._create_brush_list(), "Terrain")
        self.tabs.addTab(self._create_brush_list(), "Doodads")
        self.tabs.addTab(self._create_brush_list(), "Item")
        self.tabs.addTab(self._create_brush_list(), "Creature")
        self.tabs.addTab(self._create_brush_list(), "RAW")

        layout.addWidget(self.tabs)
        self.set_inner_layout(layout)

    def _create_brush_list(self) -> QListWidget:
        """Create a styled QListWidget for brushes."""
        list_widget = QListWidget()
        list_widget.setFrameShape(QListWidget.Shape.NoFrame)
        list_widget.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                outline: none;
                color: {THEME.ash_lavender.name()};
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {THEME.ghost_border.name()};
            }}
            QListWidget::item:selected {{
                background-color: {THEME.amethyst_core.name()};
                color: #ffffff;
                border-radius: 2px;
            }}
            QListWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
        """)
        list_widget.setFont(TYPOGRAPHY.ui_label())
        list_widget.setIconSize(QSize(32, 32))

        # Mock items for now
        for i in range(1, 21):
            item = QListWidgetItem(f"Brush Item {i}")
            list_widget.addItem(item)

        return list_widget
