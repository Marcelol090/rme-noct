"""Tier 2 regression tests for the Properties dock."""

from __future__ import annotations

from PyQt6.QtWidgets import QFormLayout, QVBoxLayout

from pyrme.ui.docks.properties import PropertiesDock


def test_properties_dock_instantiates_all_value_widgets(qtbot) -> None:
    dock = PropertiesDock()
    qtbot.addWidget(dock)

    container = dock.content_widget()
    outer_layout = container.layout()
    assert isinstance(outer_layout, QVBoxLayout)

    form_item = outer_layout.itemAt(1)
    assert form_item is not None
    form_layout = form_item.layout()
    assert isinstance(form_layout, QFormLayout)
    assert form_layout.rowCount() == 6

    expected_values = [
        "X:32000 Y:32000 Z:07",
        "2555 (grass)",
        "0",
        "0",
        '""',
        "None",
    ]
    for row, expected in enumerate(expected_values):
        field_item = form_layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
        assert field_item is not None
        field_widget = field_item.widget()
        assert field_widget is not None
        assert field_widget.text() == expected
