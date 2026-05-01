"""Tests for the Tile Properties dialog."""

from pyrme.core_bridge import create_editor_shell_state
from pyrme.ui.dialogs.tile_properties import TilePropertiesDialog


def test_tile_properties_dialog_initialization(qapp):
    """Test that the tile properties dialog initializes correctly."""
    bridge = create_editor_shell_state()
    bridge.add_town(1, "Thistlewood", 1000, 1000, 7)

    dialog = TilePropertiesDialog(bridge, 1000, 1000, 7)
    assert dialog.windowTitle() == "Tile Properties (X: 1000, Y: 1000, Z: 7)"
    assert dialog.item_list.count() > 0

    # Select first item
    dialog.item_list.setCurrentRow(0)
    assert "PROPERTIES" in dialog.details_label.text()

    # Select depot
    dialog.item_list.setCurrentRow(2)
    assert dialog.details_label.text() == "DEPOT BOX PROPERTIES"
    assert dialog.depot_panel.town_combo.count() == 1

    # Select door
    dialog.item_list.setCurrentRow(3)
    assert dialog.details_label.text() == "LOCKED DOOR PROPERTIES"
    assert dialog.door_panel.door_spin.value() == 15

    # Select teleport
    dialog.item_list.setCurrentRow(4)
    assert dialog.details_label.text() == "TELEPORT PROPERTIES"
    assert dialog.teleport_panel.x_spin.value() == 1024

    # Select writable
    dialog.item_list.setCurrentRow(5)
    assert dialog.details_label.text() == "PARCHMENT PROPERTIES"
    assert dialog.writable_panel.text_edit.toPlainText() == "A mysterious scroll."

    dialog.close()
