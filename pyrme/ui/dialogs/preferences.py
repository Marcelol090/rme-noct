"""Preferences Dialog.

Ported from legacy C++ PreferencesWindow (app/preferences.cpp).
Provides application-wide settings via QSettings.
Follows the Noct Map Editor Design System (DESIGN.md).
"""

from __future__ import annotations

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.styles import dialog_base_qss, primary_button_qss, qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY


class _PrefsPage(QWidget):
    """Base class for a preferences tab page."""

    def load_settings(self, settings: QSettings) -> None:
        _ = settings

    def save_settings(self, settings: QSettings) -> None:
        _ = settings


class GeneralPage(_PrefsPage):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.check_updates = QCheckBox("Check for updates on startup")
        layout.addRow("", self.check_updates)

    def load_settings(self, settings: QSettings) -> None:
        self.check_updates.setChecked(settings.value("general/check_updates", type=bool))

    def save_settings(self, settings: QSettings) -> None:
        settings.setValue("general/check_updates", self.check_updates.isChecked())


class EditorPage(_PrefsPage):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.autosave = QCheckBox("Enable Autosave")
        layout.addRow("", self.autosave)

    def load_settings(self, settings: QSettings) -> None:
        self.autosave.setChecked(settings.value("editor/autosave", type=bool))

    def save_settings(self, settings: QSettings) -> None:
        settings.setValue("editor/autosave", self.autosave.isChecked())


class GraphicsPage(_PrefsPage):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.vsync = QCheckBox("Enable VSync")
        self.hardware_accel = QCheckBox("Hardware Acceleration")
        layout.addRow("", self.vsync)
        layout.addRow("", self.hardware_accel)

    def load_settings(self, settings: QSettings) -> None:
        self.vsync.setChecked(settings.value("graphics/vsync", True, type=bool))
        self.hardware_accel.setChecked(
            settings.value("graphics/hardware_accel", True, type=bool)
        )

    def save_settings(self, settings: QSettings) -> None:
        settings.setValue("graphics/vsync", self.vsync.isChecked())
        settings.setValue("graphics/hardware_accel", self.hardware_accel.isChecked())


class InterfacePage(_PrefsPage):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.dark_mode = QCheckBox("Use Dark Mode (Noct Theme)")
        self.dark_mode.setEnabled(False)  # currently hardcoded in theme
        self.dark_mode.setChecked(True)
        layout.addRow("", self.dark_mode)

    def load_settings(self, settings: QSettings) -> None:
        self.dark_mode.setChecked(settings.value("interface/dark_mode", True, type=bool))

    def save_settings(self, settings: QSettings) -> None:
        settings.setValue("interface/dark_mode", self.dark_mode.isChecked())


class PreferencesDialog(QDialog):
    """Main Preferences configuration window."""

    DIALOG_SIZE = QSize(600, 480)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setFixedSize(self.DIALOG_SIZE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self._settings = QSettings("Noct Map Editor", "Noct")

        self._apply_dialog_style()
        self._build_layout()
        self._load_settings()

    def _apply_dialog_style(self) -> None:
        """Apply Noct Map Editor dialog styling, specifically QTabWidget underlines."""
        # The QTabWidget underline style mimics the Obsidian standard.
        tab_qss = f"""
            QTabWidget::pane {{
                border: 0px;
                border-top: 1px solid {qss_color(THEME.ghost_border)};
                background: transparent;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {qss_color(THEME.ash_lavender)};
                padding: 8px 16px;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {qss_color(THEME.amethyst_core)};
                border-bottom: 2px solid {qss_color(THEME.amethyst_core)};
            }}
            QTabBar::tab:hover:!selected {{
                color: {qss_color(THEME.amethyst_rim)};
            }}
        """
        self.setStyleSheet(dialog_base_qss("") + tab_qss)

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        heading = QLabel("Preferences")
        heading.setFont(TYPOGRAPHY.dialog_heading())
        layout.addWidget(heading)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.pages: list[_PrefsPage] = [
            GeneralPage(),
            EditorPage(),
            GraphicsPage(),
            InterfacePage(),
        ]

        self.tabs.addTab(self.pages[0], "General")
        self.tabs.addTab(self.pages[1], "Editor")
        self.tabs.addTab(self.pages[2], "Graphics")
        self.tabs.addTab(self.pages[3], "Interface")

        layout.addWidget(self.tabs, 1)

        # Dialog Buttons
        btn_layout = QHBoxLayout()
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        # Style OK button as primary
        ok_btn = button_box.button(QDialogButtonBox.StandardButton.Ok)
        if ok_btn:
            ok_btn.setStyleSheet(primary_button_qss())

        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self.reject)

        apply_btn = button_box.button(QDialogButtonBox.StandardButton.Apply)
        if apply_btn:
            apply_btn.clicked.connect(self._save_settings)

        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        layout.addLayout(btn_layout)

    def _load_settings(self) -> None:
        for page in self.pages:
            page.load_settings(self._settings)

    def _save_settings(self) -> None:
        for page in self.pages:
            page.save_settings(self._settings)

    def _on_ok(self) -> None:
        self._save_settings()
        self.accept()
