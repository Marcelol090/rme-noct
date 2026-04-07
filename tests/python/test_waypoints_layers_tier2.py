"""Tier 2 widget tests for the Waypoints dock and Layers toolbar."""

from __future__ import annotations

from PyQt6.QtWidgets import QToolBar

from pyrme.ui.docks.waypoints import WaypointEntry, WaypointsDock
from pyrme.ui.main_window import MainWindow


def test_waypoints_dock_supports_local_model_roundtrip(qtbot) -> None:
    dock = WaypointsDock()
    qtbot.addWidget(dock)

    assert dock.tree_widget.columnCount() == 3
    header_item = dock.tree_widget.headerItem()
    assert header_item is not None
    assert header_item.text(0) == "Name"
    assert header_item.text(1) == "Coordinates"
    assert header_item.text(2) == "Linked Spawn"

    temple = WaypointEntry("Temple", 32000, 32000, 7, "temple_spawn")
    depot = WaypointEntry("Depot", 32050, 32100, 7, None)

    dock.add_waypoint(temple)
    dock.add_waypoint(depot)

    assert dock.waypoints() == [temple, depot]

    item = dock.tree_widget.topLevelItem(0)
    assert item is not None
    assert item.text(0) == "Temple"
    assert item.text(1) == "32000, 32000, 07"
    assert item.text(2) == "temple_spawn"
    assert item.font(1).family() == "JetBrains Mono"

    dock.rename_waypoint(0, "Temple Updated")
    assert dock.waypoints()[0].name == "Temple Updated"
    renamed_item = dock.tree_widget.topLevelItem(0)
    assert renamed_item is not None
    assert renamed_item.text(0) == "Temple Updated"

    selected = dock.select_waypoint(1)
    assert selected == depot
    assert dock.selected_waypoint() == depot
    current_item = dock.tree_widget.currentItem()
    assert current_item is not None
    assert current_item.text(0) == "Depot"

    removed = dock.remove_waypoint(1)
    assert removed == depot
    assert dock.waypoints() == [WaypointEntry("Temple Updated", 32000, 32000, 7, "temple_spawn")]


def test_layers_toolbar_exposes_stable_actions_and_defaults(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    floor_toolbar = None
    for toolbar in window.findChildren(QToolBar):
        if toolbar.objectName() == "floor_toolbar":
            floor_toolbar = toolbar
            break

    assert floor_toolbar is not None

    action_texts = [action.text() for action in floor_toolbar.actions()]
    assert "Floor Up" in action_texts
    assert "Floor Down" in action_texts
    assert "Ghost Higher Floors" in action_texts
    assert "Show Lower Floors" in action_texts

    floor_labels = {f"F{i}" for i in range(16)}
    floor_actions = [action for action in floor_toolbar.actions() if action.text() in floor_labels]
    assert len(floor_actions) == 16
    assert all(action.isCheckable() for action in floor_actions)
    assert floor_actions[7].isChecked()

    ghost_action = next(
        action for action in floor_toolbar.actions() if action.text() == "Ghost Higher Floors"
    )
    show_lower_action = next(
        action for action in floor_toolbar.actions() if action.text() == "Show Lower Floors"
    )

    assert ghost_action.isCheckable()
    assert not ghost_action.isChecked()
    assert show_lower_action.isCheckable()
    assert show_lower_action.isChecked()
