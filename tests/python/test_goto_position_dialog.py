from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from PyQt6.QtCore import QSettings

from pyrme.ui.dialogs.goto_position import GotoPositionDialog

if TYPE_CHECKING:
    from pathlib import Path


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _dialog_with_recent_settings(qtbot, settings: QSettings) -> GotoPositionDialog:
    dialog = GotoPositionDialog()
    qtbot.addWidget(dialog)
    dialog._settings = settings
    return dialog


@pytest.mark.parametrize(
    "raw",
    [
        "INVALID_JSON_HERE",
        json.dumps(["not", "a", "position"]),
        json.dumps([[100, 200]]),
        json.dumps([[100, 200, "7"]]),
        json.dumps({"x": 100, "y": 200, "z": 7}),
    ],
)
def test_goto_position_invalid_recent_data_falls_back_to_empty(
    qtbot,
    settings_workspace: Path,
    raw: str,
) -> None:
    settings = _build_settings(settings_workspace, "goto-invalid-recent.ini")
    settings.setValue("recent_positions/list", raw)

    dialog = _dialog_with_recent_settings(qtbot, settings)
    dialog._load_recent_positions()

    assert dialog._recent == []
    assert dialog._recent_container.count() == 0


def test_goto_position_valid_recent_data_loads(
    qtbot,
    settings_workspace: Path,
) -> None:
    valid_data = [[100, 200, 7], [300, 400, 8]]
    settings = _build_settings(settings_workspace, "goto-valid-recent.ini")
    settings.setValue("recent_positions/list", json.dumps(valid_data))

    dialog = _dialog_with_recent_settings(qtbot, settings)
    dialog._load_recent_positions()

    assert len(dialog._recent) == 2
    assert dialog._recent[0] == (100, 200, 7)
    assert dialog._recent[1] == (300, 400, 8)
    assert dialog._recent_container.count() == 2
