"""Find Item Dialog.

Ported from legacy C++ FindItemDialog (ui/find_item_window.h/.cpp).
Provides item/creature search with type and property filters.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles import (
    checkbox_qss,
    dialog_base_qss,
    ghost_button_qss,
    group_box_qss,
    item_view_qss,
    primary_button_qss,
    secondary_label_qss,
    section_heading_qss,
)
from pyrme.ui.theme import TYPOGRAPHY


class FindItemResultMode(StrEnum):
    """Supported local result presentation modes."""

    LIST = "list"
    GRID = "grid"


@dataclass(slots=True)
class FindItemResult:
    """A local item search result."""

    server_id: int
    client_id: int
    name: str
    sprite_hash: str
    kind: str
    flags: set[str] = field(default_factory=set)


@dataclass(slots=True)
class FindItemQuery:
    """Current local search state for the dialog."""

    search_text: str = ""
    type_filters: set[str] = field(default_factory=set)
    property_filters: set[str] = field(default_factory=set)
    result_mode: FindItemResultMode = FindItemResultMode.LIST


TYPE_FILTER_VALUES = {
    "Items": "item",
    "Raw Items": "raw-item",
    "Creatures": "creature",
}

PROPERTY_FILTER_VALUES = {
    "Impassable": "impassable",
    "Immovable": "immovable",
    "Container": "container",
    "Pickupable": "pickupable",
    "Stackable": "stackable",
    "Writable": "writable",
}

DEFAULT_CATALOG: list[FindItemResult] = [
    FindItemResult(2555, 2555, "Grass", "sprite-2555", "item", {"pickupable"}),
    FindItemResult(
        2556,
        2556,
        "Dirt",
        "sprite-2556",
        "item",
        {"pickupable", "stackable"},
    ),
    FindItemResult(
        1049,
        1049,
        "Stone Wall",
        "sprite-1049",
        "raw-item",
        {"impassable", "immovable"},
    ),
    FindItemResult(
        1214,
        1214,
        "Wooden Door",
        "sprite-1214",
        "raw-item",
        {"immovable", "writable"},
    ),
    FindItemResult(
        2148,
        2148,
        "Gold Coin",
        "sprite-2148",
        "item",
        {"pickupable", "stackable"},
    ),
    FindItemResult(3100, 3100, "Dragon", "sprite-3100", "creature", set()),
]


class FindItemDialog(QDialog):
    """Dialog for searching items and brushes ("Find Item...")."""

    # DESIGN.md: Find Item dialog = 520 × 460
    DIALOG_SIZE = QSize(520, 460)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        catalog: list[FindItemResult] | tuple[FindItemResult, ...] | None = None,
        query: FindItemQuery | None = None,
        window_title: str = "Find Item",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._catalog = [replace(result) for result in (catalog or DEFAULT_CATALOG)]
        self._query = self._clone_query(query or self._default_query())
        self._selected_result: FindItemResult | None = None
        self._current_results: list[FindItemResult] = []
        self._last_search_map_query: FindItemQuery | None = None

        self._apply_dialog_style()
        self._build_layout()
        self.set_query(self._query)

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Elevation 3 dialog styling."""
        self.setStyleSheet(
            "\n".join(
                [
                    dialog_base_qss("QLineEdit"),
                    item_view_qss("QListWidget"),
                    group_box_qss(),
                    checkbox_qss(),
                ]
            )
        )

    def _build_layout(self) -> None:
        """Construct the dialog layout with splitter."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        heading = QLabel(self.windowTitle())
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search items...")
        self.search_field.setToolTip(
            "Type to filter items, raw items, and creatures."
        )
        self.search_field.textChanged.connect(self._refresh_results)
        left_layout.addWidget(self.search_field)

        type_group = QGroupBox("TYPE")
        type_layout = QVBoxLayout(type_group)
        type_layout.setSpacing(4)

        self.chk_items = QCheckBox("Items")
        self.chk_items.setChecked(True)
        self.chk_raw = QCheckBox("Raw Items")
        self.chk_creatures = QCheckBox("Creatures")
        for checkbox in (self.chk_items, self.chk_raw, self.chk_creatures):
            checkbox.toggled.connect(self._refresh_results)

        type_layout.addWidget(self.chk_items)
        type_layout.addWidget(self.chk_raw)
        type_layout.addWidget(self.chk_creatures)
        left_layout.addWidget(type_group)

        prop_group = QGroupBox("PROPERTIES")
        prop_layout = QVBoxLayout(prop_group)
        prop_layout.setSpacing(4)

        self.chk_impassable = QCheckBox("Impassable")
        self.chk_immovable = QCheckBox("Immovable")
        self.chk_container = QCheckBox("Container")
        self.chk_pickupable = QCheckBox("Pickupable")
        self.chk_stackable = QCheckBox("Stackable")
        self.chk_writable = QCheckBox("Writable")
        for checkbox in (
            self.chk_impassable,
            self.chk_immovable,
            self.chk_container,
            self.chk_pickupable,
            self.chk_stackable,
            self.chk_writable,
        ):
            checkbox.toggled.connect(self._refresh_results)

        prop_layout.addWidget(self.chk_impassable)
        prop_layout.addWidget(self.chk_immovable)
        prop_layout.addWidget(self.chk_container)
        prop_layout.addWidget(self.chk_pickupable)
        prop_layout.addWidget(self.chk_stackable)
        prop_layout.addWidget(self.chk_writable)
        left_layout.addWidget(prop_group)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(6)

        mode_label = QLabel("MODE")
        mode_label.setFont(TYPOGRAPHY.dock_title())
        mode_label.setStyleSheet(section_heading_qss())
        mode_row.addWidget(mode_label)

        self.btn_list_mode = QPushButton("List")
        self.btn_grid_mode = QPushButton("Grid")
        self.btn_list_mode.setCheckable(True)
        self.btn_grid_mode.setCheckable(True)
        self.btn_list_mode.setObjectName("find_item_list_mode")
        self.btn_grid_mode.setObjectName("find_item_grid_mode")
        self.btn_list_mode.clicked.connect(
            lambda: self.set_result_mode(FindItemResultMode.LIST)
        )
        self.btn_grid_mode.clicked.connect(
            lambda: self.set_result_mode(FindItemResultMode.GRID)
        )
        self._mode_buttons = QButtonGroup(self)
        self._mode_buttons.setExclusive(True)
        self._mode_buttons.addButton(self.btn_list_mode)
        self._mode_buttons.addButton(self.btn_grid_mode)
        mode_row.addWidget(self.btn_list_mode)
        mode_row.addWidget(self.btn_grid_mode)
        mode_row.addStretch()
        right_layout.addLayout(mode_row)

        self.result_count = QLabel("0 results")
        self.result_count.setFont(TYPOGRAPHY.ui_label(11))
        self.result_count.setStyleSheet(secondary_label_qss())
        right_layout.addWidget(self.result_count)

        self.item_list = QListWidget()
        self.item_list.setToolTip("Double-click to select an item.")
        self.item_list.itemSelectionChanged.connect(self._sync_selected_result)
        self.item_list.itemDoubleClicked.connect(lambda *_: self.accept())
        right_layout.addWidget(self.item_list, 1)
        splitter.addWidget(right_panel)
        splitter.setSizes([180, 320])

        layout.addWidget(splitter, 1)

        footer = QHBoxLayout()
        footer.setSpacing(8)

        self.btn_search_map = QPushButton("Search on Map")
        self.btn_search_map.setStyleSheet(ghost_button_qss())
        self.btn_search_map.clicked.connect(self._start_search_on_map)
        footer.addWidget(self.btn_search_map)

        footer.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet(ghost_button_qss())
        self.btn_cancel.clicked.connect(self.reject)
        footer.addWidget(self.btn_cancel)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setStyleSheet(primary_button_qss())
        self.btn_ok.clicked.connect(self.accept)
        footer.addWidget(self.btn_ok)

        layout.addLayout(footer)

    def current_query(self) -> FindItemQuery:
        """Return the current search query derived from the widgets."""
        return self._snapshot_query()

    def selected_result(self) -> FindItemResult | None:
        """Return the currently selected result."""
        return replace(self._selected_result) if self._selected_result is not None else None

    def last_search_map_query(self) -> FindItemQuery | None:
        """Return the most recent Search on Map query, if any."""
        return (
            self._clone_query(self._last_search_map_query)
            if self._last_search_map_query is not None
            else None
        )

    def set_catalog(self, catalog: list[FindItemResult] | tuple[FindItemResult, ...]) -> None:
        """Replace the local in-memory catalog and refresh results."""
        self._catalog = [replace(result) for result in catalog]
        self._refresh_results()

    def set_query(self, query: FindItemQuery) -> None:
        """Load a query into the dialog controls."""
        self._query = self._clone_query(query)
        self.search_field.blockSignals(True)
        self.chk_items.blockSignals(True)
        self.chk_raw.blockSignals(True)
        self.chk_creatures.blockSignals(True)
        self.chk_impassable.blockSignals(True)
        self.chk_immovable.blockSignals(True)
        self.chk_container.blockSignals(True)
        self.chk_pickupable.blockSignals(True)
        self.chk_stackable.blockSignals(True)
        self.chk_writable.blockSignals(True)
        self.btn_list_mode.blockSignals(True)
        self.btn_grid_mode.blockSignals(True)

        self.search_field.setText(query.search_text)
        self.chk_items.setChecked("item" in query.type_filters)
        self.chk_raw.setChecked("raw-item" in query.type_filters)
        self.chk_creatures.setChecked("creature" in query.type_filters)
        self.chk_impassable.setChecked("impassable" in query.property_filters)
        self.chk_immovable.setChecked("immovable" in query.property_filters)
        self.chk_container.setChecked("container" in query.property_filters)
        self.chk_pickupable.setChecked("pickupable" in query.property_filters)
        self.chk_stackable.setChecked("stackable" in query.property_filters)
        self.chk_writable.setChecked("writable" in query.property_filters)
        self.btn_list_mode.setChecked(query.result_mode == FindItemResultMode.LIST)
        self.btn_grid_mode.setChecked(query.result_mode == FindItemResultMode.GRID)

        self.btn_list_mode.blockSignals(False)
        self.btn_grid_mode.blockSignals(False)
        self.chk_items.blockSignals(False)
        self.chk_raw.blockSignals(False)
        self.chk_creatures.blockSignals(False)
        self.chk_impassable.blockSignals(False)
        self.chk_immovable.blockSignals(False)
        self.chk_container.blockSignals(False)
        self.chk_pickupable.blockSignals(False)
        self.chk_stackable.blockSignals(False)
        self.chk_writable.blockSignals(False)
        self.search_field.blockSignals(False)

        self._apply_result_mode(query.result_mode)
        self._refresh_results()

    def set_result_mode(self, mode: FindItemResultMode) -> None:
        """Switch the presentation mode and refresh the list."""
        self._query = replace(self._query, result_mode=mode)
        self._apply_result_mode(mode)
        self._refresh_results()

    def accept(self) -> None:  # noqa: D401
        """Accept the dialog and persist the current selection."""
        self._query = self._snapshot_query()
        self._selected_result = self._current_selected_result()
        super().accept()

    def _snapshot_query(self) -> FindItemQuery:
        """Collect the current widget values into a query object."""
        type_filters = {
            value
            for label, value in TYPE_FILTER_VALUES.items()
            if getattr(self, f"chk_{self._checkbox_suffix(label)}").isChecked()
        }
        property_filters = {
            value
            for label, value in PROPERTY_FILTER_VALUES.items()
            if getattr(self, f"chk_{self._checkbox_suffix(label)}").isChecked()
        }
        return FindItemQuery(
            search_text=self.search_field.text(),
            type_filters=type_filters,
            property_filters=property_filters,
            result_mode=self._current_result_mode(),
        )

    def _refresh_results(self) -> None:
        """Rebuild the results list from the current query and catalog."""
        query = self._snapshot_query()
        self._query = self._clone_query(query)
        self._current_results = [
            result for result in self._catalog if self._matches_query(result, query)
        ]
        self.result_count.setText(self._format_result_count(len(self._current_results)))

        previous = self._current_selected_result()
        self.item_list.blockSignals(True)
        self.item_list.clear()
        for result in self._current_results:
            item = QListWidgetItem(self._format_item_text(result, query.result_mode))
            item.setFont(TYPOGRAPHY.ui_label())
            item.setData(Qt.ItemDataRole.UserRole, result)
            item.setToolTip(self._format_item_tooltip(result))
            if query.result_mode == FindItemResultMode.GRID:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setSizeHint(QSize(132, 56))
            else:
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                item.setSizeHint(QSize(0, 24))
            self.item_list.addItem(item)

        self.item_list.blockSignals(False)

        if previous is not None:
            for index, result in enumerate(self._current_results):
                if result == previous:
                    self.item_list.setCurrentRow(index)
                    break
            else:
                self._select_first_result_if_available()
        else:
            self._select_first_result_if_available()

        self._selected_result = self._current_selected_result()

    def _capture_search_map_query(self) -> None:
        """Record the current query for the Search Map seam."""
        self._last_search_map_query = self.current_query()

    def _start_search_on_map(self) -> None:
        """Capture the current query and close so the caller can handle the seam."""
        self._capture_search_map_query()
        self.reject()

    def _sync_selected_result(self) -> None:
        """Synchronize the cached selection with the widget selection."""
        self._selected_result = self._current_selected_result()

    def _current_selected_result(self) -> FindItemResult | None:
        current_item = self.item_list.currentItem()
        if current_item is None:
            return None
        result = current_item.data(Qt.ItemDataRole.UserRole)
        return result if isinstance(result, FindItemResult) else None

    def _select_first_result_if_available(self) -> None:
        if self.item_list.count() > 0 and self.item_list.currentRow() < 0:
            self.item_list.setCurrentRow(0)

    def _apply_result_mode(self, mode: FindItemResultMode) -> None:
        """Update the view widget to match the requested mode."""
        if mode == FindItemResultMode.GRID:
            self.btn_list_mode.setChecked(False)
            self.btn_grid_mode.setChecked(True)
            self.item_list.setViewMode(QListView.ViewMode.IconMode)
            self.item_list.setWrapping(True)
            self.item_list.setFlow(QListView.Flow.LeftToRight)
            self.item_list.setGridSize(QSize(132, 56))
            self.item_list.setIconSize(QSize(32, 32))
        else:
            self.btn_list_mode.setChecked(True)
            self.btn_grid_mode.setChecked(False)
            self.item_list.setViewMode(QListView.ViewMode.ListMode)
            self.item_list.setWrapping(False)
            self.item_list.setFlow(QListView.Flow.TopToBottom)
            self.item_list.setGridSize(QSize(0, 24))
            self.item_list.setIconSize(QSize(0, 0))

    def _current_result_mode(self) -> FindItemResultMode:
        return (
            FindItemResultMode.GRID
            if self.btn_grid_mode.isChecked()
            else FindItemResultMode.LIST
        )

    def _matches_query(
        self,
        result: FindItemResult,
        query: FindItemQuery,
    ) -> bool:
        search = query.search_text.strip().lower()
        if search:
            haystack = " ".join(
                [
                    result.name.lower(),
                    str(result.server_id),
                    str(result.client_id),
                    result.sprite_hash.lower(),
                ]
            )
            if search not in haystack:
                return False

        if query.type_filters and result.kind not in query.type_filters:
            return False

        if query.property_filters:
            return query.property_filters.issubset(result.flags)

        return True

    @staticmethod
    def _format_item_text(result: FindItemResult, mode: FindItemResultMode) -> str:
        if mode == FindItemResultMode.GRID:
            return f"{result.name}\n#{result.client_id}"
        return f"[{result.server_id}] {result.name}"

    @staticmethod
    def _format_item_tooltip(result: FindItemResult) -> str:
        flags = ", ".join(sorted(result.flags)) or "none"
        return (
            f"Server ID: {result.server_id}\n"
            f"Client ID: {result.client_id}\n"
            f"Kind: {result.kind}\n"
            f"Flags: {flags}\n"
            f"Sprite: {result.sprite_hash}"
        )

    @staticmethod
    def _format_result_count(count: int) -> str:
        suffix = "result" if count == 1 else "results"
        return f"{count} {suffix}"

    @staticmethod
    def _default_query() -> FindItemQuery:
        return FindItemQuery(
            search_text="",
            type_filters={"item"},
            property_filters=set(),
            result_mode=FindItemResultMode.LIST,
        )

    @staticmethod
    def _checkbox_suffix(label: str) -> str:
        return {
            "Items": "items",
            "Raw Items": "raw",
            "Creatures": "creatures",
            "Impassable": "impassable",
            "Immovable": "immovable",
            "Container": "container",
            "Pickupable": "pickupable",
            "Stackable": "stackable",
            "Writable": "writable",
        }[label]

    @staticmethod
    def _clone_query(query: FindItemQuery) -> FindItemQuery:
        return FindItemQuery(
            search_text=query.search_text,
            type_filters=set(query.type_filters),
            property_filters=set(query.property_filters),
            result_mode=query.result_mode,
        )
