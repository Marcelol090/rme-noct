"""Preferences Dialog.

Follows the Noct Map Editor Design System (DESIGN.md) for dialog styling.
Uses a sidebar navigation with stacked pages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QFileDialog,
    QFormLayout,
)

from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY

if TYPE_CHECKING:
    from pyrme.ui.main_window import MainWindow


class PreferencesDialog(QDialog):
    """Application preferences window."""

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumSize(780, 560)
        
        self._apply_dialog_style()
        self._build_layout()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Glassmorphism styling."""
        self.setStyleSheet(dialog_base_qss())

    def _build_layout(self) -> None:
        """Construct the preferences layout with sidebar navigation."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Area
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: rgba(255, 255, 255, 0.02); border-bottom: 1px solid rgba(255, 255, 255, 0.05);")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        title = QLabel("PREFERENCES")
        title.setFont(TYPOGRAPHY.label_sm())
        title.setStyleSheet("color: rgba(201, 196, 215, 0.6); letter-spacing: 2px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        main_layout.addWidget(header)

        # Content Area (Sidebar + Pages)
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setSpacing(4)
        self.sidebar.setContentsMargins(8, 16, 8, 16)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 0.1);
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
                outline: none;
            }
            QListWidget::item {
                height: 40px;
                border-radius: 8px;
                padding-left: 12px;
                color: rgba(201, 196, 215, 0.6);
            }
            QListWidget::item:selected {
                background-color: rgba(124, 92, 252, 0.1);
                color: #C8BFFF;
                font-weight: 600;
            }
            QListWidget::item:hover:!selected {
                background-color: rgba(255, 255, 255, 0.03);
            }
        """)

        # Pages
        self.pages = QStackedWidget()
        self.pages.setContentsMargins(32, 32, 32, 32)

        items = [
            ("General", self._create_general_page()),
            ("Editor", self._create_editor_page()),
            ("Graphics", self._create_graphics_page()),
            ("Interface", self._create_interface_page()),
            ("Client Version", self._create_client_page()),
        ]

        for label, widget in items:
            list_item = QListWidgetItem(label)
            self.sidebar.addItem(list_item)
            self.pages.addWidget(widget)

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.pages)
        main_layout.addWidget(content)

        # Footer Area
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("background-color: rgba(255, 255, 255, 0.02); border-top: 1px solid rgba(255, 255, 255, 0.05);")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 0, 24, 0)
        footer_layout.setSpacing(12)

        footer_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(ghost_button_qss())
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.clicked.connect(self.reject)
        
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(ghost_button_qss())
        apply_btn.setFixedSize(100, 36)
        
        save_btn = QPushButton("Save & Close")
        save_btn.setStyleSheet(primary_button_qss())
        save_btn.setFixedSize(140, 36)
        save_btn.clicked.connect(self.accept)

        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(apply_btn)
        footer_layout.addWidget(save_btn)
        
        main_layout.addWidget(footer)

    def _create_page_container(self, title: str) -> QWidget:
        """Create a styled container for a preferences page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        header = QLabel(title.upper())
        header.setFont(TYPOGRAPHY.title_md())
        header.setStyleSheet("color: #FFFFFF; font-weight: 700;")
        layout.addWidget(header)
        
        return page

    def _create_general_page(self) -> QWidget:
        page = self._create_page_container("General")
        layout = page.layout()
        
        form = QFormLayout()
        form.setVerticalSpacing(16)
        
        lang = QComboBox()
        lang.addItems(["English (US)", "Portuguese (BR)", "Spanish", "Polish"])
        lang.setFixedWidth(200)
        form.addRow(self._label("Language"), lang)
        
        updates = QCheckBox("Automatically check for updates")
        updates.setChecked(True)
        form.addRow(None, updates)
        
        autosave = QSpinBox()
        autosave.setRange(0, 60)
        autosave.setValue(5)
        autosave.setSuffix(" min")
        form.addRow(self._label("Autosave Interval"), autosave)
        
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _create_editor_page(self) -> QWidget:
        page = self._create_page_container("Editor")
        layout = page.layout()
        
        form = QFormLayout()
        form.setVerticalSpacing(16)
        
        selection = QComboBox()
        selection.addItems(["Standard (Box)", "Legacy (Classic)"])
        selection.setFixedWidth(200)
        form.addRow(self._label("Selection Mode"), selection)
        
        autoborder = QCheckBox("Enable Autoborder")
        autoborder.setChecked(True)
        form.addRow(None, autoborder)
        
        undo = QSpinBox()
        undo.setRange(10, 1000)
        undo.setValue(100)
        form.addRow(self._label("Undo History Size"), undo)
        
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _create_graphics_page(self) -> QWidget:
        page = self._create_page_container("Graphics")
        layout = page.layout()
        
        form = QFormLayout()
        form.setVerticalSpacing(16)
        
        renderer = QComboBox()
        renderer.addItems(["WGPU (Accelerated)", "Vulkan", "Software"])
        renderer.setFixedWidth(200)
        form.addRow(self._label("Preferred Renderer"), renderer)
        
        vsync = QCheckBox("Enable VSync")
        form.addRow(None, vsync)
        
        grid = QSpinBox()
        grid.setRange(0, 100)
        grid.setValue(60)
        grid.setSuffix("%")
        form.addRow(self._label("Grid Opacity"), grid)
        
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _create_interface_page(self) -> QWidget:
        page = self._create_page_container("Interface")
        layout = page.layout()
        
        form = QFormLayout()
        form.setVerticalSpacing(16)
        
        theme = QComboBox()
        theme.addItems(["Obsidian Void", "Ethereal Amethyst"])
        theme.setFixedWidth(200)
        form.addRow(self._label("Theme"), theme)
        
        transparency = QSpinBox()
        transparency.setRange(50, 100)
        transparency.setValue(90)
        transparency.setSuffix("%")
        form.addRow(self._label("UI Transparency"), transparency)
        
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _create_client_page(self) -> QWidget:
        page = self._create_page_container("Client Version")
        layout = page.layout()
        
        form = QFormLayout()
        form.setVerticalSpacing(16)
        
        version = QComboBox()
        version.addItems(["13.10", "12.00", "8.60", "7.60"])
        version.setFixedWidth(200)
        form.addRow(self._label("Default Client"), version)
        
        path_layout = QHBoxLayout()
        path_input = QLineEdit()
        path_input.setPlaceholderText("Select data directory...")
        path_btn = QPushButton("Browse")
        path_btn.setStyleSheet(ghost_button_qss())
        path_btn.setFixedWidth(80)
        path_layout.addWidget(path_input)
        path_layout.addWidget(path_btn)
        form.addRow(self._label("Data Path"), path_layout)
        
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(TYPOGRAPHY.body_md())
        lbl.setStyleSheet("color: rgba(201, 196, 215, 0.8);")
        return lbl
