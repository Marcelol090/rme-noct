from __future__ import annotations

import builtins
from unittest.mock import MagicMock, patch

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

from pyrme.app import _build_dark_palette, _load_stylesheet, create_app, run_app


def test_load_stylesheet():
    stylesheet = _load_stylesheet()
    assert isinstance(stylesheet, str)


def test_build_dark_palette():
    palette = _build_dark_palette()
    assert isinstance(palette, QPalette)


def test_create_app():
    # Store original Qt instance if any to prevent issues
    _old_app = QApplication.instance()

    # We can't actually test create_app fully isolated if a QApplication
    # already exists in the test runner, but we can verify it sets properties
    # by mocking QApplication constructor
    with patch("pyrme.app.QApplication") as mock_qapp_cls:
        mock_app_instance = MagicMock()
        mock_qapp_cls.return_value = mock_app_instance

        _app = create_app(["test_app"])

        mock_qapp_cls.assert_called_once_with(["test_app"])
        mock_app_instance.setApplicationName.assert_called_once_with("Noct Map Editor")
        mock_app_instance.setOrganizationName.assert_called_once_with("Noct Map Editor")
        mock_app_instance.setOrganizationDomain.assert_called_once_with("noctmapeditor.dev")
        mock_app_instance.setPalette.assert_called_once()
        mock_app_instance.setFont.assert_called_once()


def test_run_app():
    mock_app = MagicMock(spec=QApplication)
    mock_app.exec.return_value = 42

    original_import = builtins.__import__

    def mock_import(name, my_globals=None, my_locals=None, fromlist=(), level=0):
        if name == "pyrme.ui.main_window" and "MainWindow" in fromlist:
            mock_module = MagicMock()
            mock_main_window_cls = MagicMock()
            mock_window_instance = MagicMock()
            mock_main_window_cls.return_value = mock_window_instance
            mock_module.MainWindow = mock_main_window_cls

            # Store instance so we can verify
            mock_import.mock_main_window_cls = mock_main_window_cls
            mock_import.mock_window_instance = mock_window_instance

            return mock_module
        return original_import(name, my_globals, my_locals, fromlist, level)

    with patch("builtins.__import__", side_effect=mock_import):
        result = run_app(mock_app)

        assert result == 42
        mock_import.mock_main_window_cls.assert_called_once()
        mock_import.mock_window_instance.show.assert_called_once()
        mock_app.exec.assert_called_once()
