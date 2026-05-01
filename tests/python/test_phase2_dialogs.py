import pytest
from PyQt6.QtCore import Qt
from pyrme.ui.dialogs.about import AboutDialog
from pyrme.ui.dialogs.preferences import PreferencesDialog

def test_about_dialog_init(qtbot):
    dialog = AboutDialog()
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "About Noct Map Editor"
    assert dialog.windowFlags() & Qt.WindowType.FramelessWindowHint

def test_preferences_dialog_init(qtbot):
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "Preferences"
    
    # Check sidebar existence
    assert hasattr(dialog, "sidebar")
    assert dialog.sidebar.count() > 0
    
    # Check page switching
    initial_index = dialog.pages.currentIndex()
    dialog.sidebar.setCurrentRow(1)
    assert dialog.pages.currentIndex() == 1
    assert dialog.pages.currentIndex() != initial_index
