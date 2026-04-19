"""Tier 2 widget tests for the Map Properties dialog."""

from __future__ import annotations

from pyrme.ui.dialogs.map_properties import MapPropertiesDialog, MapPropertiesState


def test_map_properties_dialog_renders_required_controls(qtbot) -> None:
    dialog = MapPropertiesDialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Map Properties"
    assert dialog.desc_edit is not None
    assert dialog.otbm_combo is not None
    assert dialog.client_combo is not None
    assert dialog.width_spin is not None
    assert dialog.height_spin is not None
    assert dialog.house_edit is not None
    assert dialog.spawn_edit is not None
    assert dialog.waypoint_edit is not None
    assert dialog.cancel_btn.text() == "Cancel"
    assert dialog.ok_btn.text() == "Save"


def test_map_properties_dialog_loads_state(qtbot) -> None:
    state = MapPropertiesState(
        description="A dark custom map.",
        map_version="OTServ 0.7.0 (revscriptsys)",
        client_version="7.60",
        width=1024,
        height=768,
        house_file="houses.xml",
        spawn_file="spawns.xml",
        waypoint_file="waypoints.xml",
    )

    dialog = MapPropertiesDialog(state=state)
    qtbot.addWidget(dialog)

    assert dialog.desc_edit.toPlainText() == state.description
    assert dialog.otbm_combo.currentText() == state.map_version
    assert dialog.client_combo.currentText() == state.client_version
    assert dialog.width_spin.value() == state.width
    assert dialog.height_spin.value() == state.height
    assert dialog.house_edit.text() == state.house_file
    assert dialog.spawn_edit.text() == state.spawn_file
    assert dialog.waypoint_edit.text() == state.waypoint_file


def test_map_properties_dialog_returns_edited_state_on_accept(qtbot) -> None:
    dialog = MapPropertiesDialog(
        state=MapPropertiesState(
            description="Initial description",
            map_version="OTServ 0.6.1",
            client_version="10.98",
            width=512,
            height=512,
            house_file="initial_houses.xml",
            spawn_file="initial_spawns.xml",
            waypoint_file="initial_waypoints.xml",
        )
    )
    qtbot.addWidget(dialog)

    dialog.desc_edit.setPlainText("Edited description")
    dialog.otbm_combo.setCurrentText("OTServ 0.5.0")
    dialog.client_combo.setCurrentText("8.60")
    dialog.width_spin.setValue(2048)
    dialog.height_spin.setValue(4096)
    dialog.house_edit.setText("houses_edited.xml")
    dialog.spawn_edit.setText("spawns_edited.xml")
    dialog.waypoint_edit.setText("waypoints_edited.xml")

    dialog.accept()

    assert dialog.state() == MapPropertiesState(
        description="Edited description",
        map_version="OTServ 0.5.0",
        client_version="8.60",
        width=2048,
        height=4096,
        house_file="houses_edited.xml",
        spawn_file="spawns_edited.xml",
        waypoint_file="waypoints_edited.xml",
    )
