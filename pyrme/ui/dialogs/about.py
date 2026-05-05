"""About Dialog — Noct Map Editor.

Displays version, credits, and license information in a glassmorphic modal.
Aligned with Hyprland Glassmorphism design system.
"""

from __future__ import annotations

import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles.contracts import (
    dialog_base_qss,
    primary_button_qss,
    qss_color,
)
from pyrme.ui.theme import THEME, TYPOGRAPHY


class AboutDialog(QDialog):
    """Noct Map Editor About Dialog.

    A clean, centered modal with the Noct Wolf logo and project metadata.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_window()
        self._build_interface()

    def _setup_window(self) -> None:
        self.setWindowTitle("About Noct Map Editor")
        self.setFixedSize(QSize(520, 440))
        self.setStyleSheet(
            dialog_base_qss()
            + f"""
            QDialog {{
                background-color: {qss_color(THEME.void_black)};
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-top: 1px solid {qss_color(THEME.active_border)};
                border-radius: 12px;
            }}
            """
        )
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _build_interface(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Container for glass effect
        container = QWidget()
        container.setObjectName("about_container")
        container.setStyleSheet(
            f"""
            #about_container {{
                background-color: {qss_color(THEME.obsidian_glass)};
                border-radius: 12px;
            }}
            """
        )
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 24, 16, 16)
        container_layout.setSpacing(12)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                80,
                80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setFixedSize(80, 80)
            logo_label.setStyleSheet(
                f"background-color: {qss_color(THEME.amethyst_core)}; border-radius: 40px;"
            )
        container_layout.addWidget(logo_label)

        # Title
        title_label = QLabel("Noct Map Editor")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(TYPOGRAPHY.ui_label(18, weight=600))
        title_label.setStyleSheet(f"color: {qss_color(THEME.moonstone_white)};")
        container_layout.addWidget(title_label)

        # Version
        version_label = QLabel("Version 1.0.0 (Phase 2 Migration)")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(TYPOGRAPHY.ui_label(12))
        version_label.setStyleSheet(f"color: {qss_color(THEME.ash_lavender)};")
        container_layout.addWidget(version_label)

        # License/Credits Area
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFrameStyle(0)
        self.info_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 20);
                color: {qss_color(THEME.ash_lavender)};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Inter';
                font-size: 11px;
            }}
            """
        )
        self.info_text.setText(
            "An open-source Tibia map editor reimagined with a high-performance Rust core "
            "and a modern PyQt6 shell.\n\n"
            "License: GNU GPL v3\n\n"
            "Special thanks to Remere, the original RME community, and all contributors "
            "helping bridge legacy power with modern architecture."
        )
        container_layout.addWidget(self.info_text)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()

        close_button = QPushButton("Close")
        close_button.setStyleSheet(primary_button_qss())
        close_button.setFixedWidth(100)
        close_button.setFixedHeight(32)
        close_button.clicked.connect(self.accept)
        footer.addWidget(close_button)

        container_layout.addLayout(footer)
        root.addWidget(container)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):  # noqa: N802
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
