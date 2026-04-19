"""About dialog for Noct Map Editor.

Ported from legacy C++ AboutWindow (ui/about_window.h/.cpp).
Displays the Noct wolf logo, version, credits, and license info.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme import __app_name__, __version__
from pyrme.ui.theme import THEME, TYPOGRAPHY

# Resolve logo path relative to package
_LOGO_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "logo" / "noct_wolf.png"


class AboutDialog(QDialog):
    """About dialog showing Noct branding, credits, and license.

    Mirrors legacy C++ AboutWindow with:
    - Wolf + amethyst moon logo
    - App name + version
    - Rust core build info
    - Credits and GPL v3 link
    """

    DIALOG_SIZE = QSize(480, 420)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {__app_name__}")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self._apply_style()
        self._build_layout()

    def _apply_style(self) -> None:
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME.void_black.name()};
                color: {THEME.moonstone_white.name()};
            }}
            QLabel {{
                color: {THEME.moonstone_white.name()};
                background: transparent;
            }}
        """)

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Wolf logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if _LOGO_PATH.exists():
            pixmap = QPixmap(str(_LOGO_PATH))
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    160, 160,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                logo_label.setPixmap(scaled)
            else:
                logo_label.setText("🐺")
                logo_label.setStyleSheet("font-size: 64px;")
        else:
            logo_label.setText("🐺")
            logo_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(logo_label)

        # App name
        name_label = QLabel(__app_name__)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_font = TYPOGRAPHY.ui_label(20)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {THEME.moonstone_white.name()};")
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"v{__version__}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(TYPOGRAPHY.coordinate_display())
        version_label.setStyleSheet(f"color: {THEME.ash_lavender.name()};")
        layout.addWidget(version_label)

        # Rust core info
        rust_info = self._get_rust_core_info()
        rust_label = QLabel(rust_info)
        rust_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rust_label.setFont(TYPOGRAPHY.item_id())
        rust_label.setStyleSheet(f"color: {THEME.muted_slate.name()};")
        layout.addWidget(rust_label)

        layout.addSpacing(16)

        # Credits
        credits_text = (
            "A modern Tibia map editor built with Python, Rust, and PyQt6.\n"
            "Based on Remere's Map Editor (Redux).\n\n"
            "Noct Map Editor is free software under the GNU GPL v3."
        )
        credits_label = QLabel(credits_text)
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setWordWrap(True)
        credits_label.setFont(TYPOGRAPHY.ui_label(11))
        credits_label.setStyleSheet(f"color: {THEME.ash_lavender.name()};")
        layout.addWidget(credits_label)

        layout.addStretch()

        # Close button
        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME.amethyst_core.name()};
                border: none;
                border-radius: 6px;
                color: {THEME.moonstone_white.name()};
                padding: 6px 24px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {THEME.deep_amethyst.name()};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        footer.addStretch()
        layout.addLayout(footer)

    @staticmethod
    def _get_rust_core_info() -> str:
        """Try to get Rust core build info."""
        try:
            import rme_core  # type: ignore[import-not-found]
            version = getattr(rme_core, "__version__", "unknown")
            return f"Rust core: rme_core v{version}"
        except ImportError:
            return "Rust core: not available (dev mode)"
