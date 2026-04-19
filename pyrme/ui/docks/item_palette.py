"""Item palette widget – search-first, category rail, virtual list.

Designed to replace the mock Item tab inside BrushPaletteDock.
"""

from __future__ import annotations

from PyQt6.QtCore import QItemSelectionModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListView,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.models.item_palette_model import (
    ItemCatalog,
    ItemCategoryModel,
    ItemResultModel,
)
from pyrme.ui.models.item_palette_types import ItemEntry, QueryKey
from pyrme.ui.theme import THEME, TYPOGRAPHY


class ItemPaletteWidget(QWidget):
    """Search-first item browser for the palette dock.

    Signals:
        item_selected(ItemEntry): emitted when the user clicks a result row.
    """

    item_selected = pyqtSignal(object)  # ItemEntry

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("item_palette_widget")

        self._catalog = ItemCatalog()
        self._result_model = ItemResultModel(self._catalog, self)
        self._category_model = ItemCategoryModel(self)
        self._current_category = ""

        self._setup_ui()
        self._connect_signals()

    # ── public API ────────────────────────────────────────────
    def load_items(self, entries: list[ItemEntry]) -> None:
        """Replace the full item catalog and refresh views."""
        self._catalog.load(entries)
        self._category_model.load_from_catalog(self._catalog)
        self._result_model.show_all()
        self._update_count_label()
        self._select_all_category()

    def set_search_text(self, text: str) -> None:
        """External driver for the item filter (called by parent dock)."""
        self._on_search_changed(text)

    def clear_category(self) -> None:
        """Reset category selection to 'All' and show all items."""
        self._current_category = ""
        self._select_all_category()
        self._on_search_changed("")

    # ── layout ────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        # Count label header
        count_row = QHBoxLayout()
        count_row.setSpacing(8)

        self._count_label = QLabel("0 items")
        self._count_label.setFont(TYPOGRAPHY.ui_label(10))
        self._count_label.setStyleSheet(
            f"color: {THEME.muted_slate.name()}; padding-right: 4px;"
        )
        count_row.addStretch(1)
        count_row.addWidget(self._count_label)
        root.addLayout(count_row)

        # Splitter: category rail | result list
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {THEME.ghost_border.name()}; }}"
        )

        # Category rail (left)
        self._category_view = QListView()
        self._category_view.setModel(self._category_model)
        self._category_view.setMaximumWidth(140)
        self._category_view.setFont(TYPOGRAPHY.ui_label(11))
        self._category_view.setFrameShape(QListView.Shape.NoFrame)
        self._category_view.setStyleSheet(self._rail_qss())
        splitter.addWidget(self._category_view)

        # Result list (right)
        self._result_view = QListView()
        self._result_view.setModel(self._result_model)
        self._result_view.setFont(TYPOGRAPHY.ui_label())
        self._result_view.setFrameShape(QListView.Shape.NoFrame)
        self._result_view.setUniformItemSizes(True)
        self._result_view.setStyleSheet(self._list_qss())
        splitter.addWidget(self._result_view)

        # Empty state
        self._empty_label = QLabel("No items found")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setFont(TYPOGRAPHY.ui_label(12))
        self._empty_label.setStyleSheet(
            f"color: {THEME.muted_slate.name()}; padding: 32px;"
        )
        self._empty_label.setVisible(False)

        splitter.setSizes([120, 300])
        root.addWidget(splitter, 1)
        root.addWidget(self._empty_label)

    # ── signals ───────────────────────────────────────────────
    def _connect_signals(self) -> None:
        self._category_view.clicked.connect(self._on_category_clicked)
        self._result_view.clicked.connect(self._on_result_clicked)

    def _on_search_changed(self, text: str) -> None:
        self._last_search_text = text
        key = QueryKey.from_raw(text, self._current_category)
        self._result_model.apply_query(key)
        self._update_count_label()

    def _on_category_clicked(self, index: QModelIndex) -> None:
        self._current_category = self._category_model.category_at(index.row())
        text = getattr(self, "_last_search_text", "")
        key = QueryKey.from_raw(text, self._current_category)
        self._result_model.apply_query(key)
        self._update_count_label()

    def _on_result_clicked(self, index: QModelIndex) -> None:
        entry = self._result_model.entry_at(index.row())
        if entry is not None:
            self.item_selected.emit(entry)

    # ── helpers ───────────────────────────────────────────────
    def _select_all_category(self) -> None:
        """Visually select the 'All' row in the category rail."""
        all_index = self._category_model.index(0)
        sel_model = self._category_view.selectionModel()
        if sel_model is not None:
            sel_model.select(
                all_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
            self._category_view.setCurrentIndex(all_index)

    def _update_count_label(self) -> None:
        count = self._result_model.visible_count
        self._count_label.setText(f"{count:,} items")
        self._empty_label.setVisible(count == 0)
        self._result_view.setVisible(count > 0)

    # ── stylesheets ───────────────────────────────────────────

    @staticmethod
    def _rail_qss() -> str:
        return f"""
            QListView {{
                background: transparent;
                outline: none;
                color: {THEME.ash_lavender.name()};
            }}
            QListView::item {{
                padding: 8px;
            }}
            QListView::item:selected {{
                background-color: {THEME.amethyst_glow.name()};
                color: {THEME.moonstone_white.name()};
                border-radius: 2px;
            }}
            QListView::item:hover:!selected {{
                background-color: rgba(255, 255, 255, 0.05);
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
