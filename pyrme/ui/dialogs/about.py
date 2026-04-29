"""About Dialog.

Follows the Noct Map Editor Design System (DESIGN.md) for dialog styling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
)

from pyrme.ui.styles import dialog_base_qss, ghost_button_qss, primary_button_qss
from pyrme.ui.theme import TYPOGRAPHY

if TYPE_CHECKING:
    from pyrme.ui.main_window import MainWindow


class AboutDialog(QDialog):
    """Information window about the application."""

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        self.setWindowTitle("About Noct Map Editor")
        self.setFixedSize(400, 520)
        
        # We want the premium glass look, but keep standard window controls for now
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._apply_dialog_style()
        self._build_layout()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor Glassmorphism styling."""
        self.setStyleSheet(dialog_base_qss())

    def _build_layout(self) -> None:
        """Construct the about window layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 40, 32, 32)
        layout.setSpacing(0)

        # --- Branding Section ---
        logo_container = QVBoxLayout()
        logo_container.setSpacing(16)
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Placeholder (Amethyst Glow)
        logo_frame = QFrame()
        logo_frame.setFixedSize(80, 80)
        logo_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #9D58FF);
                border-radius: 20px;
            }
        """)
        logo_container.addWidget(logo_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("NOCT MAP EDITOR")
        title.setFont(TYPOGRAPHY.display_sm())
        title.setStyleSheet("color: #FFFFFF; font-weight: 800; letter-spacing: 2px;")
        logo_container.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("THE ETHEREAL CARTOGRAPHER")
        subtitle.setFont(TYPOGRAPHY.label_sm())
        subtitle.setStyleSheet("color: rgba(201, 196, 215, 0.6); letter-spacing: 4px;")
        logo_container.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(logo_container)
        layout.addSpacing(40)

        # --- Description ---
        desc = QLabel(
            "Modern editorial-grade map editor for\nhigh-performance world building."
        )
        desc.setFont(TYPOGRAPHY.body_md())
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: rgba(201, 196, 215, 0.8); line-height: 1.5;")
        layout.addWidget(desc)
        
        layout.addSpacing(32)

        # --- Version Grid ---
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        grid_layout = QVBoxLayout(grid_frame)
        grid_layout.setSpacing(12)

        versions = [
            ("VERSION", "v1.4.0-noct"),
            ("CORE", "0.8.2-rust-wgpu"),
            ("INTERFACE", "PyQt 6.10"),
            ("PLATFORM", "x64 WINDOWS"),
        ]

        for key, val in versions:
            row = QHBoxLayout()
            key_label = QLabel(key)
            key_label.setFont(TYPOGRAPHY.label_sm())
            key_label.setStyleSheet("color: rgba(201, 196, 215, 0.4);")
            
            val_label = QLabel(val)
            val_label.setFont(TYPOGRAPHY.label_sm())
            val_label.setStyleSheet("color: #C8BFFF; font-family: 'JetBrains Mono';")
            
            row.addWidget(key_label)
            row.addStretch()
            row.addWidget(val_label)
            grid_layout.addLayout(row)

        layout.addWidget(grid_frame)
        layout.addStretch()

        # --- Footer Actions ---
        actions = QVBoxLayout()
        actions.setSpacing(12)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(primary_button_qss())
        ok_btn.setFixedHeight(44)
        ok_btn.clicked.connect(self.accept)
        actions.addWidget(ok_btn)

        secondary = QHBoxLayout()
        secondary.setSpacing(12)

        copy_btn = QPushButton("Copy Info")
        copy_btn.setStyleSheet(ghost_button_qss())
        copy_btn.setFixedHeight(36)
        
        source_btn = QPushButton("Source")
        source_btn.setStyleSheet(ghost_button_qss())
        source_btn.setFixedHeight(36)

        secondary.addWidget(copy_btn)
        secondary.addWidget(source_btn)
        actions.addLayout(secondary)

        layout.addLayout(actions)

        # Copyright
        copyright = QLabel("© 2024 NOCT LABS • ALL RIGHTS RESERVED")
        copyright.setFont(TYPOGRAPHY.label_sm())
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright.setStyleSheet("color: rgba(201, 196, 215, 0.2); margin-top: 16px;")
        layout.addWidget(copyright)
