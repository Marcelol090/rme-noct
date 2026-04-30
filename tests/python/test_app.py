from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication

from pyrme.app import create_app, run_app


def test_run_app(qapp, monkeypatch):
    """Test that run_app creates the MainWindow and starts the event loop."""
    # Mock the imports locally within the run_app namespace so it doesn't try to instantiate MainWindow
    mock_main_window_cls = MagicMock()
    mock_window_instance = MagicMock()
    mock_main_window_cls.return_value = mock_window_instance

    # We patch the module where the import happens
    import pyrme.ui.main_window

    monkeypatch.setattr(pyrme.ui.main_window, "MainWindow", mock_main_window_cls)

    # Mock QApplication
    app_mock = MagicMock(spec=QApplication)
    app_mock.exec.return_value = 0

    # Call the function
    exit_code = run_app(app_mock)

    # Assertions
    mock_main_window_cls.assert_called_once()
    mock_window_instance.show.assert_called_once()
    app_mock.exec.assert_called_once()
    assert exit_code == 0


def test_create_app(qapp):
    """Test that create_app configures the QApplication correctly."""
    # To prevent segfaults when PyQt6 tries to initialize multiple QApplication instances or interacts weirdly with pytest-qt's qapp fixture,
    # we will patch QApplication to avoid real instantiation

    with patch("pyrme.app.QApplication") as mock_qapp_cls:
        app_mock = MagicMock()
        mock_qapp_cls.return_value = app_mock

        with patch("pyrme.app._build_dark_palette") as mock_build_palette:
            palette_mock = MagicMock()
            mock_build_palette.return_value = palette_mock

            with patch("pyrme.app._load_stylesheet") as mock_load_stylesheet:
                mock_load_stylesheet.return_value = "mock stylesheet"

                with patch("pyrme.app.QFont") as mock_qfont:
                    font_mock = MagicMock()
                    mock_qfont.return_value = font_mock

                    app = create_app(["test_app"])

                    assert app is app_mock
                    mock_qapp_cls.assert_called_once_with(["test_app"])

                    # Usually imported from __app_name__ in pyrme/__init__.py
                    app_mock.setApplicationName.assert_called_once()
                    app_mock.setApplicationVersion.assert_called_once()
                    app_mock.setOrganizationName.assert_called_with("Noct Map Editor")
                    app_mock.setOrganizationDomain.assert_called_with(
                        "noctmapeditor.dev"
                    )

                    mock_build_palette.assert_called_once()
                    app_mock.setPalette.assert_called_once_with(palette_mock)

                    mock_load_stylesheet.assert_called_once()
                    app_mock.setStyleSheet.assert_called_once_with("mock stylesheet")

                    mock_qfont.assert_called_once_with("Inter", 10)
                    font_mock.setHintingPreference.assert_called_once()
                    app_mock.setFont.assert_called_once_with(font_mock)


def test_create_app_no_stylesheet(qapp):
    """Test that create_app handles missing stylesheet gracefully."""
    with patch("pyrme.app.QApplication") as mock_qapp_cls:
        app_mock = MagicMock()
        mock_qapp_cls.return_value = app_mock

        with patch("pyrme.app._build_dark_palette"):
            with patch("pyrme.app._load_stylesheet") as mock_load_stylesheet:
                mock_load_stylesheet.return_value = ""  # No stylesheet loaded

                with patch("pyrme.app.QFont"):
                    app = create_app(["test_app"])

                    assert app is app_mock
                    mock_load_stylesheet.assert_called_once()
                    app_mock.setStyleSheet.assert_not_called()


def test_load_stylesheet():
    """Test loading the QSS stylesheet."""
    from pyrme.app import _load_stylesheet

    with patch("pyrme.app.Path.exists") as mock_exists:
        with patch("pyrme.app.Path.read_text") as mock_read_text:
            mock_exists.return_value = True
            mock_read_text.return_value = "body { color: black; }"

            stylesheet = _load_stylesheet()

            assert stylesheet == "body { color: black; }"
            mock_exists.assert_called_once()
            mock_read_text.assert_called_once_with(encoding="utf-8")


def test_load_stylesheet_missing():
    """Test loading the QSS stylesheet when missing."""
    from pyrme.app import _load_stylesheet

    with patch("pyrme.app.Path.exists") as mock_exists:
        mock_exists.return_value = False

        stylesheet = _load_stylesheet()

        assert stylesheet == ""
        mock_exists.assert_called_once()


def test_build_dark_palette():
    """Test building the dark palette."""
    from PyQt6.QtGui import QPalette

    from pyrme.app import _build_dark_palette

    palette = _build_dark_palette()

    assert isinstance(palette, QPalette)
    # Check a few specific colors
    assert palette.color(QPalette.ColorRole.Window).name() == "#0a0a12"
    assert palette.color(QPalette.ColorRole.WindowText).name() == "#e8e6f0"


def test_create_app_no_args(monkeypatch):
    """Test create_app when no argv is provided (uses sys.argv)."""
    import sys

    from pyrme.app import create_app

    with patch("pyrme.app.QApplication") as mock_qapp_cls:
        app_mock = MagicMock()
        mock_qapp_cls.return_value = app_mock

        with (
            patch("pyrme.app._build_dark_palette"),
            patch("pyrme.app._load_stylesheet"),patch("pyrme.app.QFont")
        ):
            app = create_app()

            assert app is app_mock
            mock_qapp_cls.assert_called_once_with(sys.argv)
