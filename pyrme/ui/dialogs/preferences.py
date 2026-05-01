"""Preferences Dialog — Noct Map Editor.

Comprehensive settings dashboard with sidebar navigation.
Aligned with Obsidian Cartographer design system.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles.contracts import (
    checkbox_qss,
    dialog_base_qss,
    dropdown_qss,
    ghost_button_qss,
    item_view_qss,
    primary_button_qss,
    qss_color,
    section_heading_qss,
)
from pyrme.ui.theme import THEME


class PreferencesDialog(QDialog):
    """Noct Map Editor Preferences Dialog.

    Features a sidebar for category selection and a stacked widget for settings.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_window()
        self._build_interface()

    def _setup_window(self) -> None:
        self.setWindowTitle("Preferences")
        self.setMinimumSize(QSize(780, 560))
        self.setStyleSheet(dialog_base_qss())

    def _build_interface(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # Header
        header = QLabel("PREFERENCES")
        header.setStyleSheet(section_heading_qss())
        root.addWidget(header)

        # Main content area
        content = QHBoxLayout()
        content.setSpacing(12)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet(item_view_qss("QListWidget"))
        self.sidebar.addItem("General")
        self.sidebar.addItem("Graphics")
        self.sidebar.addItem("Interface")
        self.sidebar.addItem("Client Version")
        self.sidebar.currentRowChanged.connect(self._on_category_changed)
        content.addWidget(self.sidebar)

        # Settings Pane
        self.pages = QStackedWidget()
        self.pages.setStyleSheet(
            f"""
            QStackedWidget {{
                background-color: {qss_color(THEME.obsidian_glass)};
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 8px;
            }}
            """
        )

        self.pages.addWidget(self._build_general_page())
        self.pages.addWidget(self._build_graphics_page())
        self.pages.addWidget(self._build_interface_page())
        self.pages.addWidget(self._build_client_page())

        content.addWidget(self.pages, stretch=1)
        root.addLayout(content, stretch=1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(ghost_button_qss())
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet(primary_button_qss())
        save_btn.clicked.connect(self.accept)
        footer.addWidget(save_btn)

        root.addLayout(footer)

        self.sidebar.setCurrentRow(0)

    def _build_general_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        heading = QLabel("GENERAL SETTINGS")
        heading.setStyleSheet(section_heading_qss())
        layout.addWidget(heading)

        undo_layout = QHBoxLayout()
        undo_label = QLabel("Undo Levels:")
        self.undo_spin = QSpinBox()
        self.undo_spin.setRange(1, 1000)
        self.undo_spin.setValue(100)
        self.undo_spin.setFixedWidth(80)
        self.undo_spin.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: rgba(255, 255, 255, 15);
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-radius: 4px;
                color: {qss_color(THEME.moonstone_white)};
                padding: 4px;
            }}
            """
        )
        undo_layout.addWidget(undo_label)
        undo_layout.addWidget(self.undo_spin)
        undo_layout.addStretch()
        layout.addLayout(undo_layout)

        self.autosave_check = QCheckBox("Enable Autosave (every 5 minutes)")
        self.autosave_check.setStyleSheet(checkbox_qss())
        layout.addWidget(self.autosave_check)

        layout.addStretch()
        return page

    def _build_graphics_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        heading = QLabel("GRAPHICS & RENDERING")
        heading.setStyleSheet(section_heading_qss())
        layout.addWidget(heading)

        self.grid_check = QCheckBox("Show Grid by Default")
        self.grid_check.setStyleSheet(checkbox_qss())
        self.grid_check.setChecked(True)
        layout.addWidget(self.grid_check)

        self.spawns_check = QCheckBox("Show Spawns by Default")
        self.spawns_check.setStyleSheet(checkbox_qss())
        layout.addWidget(self.spawns_check)

        self.waypoints_check = QCheckBox("Show Waypoints by Default")
        self.waypoints_check.setStyleSheet(checkbox_qss())
        layout.addWidget(self.waypoints_check)

        layout.addStretch()
        return page

    def _build_interface_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        heading = QLabel("INTERFACE PREFERENCES")
        heading.setStyleSheet(section_heading_qss())
        layout.addWidget(heading)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Active Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Obsidian Cartographer (Dark)")
        self.theme_combo.setStyleSheet(dropdown_qss())
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        layout.addStretch()
        return page

    def _build_client_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        heading = QLabel("CLIENT VERSION CONFIGURATION")
        heading.setStyleSheet(section_heading_qss())
        layout.addWidget(heading)

        info = QLabel("Manage your Tibia client installations here.")
        info.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        layout.addWidget(info)

        # Placeholder for client list
        client_list = QListWidget()
        client_list.setStyleSheet(item_view_qss("QListWidget"))
        client_list.addItem("Tibia 8.60 (C:\\Tibia860)")
        client_list.addItem("Tibia 10.98 (C:\\Tibia1098)")
        layout.addWidget(client_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Client...")
        add_btn.setStyleSheet(ghost_button_qss())
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()
        return page

    def _on_category_changed(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
