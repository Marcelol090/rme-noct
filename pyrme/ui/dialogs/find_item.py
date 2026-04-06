"""Find Item Dialog.

Ported from legacy C++ FindItemDialog (ui/find_item_window.h/.cpp).
Provides item/creature search with type and property filters.
Grid view toggle deferred to Tier 3 — this implements list mode only.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.theme import THEME, TYPOGRAPHY


class FindItemDialog(QDialog):
    """Dialog for searching items and brushes ("Find Item...").

    Matches legacy C++ FindItemDialog structure:
    - Left panel: search bar + type/property filter checkboxes
    - Right panel: result count + list view
    - Footer: Cancel (ghost), Search on Map (ghost), OK (amethyst CTA)

    Grid/icon view toggle is deferred to Tier 3.
    """

    # DESIGN.md: Find Item dialog = 520 × 460
    DIALOG_SIZE = QSize(520, 460)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Find Item")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._apply_dialog_style()
        self._build_layout()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Elevation 3 dialog styling."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME.void_black.name()};
                color: {THEME.moonstone_white.name()};
            }}
            QLabel {{
                color: {THEME.moonstone_white.name()};
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                background: transparent;
            }}
            QLineEdit {{
                background-color: {THEME.obsidian_glass.name()};
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                padding: 6px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME.focus_border.name()};
                background-color: {THEME.lifted_glass.name()};
            }}
            QListWidget {{
                background-color: {THEME.obsidian_glass.name()};
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                color: {THEME.moonstone_white.name()};
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 4px 8px;
                border-left: 3px solid transparent;
                min-height: 24px;
            }}
            QListWidget::item:selected {{
                background-color: {THEME.lifted_glass.name()};
                border-left: 3px solid {THEME.amethyst_core.name()};
                color: {THEME.moonstone_white.name()};
            }}
            QListWidget::item:hover {{
                background-color: {THEME.lifted_glass.name()};
            }}
            QGroupBox {{
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 4px;
                margin-top: 12px;
                padding: 8px 8px 4px 8px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 600;
                color: {THEME.ash_lavender.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                padding: 0 6px;
                color: {THEME.ash_lavender.name()};
            }}
            QCheckBox {{
                spacing: 6px;
                color: {THEME.moonstone_white.name()};
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 1px solid {THEME.ghost_border.name()};
            }}
            QCheckBox::indicator:checked {{
                background-color: {THEME.amethyst_core.name()};
                border-color: {THEME.amethyst_core.name()};
            }}
        """)

    def _build_layout(self) -> None:
        """Construct the dialog layout with splitter."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Dialog heading
        heading = QLabel("Find Item")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        heading.setStyleSheet(
            f"color: {THEME.moonstone_white.name()}; font-weight: 600;"
        )
        layout.addWidget(heading)

        # Splitter: Left (filters) | Right (results)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)

        # ── Left Panel: Filters ─────────────────────────────────
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        # Search bar
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search items...")
        self.search_field.setToolTip(
            "Type at least 2 characters to filter items and brushes."
        )
        left_layout.addWidget(self.search_field)

        # Type filters (legacy: AdvancedFinderTypeFilter)
        type_group = QGroupBox("TYPE")
        type_layout = QVBoxLayout(type_group)
        type_layout.setSpacing(4)

        self.chk_items = QCheckBox("Items")
        self.chk_items.setChecked(True)
        self.chk_raw = QCheckBox("Raw Items")
        self.chk_creatures = QCheckBox("Creatures")

        type_layout.addWidget(self.chk_items)
        type_layout.addWidget(self.chk_raw)
        type_layout.addWidget(self.chk_creatures)
        left_layout.addWidget(type_group)

        # Property filters (legacy: AdvancedFinderPropertyFilter — core subset + Writable)
        prop_group = QGroupBox("PROPERTIES")
        prop_layout = QVBoxLayout(prop_group)
        prop_layout.setSpacing(4)

        self.chk_impassable = QCheckBox("Impassable")
        self.chk_immovable = QCheckBox("Immovable")
        self.chk_container = QCheckBox("Container")
        self.chk_pickupable = QCheckBox("Pickupable")
        self.chk_stackable = QCheckBox("Stackable")
        self.chk_writable = QCheckBox("Writable")

        prop_layout.addWidget(self.chk_impassable)
        prop_layout.addWidget(self.chk_immovable)
        prop_layout.addWidget(self.chk_container)
        prop_layout.addWidget(self.chk_pickupable)
        prop_layout.addWidget(self.chk_stackable)
        prop_layout.addWidget(self.chk_writable)
        left_layout.addWidget(prop_group)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # ── Right Panel: Results ────────────────────────────────
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        # Result count label
        self.result_count = QLabel("5 results")
        self.result_count.setFont(TYPOGRAPHY.ui_label(11))
        self.result_count.setStyleSheet(f"color: {THEME.ash_lavender.name()};")
        right_layout.addWidget(self.result_count)

        # Results list (list mode only — grid deferred to Tier 3)
        self.item_list = QListWidget()
        self.item_list.setToolTip("Double-click to select an item.")

        # Populate with dummy search results showing item IDs
        dummy_items = [
            ("2555", "Grass"),
            ("2556", "Dirt"),
            ("1049", "Stone Wall"),
            ("1214", "Wooden Door"),
            ("2148", "Gold Coin"),
        ]
        for item_id, item_name in dummy_items:
            item = QListWidgetItem(f"[{item_id}] {item_name}")
            item.setFont(TYPOGRAPHY.ui_label())
            self.item_list.addItem(item)

        right_layout.addWidget(self.item_list, 1)
        splitter.addWidget(right_panel)

        # Splitter proportions: ~35% filters, ~65% results
        splitter.setSizes([180, 320])

        layout.addWidget(splitter, 1)

        # ── Footer: Action Buttons ──────────────────────────────
        footer = QHBoxLayout()
        footer.setSpacing(8)

        # Search on Map (ghost button)
        self.btn_search_map = QPushButton("Search on Map")
        self.btn_search_map.setStyleSheet(self._ghost_button_style())
        footer.addWidget(self.btn_search_map)

        footer.addStretch()

        # Cancel (ghost button)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet(self._ghost_button_style())
        self.btn_cancel.clicked.connect(self.reject)
        footer.addWidget(self.btn_cancel)

        # OK (amethyst CTA button)
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME.amethyst_core.name()};
                border: none;
                border-radius: 6px;
                color: {THEME.moonstone_white.name()};
                padding: 6px 16px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {THEME.deep_amethyst.name()};
            }}
        """)
        self.btn_ok.clicked.connect(self.accept)
        footer.addWidget(self.btn_ok)

        layout.addLayout(footer)

    def _ghost_button_style(self) -> str:
        """Return the ghost (secondary) button stylesheet."""
        return f"""
            QPushButton {{
                background: none;
                border: 1px solid {THEME.ghost_border.name()};
                border-radius: 6px;
                color: {THEME.ash_lavender.name()};
                padding: 6px 16px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {THEME.lifted_glass.name()};
                border: 1px solid {THEME.active_border.name()};
                color: {THEME.moonstone_white.name()};
            }}
        """
