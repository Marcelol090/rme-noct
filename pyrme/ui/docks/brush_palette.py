"""Brush palette dock implementation."""

from __future__ import annotations

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
from pyrme.ui.models.brush_catalog import (
    BrushPaletteEntry,
    default_brush_palette_entries,
    entries_by_palette,
)
from pyrme.ui.models.item_palette_types import ItemEntry
from pyrme.ui.styles import input_field_qss, item_view_qss, qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY

_ROOT_INDEX = QModelIndex()


class VirtualBrushModel(QAbstractListModel):
    """Tiny virtual list model for non-item palette tabs."""

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self._entries: list[BrushPaletteEntry | str] = []

    def index(  # noqa: D102
        self,
        row: int,
        column: int = 0,
        parent: QModelIndex = _ROOT_INDEX,
    ) -> QModelIndex:
        return super().index(row, column, parent)

    def load_names(self, names: list[str]) -> None:
        self.beginResetModel()
        self._entries = list(names)
        self.endResetModel()

    def load_entries(self, entries: tuple[BrushPaletteEntry, ...]) -> None:
        self.beginResetModel()
        self._entries = list(entries)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = _ROOT_INDEX) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):  # noqa: ANN201
        if not index.isValid() or not 0 <= index.row() < len(self._entries):
            return None
        entry = self._entries[index.row()]
        if role in (Qt.ItemDataRole.DisplayRole, int(Qt.ItemDataRole.DisplayRole)):
            return entry.name if isinstance(entry, BrushPaletteEntry) else entry
        if role in (Qt.ItemDataRole.UserRole, int(Qt.ItemDataRole.UserRole)):
            return entry.search_text if isinstance(entry, BrushPaletteEntry) else entry
        return None

    def entry_at(self, row: int) -> BrushPaletteEntry | None:
        if not 0 <= row < len(self._entries):
            return None
        entry = self._entries[row]
        return entry if isinstance(entry, BrushPaletteEntry) else None


class BrushPaletteDock(GlassDockWidget):
    """Legacy-style brush palette dock with a real model/view Item tab."""

    item_selected = pyqtSignal(ItemEntry)
    brush_selected = pyqtSignal(BrushPaletteEntry)
    manage_houses_requested = pyqtSignal()

    _PALETTE_NAMES = ("Terrain", "Doodads", "Item", "Creature", "RAW")

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        brush_entries: tuple[BrushPaletteEntry, ...] | None = None,
    ) -> None:
        super().__init__("BRUSH PALETTE", parent)
        self.setObjectName("brush_palette_dock")
        self._views: dict[str, QListView] = {}
        self._models: dict[str, VirtualBrushModel] = {}
        self._proxies: dict[str, QSortFilterProxyModel] = {}
        self._item_palette: ItemPaletteWidget | None = None
        self._brush_entries = entries_by_palette(
            brush_entries or default_brush_palette_entries()
        )
        self._setup_ui()

    @property
    def item_palette(self) -> ItemPaletteWidget | None:
        return self._item_palette

    def palette_names(self) -> tuple[str, ...]:
        return self._PALETTE_NAMES

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
        self._search_bar.setStyleSheet(input_field_qss("QLineEdit"))
        self._search_bar.textChanged.connect(self._apply_search_to_current_palette)
        layout.addWidget(self._search_bar)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_palette_changed)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {qss_color(THEME.ghost_border)};
                background: transparent;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {qss_color(THEME.ash_lavender)};
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                padding: 6px 12px;
                border: 1px solid transparent;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: #FFFFFF;
                border-bottom: 2px solid {qss_color(THEME.amethyst_core)};
            }}
            QTabBar::tab:hover {{
                background: rgba(255, 255, 255, 0.05);
            }}
        """)

        for name in self._PALETTE_NAMES:
            if name == "Item":
                self._item_palette = ItemPaletteWidget(self)
                self._item_palette.item_selected.connect(self.item_selected)
                self.tabs.addTab(self._item_palette, name)
            else:
                self.tabs.addTab(self._create_brush_view(name), name)

        layout.addWidget(self.tabs)
        self.set_inner_layout(layout)
        self._sync_search_placeholder()
        self._apply_search_to_current_palette(self._search_bar.text())

    def _create_brush_view(self, name: str) -> QListView:
        model = VirtualBrushModel(self)
        model.load_entries(self._brush_entries.get(name, ()))
        proxy = QSortFilterProxyModel(self)
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        proxy.setFilterRole(int(Qt.ItemDataRole.UserRole))

        view = QListView()
        view.setFrameShape(QListView.Shape.NoFrame)
        view.setModel(proxy)
        view.setUniformItemSizes(True)
        view.setIconSize(QSize(32, 32))
        view.setStyleSheet(item_view_qss("QListView"))
        view.setFont(TYPOGRAPHY.ui_label())
        view.clicked.connect(
            lambda index, palette_name=name: self._on_brush_clicked(
                palette_name,
                index,
            )
        )

        self._models[name] = model
        self._proxies[name] = proxy
        self._views[name] = view
        return view

    def _on_brush_clicked(self, palette_name: str, index: QModelIndex) -> None:
        proxy = self._proxies.get(palette_name)
        model = self._models.get(palette_name)
        if proxy is None or model is None:
            return
        source_index = proxy.mapToSource(index)
        entry = model.entry_at(source_index.row())
        if entry is not None:
            self.brush_selected.emit(entry)

    def _apply_search_to_current_palette(self, text: str) -> None:
        current = self.current_palette()
        if current == "Item" and self._item_palette is not None:
            self._item_palette.set_search_text(text)
            return
        proxy = self._proxies.get(current)
        if proxy is not None:
            proxy.setFilterFixedString(text)

    def _sync_search_placeholder(self) -> None:
        if self.current_palette() == "Item":
            self._search_bar.setPlaceholderText("Search items")
        else:
            self._search_bar.setPlaceholderText("Search brushes")

    def _on_palette_changed(self, _index: int) -> None:
        self._sync_search_placeholder()
        self._apply_search_to_current_palette(self._search_bar.text())
