from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

from pyrme import __app_name__, __version__
from pyrme.app import _build_dark_palette, _load_stylesheet, create_app, run_app


def test_load_stylesheet_returns_text() -> None:
    stylesheet = _load_stylesheet()
    assert isinstance(stylesheet, str)


def test_build_dark_palette_returns_palette() -> None:
    palette = _build_dark_palette()
    assert isinstance(palette, QPalette)


def test_create_app_configures_qapplication() -> None:
    palette = MagicMock(spec=QPalette)
    with (
        patch("pyrme.app.QApplication") as qapplication_cls,
        patch("pyrme.app._build_dark_palette", return_value=palette),
        patch("pyrme.app._load_stylesheet", return_value="QWidget {}"),
    ):
        app = MagicMock(spec=QApplication)
        qapplication_cls.return_value = app

        result = create_app(["test_app"])

    assert result is app
    qapplication_cls.assert_called_once_with(["test_app"])
    app.setApplicationName.assert_called_once_with(__app_name__)
    app.setApplicationVersion.assert_called_once_with(__version__)
    app.setOrganizationName.assert_called_once_with("Noct Map Editor")
    app.setOrganizationDomain.assert_called_once_with("noctmapeditor.dev")
    app.setPalette.assert_called_once_with(palette)
    app.setStyleSheet.assert_called_once_with("QWidget {}")
    app.setFont.assert_called_once()


def test_run_app_shows_main_window_and_returns_exit_code(monkeypatch) -> None:
    mock_app = MagicMock(spec=QApplication)
    mock_app.exec.return_value = 42

    main_window_module = ModuleType("pyrme.ui.main_window")
    main_window_cls = MagicMock()
    window = MagicMock()
    main_window_cls.return_value = window
    main_window_module.MainWindow = main_window_cls
    monkeypatch.setitem(sys.modules, "pyrme.ui.main_window", main_window_module)

    result = run_app(mock_app)

    assert result == 42
    main_window_cls.assert_called_once_with()
    window.show.assert_called_once_with()
    mock_app.exec.assert_called_once_with()
