"""Tier 2 visual style contract tests."""

from __future__ import annotations

from pathlib import Path

from pyrme.ui.dialogs.find_item import FindItemDialog
from pyrme.ui.dialogs.goto_position import GotoPositionDialog
from pyrme.ui.dialogs.map_properties import MapPropertiesDialog
from pyrme.ui.docks.waypoints import WaypointsDock
from pyrme.ui.styles.contracts import (
    destructive_button_qss,
    dialog_base_qss,
    ghost_button_qss,
    item_view_qss,
    primary_button_qss,
    qss_color,
    section_heading_qss,
    subtle_action_qss,
)
from pyrme.ui.theme import THEME


def test_qss_color_preserves_alpha_for_translucent_theme_tokens() -> None:
    assert qss_color(THEME.obsidian_glass) == "rgba(255, 255, 255, 10)"
    assert qss_color(THEME.lifted_glass) == "rgba(255, 255, 255, 17)"
    assert qss_color(THEME.ghost_border) == "rgba(255, 255, 255, 20)"
    assert qss_color(THEME.active_border) == "rgba(255, 255, 255, 35)"
    assert qss_color(THEME.amethyst_core) == "#7c5cfc"


def test_tier2_widgets_share_visual_contract_helpers(qtbot) -> None:
    map_dialog = MapPropertiesDialog()
    find_dialog = FindItemDialog()
    goto_dialog = GotoPositionDialog()
    waypoints_dock = WaypointsDock()

    for widget in (map_dialog, find_dialog, goto_dialog, waypoints_dock):
        qtbot.addWidget(widget)

    assert map_dialog.cancel_btn.styleSheet() == ghost_button_qss()
    assert map_dialog.ok_btn.styleSheet() == primary_button_qss()
    assert find_dialog.btn_search_map.styleSheet() == ghost_button_qss()
    assert find_dialog.btn_cancel.styleSheet() == ghost_button_qss()
    assert find_dialog.btn_ok.styleSheet() == primary_button_qss()
    assert goto_dialog._clear_btn.styleSheet() == subtle_action_qss()
    assert waypoints_dock.btn_add.styleSheet() == ghost_button_qss()
    assert waypoints_dock.btn_rename.styleSheet() == ghost_button_qss()
    assert waypoints_dock.btn_remove.styleSheet() == destructive_button_qss()
    assert waypoints_dock.tree_widget.styleSheet() == item_view_qss(
        "QTreeWidget",
        include_header=True,
    )

    assert map_dialog.styleSheet() == dialog_base_qss(
        "QLineEdit, QSpinBox, QComboBox, QTextEdit"
    )
    assert goto_dialog.styleSheet() == dialog_base_qss()
    assert goto_dialog.recent_header.styleSheet() == section_heading_qss()


def test_dark_theme_qss_keeps_toolbar_and_dock_token_contract() -> None:
    qss = Path("pyrme/ui/styles/dark_theme.qss").read_text(encoding="utf-8")

    assert "QToolBar QToolButton:checked" in qss
    assert "background-color: rgba(124, 92, 252, 38);" in qss
    assert "border-color: #7C5CFC;" in qss
    assert "QDockWidget::title" in qss
    assert "border-top: 1px solid rgba(255, 255, 255, 36);" in qss
    assert "border-bottom: 1px solid rgba(255, 255, 255, 20);" in qss
