"""Integration tests for WelcomeDialog in MainWindow flow.

T13: Integration with EditorShellState.
Verify WelcomeDialog launches on startup, and its signals
(load, new, exit) correctly control the main window state.
"""

from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from pyrme.ui.dialogs.welcome_dialog import WelcomeDialog
from pyrme.ui.main_window import MainWindow
from pyrme.ui.models.startup_models import StartupLoadRequest


@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def window():
    """Create a headless MainWindow for testing."""
    win = MainWindow(enable_docks=False)
    yield win
    win.close()


# ── T13: Integration Tests ──────────────────────────────────────────


class TestWelcomeDialogIntegration:
    """Verify MainWindow <-> WelcomeDialog interaction."""

    def test_shows_welcome_dialog_on_startup(self, window):
        """MainWindow should show the WelcomeDialog upon request."""
        # Note: We don't auto-show in __init__ because tests need to run headless.
        # We call a dedicated startup method.
        window.show_startup_dashboard()

        # Dialog should be created and shown
        assert window._welcome_dialog is not None
        assert window._welcome_dialog.isVisible()

    def test_new_map_signal_creates_tab(self, window):
        """WelcomeDialog 'new map' should trigger file_new action."""
        window.show_startup_dashboard()
        dialog = window._welcome_dialog

        # We expect file_new_action to be triggered (it's currently a stub in MainWindow)
        called = []
        window.file_new_action.triggered.connect(lambda: called.append(True))

        dialog.new_map_requested.emit()

        # Dialog should close
        assert not dialog.isVisible()
        # Action should be triggered
        assert len(called) >= 1

    def test_load_signal_triggers_open(self, window):
        """WelcomeDialog 'load' should trigger map load process."""
        window.show_startup_dashboard()
        dialog = window._welcome_dialog

        # Mock the internal open implementation
        received_paths = []
        window._open_map_file = lambda path: received_paths.append(path)

        req = StartupLoadRequest(
            map_path="/maps/test.otbm",
            client_version_id="1098"
        )
        dialog.load_requested.emit(req)

        assert not dialog.isVisible()
        assert len(received_paths) == 1
        assert received_paths[0] == "/maps/test.otbm"

    def test_browse_signal_triggers_file_dialog(self, window):
        """WelcomeDialog 'browse' should trigger file open dialog."""
        window.show_startup_dashboard()
        dialog = window._welcome_dialog

        # Trigger file open action (mocked or just checking it calls the right method)
        # We can intercept file_open_action
        called = []
        window.file_open_action.triggered.connect(lambda: called.append(True))

        dialog.browse_map_requested.emit()

        # Since Browse map is basically "File -> Open", it should trigger the action
        # and then close the dialog (or wait for the open result).
        # Actually, in legacy RME, "Browse Map" closes dialog and opens file picker.
        assert not dialog.isVisible()
        assert len(called) >= 1
