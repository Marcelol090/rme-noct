"""Brush Palette Doc implementation."""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY


class BrushPaletteDock(GlassDockWidget):
    """The brush palette replacing legacy RME's PaletteWindow.

    Provides tabs for Terrain, Doodads, Items, Creatures, etc.
    Styled with the Noct Map Editor aesthetic.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("BRUSH PALETTE", parent)
        self.setObjectName("brush_palette_dock")
        self.item_palette = None
        self._lists: dict[str, QListWidget] = {}
        self._setup_ui()

    def current_palette(self) -> str:
        return self.tabs.tabText(self.tabs.currentIndex())

    def select_palette(self, name: str) -> bool:
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == name:
                self.tabs.setCurrentIndex(index)
                self._apply_search_to_current_palette(self._search_bar.text())
                return True
        return False

    def focus_item_palette(self, search_text: str = "") -> bool:
        if not self.select_palette("Item"):
            return False
        self._search_bar.setText(search_text)
        return True

    def clear_search(self) -> None:
        self._search_bar.clear()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search brushes")
        self._search_bar.setFont(TYPOGRAPHY.ui_label())
        self._search_bar.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 4px;
                color: {qss_color(THEME.ash_lavender)};
                padding: 8px;
            }}
            QLineEdit:focus {{
                border-color: {qss_color(THEME.amethyst_core)};
            }}
        """)
        self._search_bar.textChanged.connect(self._apply_search_to_current_palette)
        layout.addWidget(self._search_bar)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_palette_changed)
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
        for name in ("Terrain", "Doodads", "Item", "Creature", "RAW"):
            self.tabs.addTab(self._create_brush_list(name), name)

        layout.addWidget(self.tabs)
        self.set_inner_layout(layout)
        self._sync_search_placeholder()

    def _create_brush_list(self, name: str) -> QListWidget:
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
            label = f"{name} Brush {i}"
            if name == "Item":
                label = ("Stone", "Gold Coin", "Dragon Ham")[i - 1] if i <= 3 else f"Item {i}"
            item = QListWidgetItem(label)
            list_widget.addItem(item)

        self._lists[name] = list_widget
        return list_widget

    def _apply_search_to_current_palette(self, text: str) -> None:
        current = self.current_palette()
        if current == "Item" and self.item_palette is not None and hasattr(
            self.item_palette, "set_search_text"
        ):
            self.item_palette.set_search_text(text)
            return
        list_widget = self._lists.get(current)
        if list_widget is None:
            return
        needle = text.strip().casefold()
        for row in range(list_widget.count()):
            item = list_widget.item(row)
            item.setHidden(bool(needle) and needle not in item.text().casefold())

    def _sync_search_placeholder(self) -> None:
        if self.current_palette() == "Item":
            self._search_bar.setPlaceholderText("Search items")
        else:
            self._search_bar.setPlaceholderText("Search brushes")

    def _on_palette_changed(self, _index: int) -> None:
        self._sync_search_placeholder()
        self._apply_search_to_current_palette(self._search_bar.text())
