"""Pytest configuration for Qt widget tests."""

from __future__ import annotations

import os
import shutil
import sys
import uuid
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


if find_spec("pytestqt") is None:
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication, QWidget

    @pytest.fixture(scope="session")
    def qapp() -> QApplication:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    class _FallbackQtBot:
        def __init__(self, app: QApplication) -> None:
            self._app = app
            self._widgets: list[QWidget] = []

        def addWidget(self, widget: QWidget) -> None:  # noqa: N802
            self._widgets.append(widget)

        def wait(self, ms: int) -> None:
            QTest.qWait(ms)
            self._app.processEvents()

        def cleanup(self) -> None:
            for widget in reversed(self._widgets):
                widget.close()
                widget.deleteLater()
            self._app.processEvents()

    @pytest.fixture
    def qtbot(qapp: QApplication) -> Iterator[_FallbackQtBot]:
        bot = _FallbackQtBot(qapp)
        try:
            yield bot
        finally:
            bot.cleanup()


@pytest.fixture
def settings_workspace() -> Path:
    workspace = ROOT / ".tmp-tests" / f"settings-{uuid.uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=True)
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
