from __future__ import annotations

import json
import pytest
from PyQt6.QtCore import QSettings
from pyrme.ui.dialogs.goto_position import GotoPositionDialog

@pytest.fixture
def mock_settings():
    """Provides a fresh QSettings object for testing and cleans it up after."""
    settings = QSettings("NoctTest", "GotoPositionTest")
    settings.clear()
    yield settings
    settings.clear()

def test_goto_position_parse_error_fallback(qtbot, mock_settings):
    """Test that invalid JSON in QSettings falls back to an empty list."""
    mock_settings.setValue("recent_positions/list", "INVALID_JSON_HERE")

    dialog = GotoPositionDialog()
    qtbot.addWidget(dialog)
    dialog._settings = mock_settings
    dialog._load_recent_positions()

    assert dialog._recent == []
    assert dialog._recent_container.count() == 0

def test_goto_position_type_error_fallback(qtbot, mock_settings):
    """Test that valid JSON but wrong structure falls back to an empty list."""
    # List of strings instead of coordinates should raise TypeError or ValueError
    mock_settings.setValue("recent_positions/list", '["not", "a", "tuple"]')

    dialog = GotoPositionDialog()
    qtbot.addWidget(dialog)
    dialog._settings = mock_settings
    dialog._load_recent_positions()

    assert dialog._recent == []
    assert dialog._recent_container.count() == 0

def test_goto_position_value_error_wrong_length(qtbot, mock_settings):
    """Test that coordinate lists of the wrong length fall back to an empty list."""
    # Two integers instead of three
    mock_settings.setValue("recent_positions/list", '[[100, 200]]')

    dialog = GotoPositionDialog()
    qtbot.addWidget(dialog)
    dialog._settings = mock_settings
    dialog._load_recent_positions()

    assert dialog._recent == []
    assert dialog._recent_container.count() == 0

def test_goto_position_type_error_wrong_type(qtbot, mock_settings):
    """Test that coordinate lists with non-integers fall back to an empty list."""
    # A string inside the coordinate list
    mock_settings.setValue("recent_positions/list", '[[100, 200, "7"]]')

    dialog = GotoPositionDialog()
    qtbot.addWidget(dialog)
    dialog._settings = mock_settings
    dialog._load_recent_positions()

    assert dialog._recent == []
    assert dialog._recent_container.count() == 0

def test_goto_position_valid_data_loads(qtbot, mock_settings):
    """Test that valid JSON data is loaded correctly."""
    valid_data = [[100, 200, 7], [300, 400, 8]]
    mock_settings.setValue("recent_positions/list", json.dumps(valid_data))

    dialog = GotoPositionDialog()
    qtbot.addWidget(dialog)
    dialog._settings = mock_settings
    dialog._load_recent_positions()

    assert len(dialog._recent) == 2
    assert dialog._recent[0] == (100, 200, 7)
    assert dialog._recent[1] == (300, 400, 8)
    assert dialog._recent_container.count() == 2
