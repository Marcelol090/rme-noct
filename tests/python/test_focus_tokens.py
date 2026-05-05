from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QFocusEvent
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from pyrme.ui.components.glass import GlassPanel
from pyrme.ui.styles.contracts import qss_color
from pyrme.ui.styles.focus import FOCUS_TOKENS, focus_panel_qss
from pyrme.ui.theme import THEME


def test_focus_tokens_use_noct_theme_colors() -> None:
    assert FOCUS_TOKENS.inactive_border == qss_color(THEME.ghost_border)
    assert FOCUS_TOKENS.active_border == qss_color(THEME.focus_border)
    assert FOCUS_TOKENS.active_background == qss_color(THEME.lifted_glass)


def test_focus_panel_qss_contains_active_and_inactive_rules() -> None:
    qss = focus_panel_qss("QWidget")

    assert 'QWidget[activeEditorView="false"]' in qss
    assert 'QWidget[activeEditorView="true"]' in qss
    assert f"border: 1px solid {FOCUS_TOKENS.inactive_border};" in qss
    assert f"border: 1px solid {FOCUS_TOKENS.active_border};" in qss
    assert f"background-color: {FOCUS_TOKENS.active_background};" in qss


def test_hyprland_tokens_use_arch_blue_accents() -> None:
    assert THEME.void_black == QColor("#1e2227")
    assert THEME.amethyst_core == QColor("#1793d1")
    assert THEME.deep_amethyst == QColor("#116b99")
    assert qss_color(THEME.focus_border) == "rgba(23, 147, 209, 204)"


def test_glass_panel_shadow_and_focus_contract(qtbot) -> None:
    panel = GlassPanel()
    qtbot.addWidget(panel)

    effect = panel.graphicsEffect()
    assert isinstance(effect, QGraphicsDropShadowEffect)
    assert effect.blurRadius() == 20
    assert effect.yOffset() == 4
    assert panel.focusPolicy() == Qt.FocusPolicy.ClickFocus
    assert panel._is_active is False

    panel.focusInEvent(QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.MouseFocusReason))
    assert panel._is_active is True

    panel.focusOutEvent(QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.MouseFocusReason))
    assert panel._is_active is False


def test_styles_exports_input_and_dropdown_helpers() -> None:
    from pyrme.ui.styles import dropdown_qss, input_field_qss

    assert "QLineEdit:focus" in input_field_qss("QLineEdit")
    assert "QComboBox:focus" in dropdown_qss("QComboBox")


def test_brush_palette_uses_shared_focus_qss(qtbot) -> None:
    from pyrme.ui.docks.brush_palette import BrushPaletteDock

    dock = BrushPaletteDock()
    qtbot.addWidget(dock)

    assert "QLineEdit:focus" in dock._search_bar.styleSheet()
    assert "QListView:focus" in dock._views["Terrain"].styleSheet()
    assert qss_color(THEME.focus_border) in dock._search_bar.styleSheet()


def test_minimap_and_properties_use_theme_qss_contracts(qtbot) -> None:
    from pyrme.ui.docks.minimap import MinimapDock
    from pyrme.ui.docks.properties import PropertiesDock

    minimap = MinimapDock()
    properties = PropertiesDock()
    qtbot.addWidget(minimap)
    qtbot.addWidget(properties)

    assert qss_color(THEME.ghost_border) in minimap.map_view.styleSheet()
    assert qss_color(THEME.moonstone_white) in minimap.pos_label.styleSheet()
    assert qss_color(THEME.active_border) in minimap.z_up_btn.styleSheet()

    heading = properties.content_widget().layout().itemAt(0).widget()
    assert heading.text() == "SELECTION PROPERTIES"
    assert "font-size: 11px" in heading.styleSheet()
    assert qss_color(THEME.ash_lavender) in heading.styleSheet()
