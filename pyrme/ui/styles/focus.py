"""Focus-state QSS helpers for Noct shell widgets."""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent

from pyrme.ui.styles.contracts import qss_color
from pyrme.ui.theme import THEME


@dataclass(frozen=True, slots=True)
class FocusTokens:
    inactive_border: str
    active_border: str
    active_background: str
    radius_px: int = 4


FOCUS_TOKENS = FocusTokens(
    inactive_border=qss_color(THEME.ghost_border),
    active_border=qss_color(THEME.focus_border),
    active_background=qss_color(THEME.lifted_glass),
)


def focus_panel_qss(selector: str) -> str:
    return dedent(
        f"""
        {selector}[activeEditorView="false"] {{
            border: 1px solid {FOCUS_TOKENS.inactive_border};
            border-radius: {FOCUS_TOKENS.radius_px}px;
        }}
        {selector}[activeEditorView="true"] {{
            border: 1px solid {FOCUS_TOKENS.active_border};
            border-radius: {FOCUS_TOKENS.radius_px}px;
            background-color: {FOCUS_TOKENS.active_background};
        }}
        """
    ).strip()
