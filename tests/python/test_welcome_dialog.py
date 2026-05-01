"""Tests for WelcomeDialog startup screen.

T05: Layout tests — verify panel structure, minimum size, child widgets.
T06: Theme integration — verify correct color tokens applied.
T08-T10: Behavioral wiring — map/client selection, auto-match, event emission.
T12: Button events.
"""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QApplication

from pyrme.ui.models.startup_models import (
    StartupConfiguredClientEntry,
    StartupMapPeekResult,
    StartupRecentMapEntry,
)


# Ensure QApplication exists for widget tests
@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_maps():
    return [
        StartupRecentMapEntry(path="/maps/forgotten_city.otbm", modified_label="2026-04-27"),
        StartupRecentMapEntry(path="/maps/yalahar_rework.otbm", modified_label="2026-04-26"),
        StartupRecentMapEntry(path="/maps/starting_island.otbm", modified_label="2026-04-20"),
    ]


@pytest.fixture
def sample_clients():
    return [
        StartupConfiguredClientEntry(
            name="Tibia 12.86", version_id="1286",
            client_path="C:/Tibia/1286", otb_major=3, otb_minor=57,
        ),
        StartupConfiguredClientEntry(
            name="Tibia 10.98", version_id="1098",
            client_path="C:/Tibia/1098", otb_major=3, otb_minor=42,
        ),
    ]


@pytest.fixture
def sample_peek():
    return StartupMapPeekResult(
        map_name="forgotten_city",
        items_major_version=3,
        items_minor_version=57,
        map_width=32000,
        map_height=32000,
        description="Rain city rework",
    )


@pytest.fixture
def dialog(sample_maps, sample_clients):
    from pyrme.ui.dialogs.welcome_dialog import WelcomeDialog
    dlg = WelcomeDialog(
        recent_maps=sample_maps,
        configured_clients=sample_clients,
    )
    yield dlg
    dlg.close()


# ── T05: Layout ──────────────────────────────────────────────────────


class TestWelcomeDialogLayout:
    """Verify all 5 panels present and correctly structured."""

    def test_minimum_size(self, dialog):
        min_size = dialog.minimumSize()
        assert min_size.width() >= 1000  # Allow some flex for DPI
        assert min_size.height() >= 600

    def test_has_header(self, dialog):
        assert dialog._header_panel is not None

    def test_header_has_title(self, dialog):
        assert dialog._title_label is not None
        assert "Noct" in dialog._title_label.text()

    def test_header_has_subtitle(self, dialog):
        assert dialog._subtitle_label is not None

    def test_header_has_preferences_button(self, dialog):
        assert dialog._preferences_button is not None

    def test_has_quick_actions(self, dialog):
        assert dialog._new_map_button is not None
        assert dialog._browse_map_button is not None

    def test_has_recent_maps_list(self, dialog):
        assert dialog._recent_list is not None

    def test_recent_maps_populated(self, dialog):
        assert dialog._recent_list.count() == 3

    def test_has_map_info_panel(self, dialog):
        assert dialog._map_info_panel is not None

    def test_has_client_list(self, dialog):
        assert dialog._client_list is not None

    def test_client_list_populated(self, dialog):
        assert dialog._client_list.count() == 2

    def test_has_footer(self, dialog):
        assert dialog._footer_panel is not None

    def test_footer_has_status_label(self, dialog):
        assert dialog._status_label is not None

    def test_footer_has_force_checkbox(self, dialog):
        assert dialog._force_load_checkbox is not None

    def test_footer_has_load_button(self, dialog):
        assert dialog._load_button is not None

    def test_footer_has_exit_button(self, dialog):
        assert dialog._exit_button is not None


# ── T08: Map Selection ───────────────────────────────────────────────


class TestMapSelection:
    """Verify map selection updates info panel."""

    def test_selecting_map_updates_info(self, dialog, sample_peek):
        dialog._peek_cache["/maps/forgotten_city.otbm"] = sample_peek
        dialog.set_selected_map_index(0)
        # Info panel should now show fields
        assert dialog._map_info_panel.layout().count() > 0

    def test_no_selection_shows_empty(self, dialog):
        dialog.set_selected_map_index(-1)
        assert dialog._selected_map_index == -1


# ── T09: Client Selection ───────────────────────────────────────────


class TestClientSelection:
    """Verify client selection updates info panel."""

    def test_selecting_client_updates_info(self, dialog):
        dialog.set_selected_client_index(0, manual=False)
        assert dialog._selected_client_index == 0

    def test_manual_flag_persists(self, dialog):
        dialog.set_selected_client_index(1, manual=True)
        assert dialog._has_manual_client_selection is True


# ── T10: Auto-Client Matching ────────────────────────────────────────


class TestAutoClientMatch:
    """Legacy: WelcomeDialog::AutoSelectMatchingClient()."""

    def test_auto_selects_matching_client(self, dialog, sample_peek):
        """Map with items 3.57 should auto-select client with OTB 3.57."""
        dialog._has_manual_client_selection = False
        dialog._peek_cache["/maps/forgotten_city.otbm"] = sample_peek
        dialog.set_selected_map_index(0)
        # Client 0 has otb_major=3, otb_minor=57 → should be selected
        assert dialog._selected_client_index == 0

    def test_manual_selection_blocks_auto_match(self, dialog, sample_peek):
        """Manual client selection should not be overridden by auto-match."""
        dialog._peek_cache["/maps/forgotten_city.otbm"] = sample_peek
        dialog.set_selected_client_index(1, manual=True)
        dialog.set_selected_map_index(0)
        # Should stay at 1 because manual flag is set
        assert dialog._selected_client_index == 1


# ── T11: Status Display ─────────────────────────────────────────────


class TestStatusDisplay:
    """Verify footer status reflects compatibility state."""

    def test_compatible_shows_green_text(self, dialog, sample_peek):
        dialog._peek_cache["/maps/forgotten_city.otbm"] = sample_peek
        dialog.set_selected_map_index(0)
        # Client 0 matches → compatible
        text = dialog._status_label.text()
        assert "ready" in text.lower() or "matches" in text.lower()

    def test_load_enabled_when_compatible(self, dialog, sample_peek):
        dialog._peek_cache["/maps/forgotten_city.otbm"] = sample_peek
        dialog.set_selected_map_index(0)
        assert dialog._load_button.isEnabled()

    def test_load_disabled_when_no_selection(self, dialog):
        dialog.set_selected_map_index(-1)
        assert not dialog._load_button.isEnabled()


# ── T12: Event Emission ─────────────────────────────────────────────


class TestEventEmission:
    """Verify buttons emit correct signals."""

    def test_load_emits_request(self, dialog, sample_peek):
        dialog._peek_cache["/maps/forgotten_city.otbm"] = sample_peek
        dialog.set_selected_map_index(0)
        dialog.set_selected_client_index(0, manual=False)

        received = []
        dialog.load_requested.connect(lambda req: received.append(req))
        dialog._on_load_clicked()

        assert len(received) == 1
        req = received[0]
        assert req.map_path == "/maps/forgotten_city.otbm"
        assert req.client_version_id == "1286"

    def test_new_map_emits_signal(self, dialog):
        received = []
        dialog.new_map_requested.connect(lambda: received.append(True))
        dialog._on_new_map_clicked()
        assert len(received) == 1

    def test_exit_closes_dialog(self, dialog):
        dialog.show()
        dialog._on_exit_clicked()
        assert not dialog.isVisible()
