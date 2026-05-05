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
