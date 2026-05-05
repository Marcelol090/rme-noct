"""Welcome Dialog — Noct Map Editor Startup Screen.

Behavioral parity with legacy WelcomeDialog (welcome_dialog.cpp).
Single-screen dashboard: Recent Maps + Client Selection + Compatibility Status.

Design: Obsidian Cartographer tokens from .stitch/DESIGN.md.
"""

from __future__ import annotations

import os

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyrme.ui.models.startup_logic import (
    build_client_info_fields,
    build_compatibility_message,
    build_map_info_fields,
    compute_compatibility_status,
)
from pyrme.ui.models.startup_models import (
    StartupCompatibilityStatus,
    StartupConfiguredClientEntry,
    StartupInfoField,
    StartupLoadRequest,
    StartupMapPeekResult,
    StartupRecentMapEntry,
)
from pyrme.ui.styles.contracts import (
    checkbox_qss,
    dialog_base_qss,
    ghost_button_qss,
    item_view_qss,
    primary_button_qss,
    qss_color,
    section_heading_qss,
)
from pyrme.ui.theme import THEME, TYPOGRAPHY


class StartupInfoPanel(QWidget):
    """Key-value info display panel for map or client details."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(8)
        self.setStyleSheet("background: transparent;")

    def set_fields(self, fields: list[StartupInfoField]) -> None:
        """Replace current fields with new data."""
        # Clear existing
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for field in fields:
            label = QLabel(field.label)
            label.setStyleSheet(section_heading_qss())

            value_label = QLabel(field.value)
            if field.use_mono_font:
                value_label.setFont(TYPOGRAPHY.code_label(12))
            else:
                value_label.setFont(TYPOGRAPHY.ui_label(12))
            value_label.setStyleSheet(
                f"color: {qss_color(THEME.moonstone_white)}; background: transparent;"
            )
            value_label.setWordWrap(True)

            self._layout.addWidget(label)
            self._layout.addWidget(value_label)

        self._layout.addStretch()


class WelcomeDialog(QDialog):
    """Noct Map Editor Welcome / Startup Screen.

    Single-screen dashboard providing:
    - Quick Actions: New Map, Browse Map
    - Recent Maps list with peek info
    - Client version selection with auto-matching
    - Compatibility status and Load button
    """

    # Signals
    load_requested = pyqtSignal(object)  # StartupLoadRequest
    new_map_requested = pyqtSignal()
    browse_map_requested = pyqtSignal()
    preferences_requested = pyqtSignal()

    def __init__(
        self,
        recent_maps: list[StartupRecentMapEntry] | None = None,
        configured_clients: list[StartupConfiguredClientEntry] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._recent_maps = recent_maps or []
        self._configured_clients = configured_clients or []
        self._peek_cache: dict[str, StartupMapPeekResult] = {}
        self._selected_map_index: int = -1
        self._selected_client_index: int = -1
        self._has_manual_client_selection: bool = False

        self._setup_window()
        self._build_interface()
        self._populate_lists()
        self._refresh_footer_state()

    # ── Window Setup ─────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle("Noct Map Editor")
        self.setMinimumSize(QSize(1180, 720))
        self.setStyleSheet(
            dialog_base_qss()
            + f"""
            QDialog {{
                background-color: {qss_color(THEME.void_black)};
            }}
            """
        )

    # ── Interface Construction ───────────────────────────────────

    def _build_interface(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        # Header
        self._header_panel = self._build_header()
        root.addWidget(self._header_panel)

        # Content row
        content = QHBoxLayout()
        content.setSpacing(12)

        # Quick Actions
        actions_panel = self._build_quick_actions()
        content.addWidget(actions_panel)

        # Recent Maps
        recent_panel = self._build_card("RECENT MAPS")
        self._recent_list = QListWidget()
        self._recent_list.setObjectName("welcome_recent_maps_list")
        self._recent_list.setStyleSheet(item_view_qss("QListWidget"))
        self._recent_list.currentRowChanged.connect(self._on_map_selected)
        recent_panel.layout().addWidget(self._recent_list)
        content.addWidget(recent_panel, stretch=22)

        # Map Info
        map_info_panel = self._build_card("MAP DETAILS")
        self._map_info_panel = StartupInfoPanel()
        map_info_panel.layout().addWidget(self._map_info_panel)
        content.addWidget(map_info_panel, stretch=20)

        # Client Info (embedded in client card)
        client_panel = self._build_card("CLIENT VERSION")
        self._client_list = QListWidget()
        self._client_list.setObjectName("welcome_client_version_list")
        self._client_list.setStyleSheet(item_view_qss("QListWidget"))
        self._client_list.currentRowChanged.connect(self._on_client_selected)
        client_panel.layout().addWidget(self._client_list)

        self._client_info_panel = StartupInfoPanel()
        client_panel.layout().addWidget(self._client_info_panel)

        content.addWidget(client_panel, stretch=18)

        content_widget = QWidget()
        content_widget.setLayout(content)
        root.addWidget(content_widget, stretch=1)

        # Footer
        self._footer_panel = self._build_footer()
        root.addWidget(self._footer_panel)

    def _build_header(self) -> QWidget:
        panel = QWidget()
        panel.setFixedHeight(64)
        panel.setStyleSheet(
            f"background-color: {qss_color(THEME.elevated_surface)};"
            f"border-radius: 8px;"
        )

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        # Logo
        self._logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                40,
                40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._logo_label.setPixmap(pixmap)
        else:
            # Fallback if logo not found
            self._logo_label.setFixedSize(40, 40)
            self._logo_label.setStyleSheet(
                f"background-color: {qss_color(THEME.amethyst_purple)}; border-radius: 20px;"
            )
        layout.addWidget(self._logo_label)

        # Title block
        title_block = QVBoxLayout()
        self._title_label = QLabel("Noct Map Editor")
        self._title_label.setFont(TYPOGRAPHY.dialog_heading())
        self._title_label.setStyleSheet(
            f"color: {qss_color(THEME.moonstone_white)}; background: transparent;"
        )
        title_block.addWidget(self._title_label)

        self._subtitle_label = QLabel(
            "Welcome back. Pick a map, confirm the client, and load."
        )
        self._subtitle_label.setFont(TYPOGRAPHY.ui_label(9))
        self._subtitle_label.setStyleSheet(
            f"color: {qss_color(THEME.ash_lavender)}; background: transparent;"
        )
        title_block.addWidget(self._subtitle_label)
        layout.addLayout(title_block, stretch=1)

        # Preferences button
        self._preferences_button = QPushButton("⚙")
        self._preferences_button.setFixedSize(28, 28)
        self._preferences_button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {qss_color(THEME.ash_lavender)};
                font-size: 16px;
            }}
            QPushButton:hover {{
                color: {qss_color(THEME.moonstone_white)};
            }}
            """
        )
        self._preferences_button.clicked.connect(self.preferences_requested.emit)
        layout.addWidget(self._preferences_button)

        return panel

    def _build_quick_actions(self) -> QWidget:
        panel = self._build_card("QUICK ACTIONS")
        panel.setFixedWidth(170)

        self._new_map_button = QPushButton("New Map")
        self._new_map_button.setStyleSheet(primary_button_qss())
        self._new_map_button.setFixedHeight(36)
        self._new_map_button.clicked.connect(self._on_new_map_clicked)

        self._browse_map_button = QPushButton("Browse Map")
        self._browse_map_button.setStyleSheet(ghost_button_qss())
        self._browse_map_button.setFixedHeight(36)
        self._browse_map_button.clicked.connect(self._on_browse_clicked)

        panel.layout().addWidget(self._new_map_button)
        panel.layout().addSpacing(8)
        panel.layout().addWidget(self._browse_map_button)
        panel.layout().addStretch()

        return panel

    def _build_card(self, title: str) -> QWidget:
        """Create a glass-style card panel with uppercase header."""
        panel = QWidget()
        panel.setStyleSheet(
            f"""
            QWidget {{
                background-color: {qss_color(THEME.obsidian_glass)};
                border: 1px solid {qss_color(THEME.ghost_border)};
                border-top: 1px solid {qss_color(THEME.active_border)};
                border-radius: 8px;
            }}
            """
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        header = QLabel(title)
        header.setStyleSheet(section_heading_qss() + " background: transparent;")
        layout.addWidget(header)

        return panel

    def _build_footer(self) -> QWidget:
        panel = QWidget()
        panel.setFixedHeight(56)
        panel.setStyleSheet(
            f"""
            background-color: {qss_color(THEME.obsidian_glass)};
            border: 1px solid {qss_color(THEME.ghost_border)};
            border-top: 1px solid {qss_color(THEME.active_border)};
            border-radius: 8px;
            """
        )

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 0, 12, 0)

        # Exit button
        self._exit_button = QPushButton("Exit Editor")
        self._exit_button.setStyleSheet(ghost_button_qss())
        self._exit_button.setFixedHeight(32)
        self._exit_button.clicked.connect(self._on_exit_clicked)
        layout.addWidget(self._exit_button)

        layout.addStretch()

        # Status label
        self._status_label = QLabel("")
        self._status_label.setFont(TYPOGRAPHY.ui_label(12))
        self._status_label.setStyleSheet(
            f"color: {qss_color(THEME.ash_lavender)}; background: transparent;"
        )
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label, stretch=2)

        layout.addStretch()

        # Force Load checkbox
        self._force_load_checkbox = QCheckBox("Force Load")
        self._force_load_checkbox.setStyleSheet(checkbox_qss())
        self._force_load_checkbox.setEnabled(False)
        self._force_load_checkbox.stateChanged.connect(
            self._on_force_load_changed
        )
        layout.addWidget(self._force_load_checkbox)

        # Load button
        self._load_button = QPushButton("Load Map")
        self._load_button.setStyleSheet(primary_button_qss())
        self._load_button.setFixedHeight(36)
        self._load_button.setEnabled(False)
        self._load_button.clicked.connect(self._on_load_clicked)
        layout.addWidget(self._load_button)

        return panel

    # ── List Population ──────────────────────────────────────────

    def _populate_lists(self) -> None:
        self._recent_list.clear()
        for entry in self._recent_maps:
            item = QListWidgetItem(entry.path)
            if entry.modified_label:
                item.setToolTip(f"Modified: {entry.modified_label}")
            self._recent_list.addItem(item)

        self._client_list.clear()
        for entry in self._configured_clients:
            item = QListWidgetItem(f"{entry.name}")
            item.setToolTip(entry.client_path)
            self._client_list.addItem(item)

    # ── Selection Logic ──────────────────────────────────────────

    def set_selected_map_index(self, index: int) -> None:
        """Set selected map index and trigger auto-client match."""
        if index < 0 or index >= len(self._recent_maps):
            self._selected_map_index = -1
            self._recent_list.setCurrentRow(-1)
        else:
            self._selected_map_index = index
            self._recent_list.setCurrentRow(index)
            path = self._recent_maps[index].path
            if path in self._peek_cache:
                self._auto_select_matching_client()

        self._refresh_map_info()
        self._refresh_footer_state()

    def set_selected_client_index(
        self, index: int, *, manual: bool = False
    ) -> None:
        """Set selected client index."""
        if index < 0 or index >= len(self._configured_clients):
            self._selected_client_index = -1
            self._client_list.setCurrentRow(-1)
        else:
            self._selected_client_index = index
            self._client_list.setCurrentRow(index)

        self._has_manual_client_selection = manual
        self._refresh_client_info()
        self._refresh_footer_state()

    def _auto_select_matching_client(self) -> None:
        """Port of legacy WelcomeDialog::AutoSelectMatchingClient()."""
        if self._has_manual_client_selection or self._selected_map_index == -1:
            return

        peek = self._get_selected_map_info()
        if peek is None or peek.has_error:
            return

        # Exact match: OTB major + minor
        for i, client in enumerate(self._configured_clients):
            if (
                client.otb_major == peek.items_major_version
                and client.otb_minor == peek.items_minor_version
            ):
                self._selected_client_index = i
                self._client_list.setCurrentRow(i)
                self._refresh_client_info()
                return

        # Fallback: minor-only match
        for i, client in enumerate(self._configured_clients):
            if client.otb_minor == peek.items_minor_version:
                self._selected_client_index = i
                self._client_list.setCurrentRow(i)
                self._refresh_client_info()
                return

    # ── Info Refresh ─────────────────────────────────────────────

    def _get_selected_map_info(self) -> StartupMapPeekResult | None:
        if self._selected_map_index < 0:
            return None
        path = self._recent_maps[self._selected_map_index].path
        return self._peek_cache.get(path)

    def _get_selected_client(self) -> StartupConfiguredClientEntry | None:
        if self._selected_client_index < 0:
            return None
        return self._configured_clients[self._selected_client_index]

    def _refresh_map_info(self) -> None:
        peek = self._get_selected_map_info()
        fields = build_map_info_fields(peek)
        self._map_info_panel.set_fields(fields)

    def _refresh_client_info(self) -> None:
        client = self._get_selected_client()
        fields = build_client_info_fields(client)
        self._client_info_panel.set_fields(fields)

    def _refresh_footer_state(self) -> None:
        peek = self._get_selected_map_info()
        client = self._get_selected_client()
        force = self._force_load_checkbox.isChecked()

        status = compute_compatibility_status(peek, client, force)
        message = build_compatibility_message(
            status,
            peek,
            client,
            has_maps=len(self._recent_maps) > 0,
        )

        self._status_label.setText(message)

        # Status color
        color_map = {
            StartupCompatibilityStatus.COMPATIBLE: THEME.verdant_green,
            StartupCompatibilityStatus.FORCE_REQUIRED: THEME.amber_caution,
            StartupCompatibilityStatus.FORCED: THEME.amber_caution,
            StartupCompatibilityStatus.MAP_ERROR: THEME.ember_red,
            StartupCompatibilityStatus.MISSING_SELECTION: THEME.ash_lavender,
        }
        color = color_map.get(status, THEME.ash_lavender)
        self._status_label.setStyleSheet(
            f"color: {qss_color(color)}; background: transparent;"
        )

        # Force Load checkbox
        mismatch = status in (
            StartupCompatibilityStatus.FORCE_REQUIRED,
            StartupCompatibilityStatus.FORCED,
        )
        if not mismatch and self._force_load_checkbox.isChecked():
            self._force_load_checkbox.setChecked(False)
        self._force_load_checkbox.setEnabled(mismatch)

        # Load button
        can_load = status in (
            StartupCompatibilityStatus.COMPATIBLE,
            StartupCompatibilityStatus.FORCED,
        )
        self._load_button.setEnabled(can_load)

    # ── Event Handlers ───────────────────────────────────────────

    def _on_map_selected(self, row: int) -> None:
        self.set_selected_map_index(row)

    def _on_client_selected(self, row: int) -> None:
        self.set_selected_client_index(row, manual=True)

    def _on_force_load_changed(self) -> None:
        self._refresh_footer_state()

    def _on_load_clicked(self) -> None:
        if self._selected_map_index < 0 or self._selected_client_index < 0:
            return
        client = self._get_selected_client()
        if client is None:
            return

        request = StartupLoadRequest(
            map_path=self._recent_maps[self._selected_map_index].path,
            client_version_id=client.version_id,
            force_client_mismatch=self._force_load_checkbox.isChecked(),
        )
        self.load_requested.emit(request)

    def _on_new_map_clicked(self) -> None:
        self.new_map_requested.emit()

    def _on_browse_clicked(self) -> None:
        self.browse_map_requested.emit()

    def _on_exit_clicked(self) -> None:
        self.close()
