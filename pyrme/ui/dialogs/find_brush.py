"""Find Brush Dialog.

Local search-first dialog for the legacy "Jump to Brush" command.
The current Python shell can honestly select supported palette pages
or item-backed brushes without pretending full C++ brush parity.
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.dialogs.find_item import DEFAULT_CATALOG
from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, item_view_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY


@dataclass(frozen=True, slots=True)
class FindBrushResult:
    """Selectable local jump-to-brush result."""

    name: str
    kind: str
    palette_name: str | None = None
    item_id: int | None = None


_DEFAULT_PALETTES = ("Terrain", "Doodads", "Item", "Creature", "RAW")


class FindBrushDialog(QDialog):
    """Search dialog for the legacy Jump to Brush command."""

    DIALOG_SIZE = QSize(480, 420)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        catalog: list[FindBrushResult] | tuple[FindBrushResult, ...] | None = None,
        window_title: str = "Jump to Brush",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self._catalog = list(catalog or self._default_catalog())
        self._current_results: list[FindBrushResult] = []
        self._selected_result: FindBrushResult | None = None

        self.setStyleSheet("\n".join([dialog_base_qss("QLineEdit"), item_view_qss("QListWidget")]))
        self._build_layout()
        self._refresh_results()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        heading = QLabel("Jump to Brush")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type at least 2 characters...")
        self.search_field.textChanged.connect(self._refresh_results)
        layout.addWidget(self.search_field)

        self.result_count = QLabel("0 results")
        self.result_count.setFont(TYPOGRAPHY.ui_label(11))
        layout.addWidget(self.result_count)

        self.result_list = QListWidget()
        self.result_list.itemSelectionChanged.connect(self._sync_selected_result)
        self.result_list.itemDoubleClicked.connect(lambda *_: self.accept())
        layout.addWidget(self.result_list, 1)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        footer.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(ghost_button_qss())
        cancel_button.clicked.connect(self.reject)
        footer.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(primary_button_qss())
        ok_button.clicked.connect(self.accept)
        footer.addWidget(ok_button)

        layout.addLayout(footer)

    def selected_result(self) -> FindBrushResult | None:
        """Return the selected brush result, if any."""
        return self._selected_result

    def accept(self) -> None:  # noqa: D401
        """Accept the dialog, defaulting to the first search result when needed."""
        if self.result_list.count() > 0 and self.result_list.currentRow() < 0:
            self.result_list.setCurrentRow(0)
        self._selected_result = self._current_selected_result()
        super().accept()

    def _refresh_results(self) -> None:
        search_text = " ".join(self.search_field.text().split()).casefold()
        if len(search_text) < 2:
            self._current_results = []
        else:
            self._current_results = [
                result
                for result in self._catalog
                if search_text in result.name.casefold()
                or (result.item_id is not None and search_text in str(result.item_id))
            ]

        result_count = len(self._current_results)
        self.result_count.setText(
            "1 result" if result_count == 1 else f"{result_count} results"
        )

        self.result_list.blockSignals(True)
        self.result_list.clear()
        for result in self._current_results:
            item = QListWidgetItem(self._format_result_text(result))
            item.setFont(TYPOGRAPHY.ui_label())
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.result_list.addItem(item)
        self.result_list.blockSignals(False)

        if self.result_list.count() > 0:
            self.result_list.setCurrentRow(0)
        self._sync_selected_result()

    def _sync_selected_result(self) -> None:
        self._selected_result = self._current_selected_result()

    def _current_selected_result(self) -> FindBrushResult | None:
        current_item = self.result_list.currentItem()
        if current_item is None:
            return None
        result = current_item.data(Qt.ItemDataRole.UserRole)
        return result if isinstance(result, FindBrushResult) else None

    @staticmethod
    def _format_result_text(result: FindBrushResult) -> str:
        if result.kind == "palette":
            return f"{result.name} palette"
        if result.item_id is not None:
            return f"{result.name} (#{result.item_id})"
        return result.name

    @staticmethod
    def _default_catalog() -> tuple[FindBrushResult, ...]:
        palette_results = tuple(
            FindBrushResult(name=palette, kind="palette", palette_name=palette)
            for palette in _DEFAULT_PALETTES
        )
        item_results = tuple(
            FindBrushResult(
                name=result.name,
                kind="item",
                palette_name="Item",
                item_id=result.server_id,
            )
            for result in DEFAULT_CATALOG
            if result.kind != "creature"
        )
        return palette_results + item_results
