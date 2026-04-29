import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor
import sys

def test_selection_and_invalid_overlays():
    """GREEN: test selected and invalid tile overlays in RendererHostCanvasWidget"""
    from pyrme.ui.theme import THEME
    
    # Verify theme colors match design system requirements (M023-T06)
    # Selection: White (0.2 alpha)
    assert THEME.selection_overlay.red() == 255
    assert THEME.selection_overlay.alpha() == int(255 * 0.2)
    
    # Invalid: Ember Red (0.4 alpha)
    assert THEME.invalid_overlay.name() == "#e05c5c"
    assert THEME.invalid_overlay.alpha() == int(255 * 0.4)
    
    # Amethyst Glow: Core (0.15 alpha)
    assert THEME.amethyst_glow.alpha() == int(255 * 0.15)
