"""Smoke tests for PyRME – Milestone 1 verification."""

from __future__ import annotations

import importlib


class TestRustCoreImport:
    """Test that the Rust core module can be imported and used."""

    def test_import_rme_core(self) -> None:
        """rme_core module should be importable."""
        rme_core = importlib.import_module("pyrme.rme_core")
        assert rme_core.__name__ == "pyrme.rme_core"

    def test_version_returns_string(self) -> None:
        """rme_core.version() should return a non-empty version string."""
        from pyrme import rme_core  # type: ignore[attr-defined]

        version = rme_core.version()
        assert isinstance(version, str)
        assert len(version) > 0
        assert version.startswith("0.")

    def test_build_info(self) -> None:
        """rme_core.build_info() should return build information."""
        from pyrme import rme_core  # type: ignore[attr-defined]

        info = rme_core.build_info()
        assert isinstance(info, str)
        assert "rme_core" in info
        assert "PyO3" in info


class TestPyRMEPackage:
    """Test the Python package structure."""

    def test_pyrme_version(self) -> None:
        """pyrme.__version__ should match expected version."""
        from pyrme import __version__

        assert __version__ == "0.1.0"

    def test_app_name(self) -> None:
        """pyrme.__app_name__ should be Noct Map Editor."""
        from pyrme import __app_name__

        assert __app_name__ == "Noct Map Editor"

    def test_devtools_import(self) -> None:
        """DevTools modules should be importable."""
        from pyrme.devtools.gsd.config import GSDConfig
        from pyrme.devtools.superpowers.skills_loader import SkillsLoader

        config = GSDConfig()
        assert config.mode == "solo"

        loader = SkillsLoader()
        assert isinstance(loader, SkillsLoader)

    def test_ai_assistant_import(self) -> None:
        """AI Assistant should be importable and configurable."""
        from pyrme.tools.ai_assistant import AIAssistant

        assistant = AIAssistant()
        info = assistant.info()
        assert "project_root" in info
        assert "gsd_mode" in info
        assert info["gsd_mode"] == "solo"


class TestMainWindowImport:
    """Test that UI modules can be imported (no Qt display needed)."""

    def test_main_window_class_exists(self) -> None:
        """MainWindow class should be importable."""
        # This test only checks import, not instantiation
        # (instantiation requires QApplication which needs a display)
        from pyrme.ui.main_window import MainWindow

        assert MainWindow.__name__ == "MainWindow"
        assert hasattr(MainWindow, "WINDOW_MIN_SIZE")
        assert hasattr(MainWindow, "WINDOW_DEFAULT_SIZE")
