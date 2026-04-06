"""Noct Map Editor Application setup – QApplication with dark theme."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

from pyrme import __app_name__, __version__


def _load_stylesheet() -> str:
    """Load the dark theme QSS stylesheet."""
    qss_path = Path(__file__).parent / "ui" / "styles" / "dark_theme.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


def _build_dark_palette() -> QPalette:
    """Build a dark-mode QPalette aligned with .stitch/DESIGN.md tokens."""
    palette = QPalette()

    # DESIGN.md token mapping
    void_black = QColor("#0A0A12")           # Void Black
    lifted = QColor(255, 255, 255, 18)       # Lifted Glass (rgba 0.07)
    moonstone = QColor("#E8E6F0")            # Moonstone White
    ash_lavender = QColor("#9490A8")         # Ash Lavender
    amethyst = QColor("#7C5CFC")             # Amethyst Core
    deep_amethyst = QColor("#4F3DB5")        # Deep Amethyst
    ember_red = QColor("#E05C5C")            # Ember Red
    muted_slate = QColor("#4A4860")          # Muted Slate

    # Window backgrounds
    palette.setColor(QPalette.ColorRole.Window, void_black)
    palette.setColor(QPalette.ColorRole.WindowText, moonstone)
    palette.setColor(QPalette.ColorRole.Base, void_black)
    palette.setColor(QPalette.ColorRole.AlternateBase, lifted)

    # Text
    palette.setColor(QPalette.ColorRole.Text, moonstone)
    palette.setColor(QPalette.ColorRole.PlaceholderText, ash_lavender)
    palette.setColor(QPalette.ColorRole.BrightText, ember_red)

    # Buttons
    palette.setColor(QPalette.ColorRole.Button, lifted)
    palette.setColor(QPalette.ColorRole.ButtonText, moonstone)

    # Highlights & accents
    palette.setColor(QPalette.ColorRole.Highlight, amethyst)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    # Tooltips
    palette.setColor(QPalette.ColorRole.ToolTipBase, lifted)
    palette.setColor(QPalette.ColorRole.ToolTipText, moonstone)

    # Links
    palette.setColor(QPalette.ColorRole.Link, amethyst)
    palette.setColor(QPalette.ColorRole.LinkVisited, deep_amethyst)

    # Disabled state
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, muted_slate
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, muted_slate
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, muted_slate
    )

    return palette


def create_app(argv: list[str] | None = None) -> QApplication:
    """Create and configure the QApplication with dark theme."""
    if argv is None:
        argv = sys.argv

    # High-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Noct Map Editor")
    app.setOrganizationDomain("noctmapeditor.dev")

    # Apply dark palette
    app.setPalette(_build_dark_palette())

    # Apply QSS stylesheet
    stylesheet = _load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Set default font
    font = QFont("Inter", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    return app


def run_app(app: QApplication) -> int:
    """Create the main window and start the event loop."""
    from pyrme.ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    return app.exec()
