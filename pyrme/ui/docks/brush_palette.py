"""Brush Palette Dock – virtual model, instant search.

Replaces legacy QListWidget with QListView + QAbstractListModel
to handle 50k+ brush items without freezing the UI.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QSize,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QLineEdit,
    QListView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.components.glass import GlassDockWidget
from pyrme.ui.docks.item_palette import ItemPaletteWidget
from pyrme.ui.theme import THEME, TYPOGRAPHY


# ── Virtual Model ──────────────────────────────────────────────
class VirtualBrushModel(QAbstractListModel):
    """Flat list model – serves data on demand, no widget per row."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._names: list[str] = []

    # ── public API ────────────────────────────────────────────
    def load_names(self, names: list[str]) -> None:
        """Bulk-replace the backing list (resets the view)."""
        self.beginResetModel()
        self._names = names
        self.endResetModel()

    # ── QAbstractListModel contract ───────────────────────────
    def rowCount(  # noqa: N802
        self, parent: QModelIndex | None = None,
    ) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._names)

    def data(
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._names[index.row()]
        return None


# ── Dock ───────────────────────────────────────────────────────
class BrushPaletteDock(GlassDockWidget):
    """Brush palette with tabbed categories and instant search.

    Uses QListView + VirtualBrushModel for O(1) scroll perf.
    """

    item_selected = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("PALETTE", parent)
        self.setObjectName("brush_palette_dock")

        self._models: dict[str, VirtualBrushModel] = {}
        self._proxies: dict[str, QSortFilterProxyModel] = {}
        self._views: dict[str, QListView] = {}

        self._setup_ui()

    # ── layout ────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        root = QVBoxLayout()
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # Search bar
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search brushes…")
        self._search_bar.setClearButtonEnabled(True)
        self._search_bar.setFont(TYPOGRAPHY.ui_label(11))
        self._search_bar.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                padding: 6px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border-color: {THEME.amethyst_core.name()};
            }}
        """)
        self._search_bar.textChanged.connect(self._on_search_changed)
        root.addWidget(self._search_bar)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self._tabs_qss())
        self.tabs.currentChanged.connect(self._sync_filter_to_active_tab)

        for name in self.palette_names():
            if name == "Item":
                self._item_palette = ItemPaletteWidget(self)
                self._item_palette.setObjectName("Item")
                self._item_palette.load_items(self._initial_item_catalog())
                self._item_palette.item_selected.connect(self.item_selected)
                self.tabs.addTab(self._item_palette, name)
            else:
                view = self._create_brush_view(name)
                self.tabs.addTab(view, name)

        root.addWidget(self.tabs)
        self.set_inner_layout(root)

    # ── palette names ─────────────────────────────────────────
    @staticmethod
    def palette_names() -> tuple[str, ...]:
        return (
            "Terrain",
            "Doodad",
            "Item",
            "Collection",
            "House",
            "Creature",
            "Waypoint",
            "RAW",
        )

    # ── tab helpers ───────────────────────────────────────────
    def select_palette(self, name: str) -> bool:
        """Switch to named palette tab."""
        child = self.tabs.findChild(QWidget, name)
        if child is not None:
            idx = self.tabs.indexOf(child)
            if idx >= 0:
                self.tabs.setCurrentIndex(idx)
                return True
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i).casefold() == name.casefold():
                self.tabs.setCurrentIndex(i)
                return True
        return False

    def current_palette(self) -> str:
        return self.tabs.tabText(self.tabs.currentIndex())

    def focus_item_palette(self, search_text: str = "") -> None:
        """Switch to Item palette and optionally narrow the search surface."""
        self.select_palette("Item")
        if search_text:
            self._search_bar.setText(search_text)
        else:
            self._search_bar.clear()

    def focus_palette(self, name: str, search_text: str = "") -> bool:
        """Switch to a palette and replace the shared search state."""
        if not self.select_palette(name):
            return False
        if search_text:
            self._search_bar.setText(search_text)
        else:
            self._search_bar.clear()
        return True

    @property
    def item_palette(self) -> ItemPaletteWidget | None:
        """Public access to the ItemPaletteWidget for external data loading."""
        return getattr(self, "_item_palette", None)

    # ── data factory ─────────────────────────────────────────
    @staticmethod
    def _initial_item_catalog() -> list:
        """Seed items for dev/preview. Replace with real asset loader."""
        from pyrme.ui.models.item_palette_types import ItemEntry

        named = [
            ItemEntry(1, "Stone", category="Ground"),
            ItemEntry(2, "Sword", category="Weapons"),
            ItemEntry(3, "Shield", category="Armor"),
            ItemEntry(2112, "Large Trunk", category="Decoration"),
            ItemEntry(3264, "Gold Coin", category="Currency"),
            ItemEntry(101, "Grass", category="Ground"),
        ]
        synthetic = [
            ItemEntry(i, f"Mock Item {i}", category="Misc")
            for i in range(200, 250)
        ]
        return named + synthetic

    # ── view factory ──────────────────────────────────────────
    def _create_brush_view(self, palette_name: str) -> QListView:
        model = VirtualBrushModel(self)
        # Seed with placeholder items (real data comes from asset loader)
        model.load_names([f"{palette_name} Brush {i}" for i in range(1, 21)])

        proxy = QSortFilterProxyModel(self)
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        proxy.setFilterRole(Qt.ItemDataRole.DisplayRole)

        view = QListView()
        view.setObjectName(palette_name)
        view.setModel(proxy)
        view.setFrameShape(QListView.Shape.NoFrame)
        view.setFont(TYPOGRAPHY.ui_label())
        view.setIconSize(QSize(32, 32))
        view.setUniformItemSizes(True)  # perf: skip per-item size hint
        view.setStyleSheet(self._list_qss())

        self._models[palette_name] = model
        self._proxies[palette_name] = proxy
        self._views[palette_name] = view
        return view

    # ── search ────────────────────────────────────────────────
    def _on_search_changed(self, text: str) -> None:
        palette = self.current_palette()
        if palette == "Item" and hasattr(self, "_item_palette"):
            self._item_palette.set_search_text(text)
        else:
            proxy = self._proxies.get(palette)
            if proxy:
                proxy.setFilterFixedString(text)

    def _sync_filter_to_active_tab(self, _index: int) -> None:
        """Re-apply current search text when tab changes."""
        text = self._search_bar.text()
        if text:
            self._on_search_changed(text)

    # ── stylesheets ───────────────────────────────────────────
    def _tabs_qss(self) -> str:
        return f"""
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
        """

    @staticmethod
    def _list_qss() -> str:
        return f"""
            QListView {{
                background: transparent;
                outline: none;
                color: {THEME.ash_lavender.name()};
            }}
            QListView::item {{
                padding: 8px;
                border-bottom: 1px solid {THEME.ghost_border.name()};
            }}
            QListView::item:selected {{
                background-color: {THEME.amethyst_core.name()};
                color: #ffffff;
                border-radius: 2px;
            }}
            QListView::item:hover:!selected {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
        """
