"""Search-first item palette widget."""

from __future__ import annotations

from PyQt6.QtCore import QItemSelectionModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListView,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.models.item_palette_model import (
    ItemCatalog,
    ItemCategoryModel,
    ItemResultModel,
)
from pyrme.ui.models.item_palette_types import ItemEntry, QueryKey
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY


def default_item_entries() -> list[ItemEntry]:
    """Small local fixture until backend catalog loading exists."""

    return [
        ItemEntry(1, "Stone", server_id=1, category="Ground"),
        ItemEntry(2, "Grass", server_id=2, category="Ground"),
        ItemEntry(2148, "Gold Coin", server_id=2148, category="Valuables"),
        ItemEntry(2383, "Spike Sword", server_id=2383, category="Weapons"),
        ItemEntry(2512, "Wooden Shield", server_id=2512, category="Armor"),
        ItemEntry(2671, "Ham", server_id=2671, category="Food"),
    ]


class ItemPaletteWidget(QWidget):
    """Model/view item palette optimized for quick search and selection."""

    item_selected = pyqtSignal(ItemEntry)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Item")
        self._catalog = ItemCatalog()
        self._result_model = ItemResultModel(self._catalog, self)
        self._category_model = ItemCategoryModel(self)
        self._search_text = ""
        self._current_category = ""
        self._setup_ui()
        self.load_items(default_item_entries())

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._count_label = QLabel("0 items")
        self._count_label.setFont(TYPOGRAPHY.ui_label())
        self._count_label.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        layout.addWidget(self._count_label)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(8)

        self._category_view = QListView()
        self._category_view.setModel(self._category_model)
        self._category_view.setUniformItemSizes(True)
        self._category_view.setMaximumWidth(132)
        self._category_view.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self._category_view.clicked.connect(self._on_category_clicked)
        self._category_view.setStyleSheet(self._view_qss())
        body.addWidget(self._category_view)

        result_area = QVBoxLayout()
        result_area.setContentsMargins(0, 0, 0, 0)
        result_area.setSpacing(0)

        self._result_view = QListView()
        self._result_view.setModel(self._result_model)
        self._result_view.setUniformItemSizes(True)
        self._result_view.clicked.connect(self._on_result_clicked)
        self._result_view.setStyleSheet(self._view_qss())
        result_area.addWidget(self._result_view)

        self._empty_label = QLabel("No matching items.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setFont(TYPOGRAPHY.ui_label())
        self._empty_label.setStyleSheet(f"color: {qss_color(THEME.muted_slate)};")
        self._empty_label.setVisible(False)
        result_area.addWidget(self._empty_label)

        body.addLayout(result_area, 1)
        layout.addLayout(body, 1)

    def _view_qss(self) -> str:
        return f"""
            QListView {{
                background: transparent;
                color: {qss_color(THEME.ash_lavender)};
                outline: none;
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 4px;
            }}
            QListView::item {{
                padding: 8px;
                border-bottom: 1px solid {qss_color(THEME.ghost_border)};
            }}
            QListView::item:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QListView::item:selected {{
                background-color: {qss_color(THEME.amethyst_core)};
                color: #ffffff;
            }}
        """

    def load_items(self, entries: list[ItemEntry]) -> None:
        self._catalog.load(entries)
        self._category_model.load_from_catalog(self._catalog)
        self._current_category = ""
        self._apply_query()
        self._select_all_category()

    def set_search_text(self, text: str) -> None:
        self._search_text = text
        self._apply_query()

    def clear_category(self) -> None:
        self._current_category = ""
        self._apply_query()
        self._select_all_category()

    def _apply_query(self) -> None:
        self._result_model.apply_query(
            QueryKey.from_raw(self._search_text, self._current_category)
        )
        count = self._result_model.rowCount()
        self._count_label.setText(f"{count} item{'s' if count != 1 else ''}")
        has_results = count > 0
        self._result_view.setVisible(has_results)
        self._empty_label.setVisible(not has_results)

    def _select_all_category(self) -> None:
        selection = self._category_view.selectionModel()
        if selection is None or self._category_model.rowCount() == 0:
            return
        selection.select(
            self._category_model.index(0),
            QItemSelectionModel.SelectionFlag.ClearAndSelect
            | QItemSelectionModel.SelectionFlag.Rows,
        )

    def _on_category_clicked(self, index: QModelIndex) -> None:
        self._current_category = self._category_model.category_at(index.row())
        self._apply_query()

    def _on_result_clicked(self, index: QModelIndex) -> None:
        entry = self._result_model.entry_at(index.row())
        if entry is not None:
            self.item_selected.emit(entry)
