"""Tier 2 widget tests for the Find Brush dialog."""

from __future__ import annotations

from pyrme.ui.dialogs.find_brush import FindBrushDialog, FindBrushResult


def test_find_brush_dialog_filters_palette_and_item_results(qtbot) -> None:
    dialog = FindBrushDialog(
        catalog=[
            FindBrushResult(name="RAW", kind="palette", palette_name="RAW"),
            FindBrushResult(name="Stone", kind="item", palette_name="Item", item_id=1),
            FindBrushResult(name="Gold Coin", kind="item", palette_name="Item", item_id=2148),
        ]
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Jump to Brush"
    assert dialog.result_list.count() == 0

    dialog.search_field.setText("st")

    assert dialog.result_list.count() == 1
    assert dialog.result_list.currentItem() is not None
    assert dialog.result_list.currentItem().text() == "Stone (#1)"


def test_find_brush_dialog_returns_selected_result_on_accept(qtbot) -> None:
    dialog = FindBrushDialog(
        catalog=[
            FindBrushResult(name="RAW", kind="palette", palette_name="RAW"),
            FindBrushResult(name="Stone", kind="item", palette_name="Item", item_id=1),
        ]
    )
    qtbot.addWidget(dialog)

    dialog.search_field.setText("ra")
    dialog.accept()

    assert dialog.selected_result() == FindBrushResult(
        name="RAW",
        kind="palette",
        palette_name="RAW",
    )


def test_find_brush_default_catalog_includes_catalog_brushes(qapp) -> None:  # noqa: ARG001
    dialog = FindBrushDialog()
    dialog.search_field.setText("grass")

    result = dialog.selected_result()

    assert result is not None
    assert result.name == "grass"
    assert result.kind == "brush"
    assert result.palette_name == "Terrain"
    assert result.brush_id == 10
