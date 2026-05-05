from __future__ import annotations

from PyQt6.QtCore import QSettings, Qt

from pyrme.ui.docks.brush_palette import BrushPaletteDock
from pyrme.ui.main_window import MainWindow
from pyrme.ui.models.brush_catalog import (
    BrushPaletteEntry,
    default_brush_palette_entries,
    entries_by_palette,
)


def _build_settings(root, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def test_default_brush_catalog_has_real_ground_and_wall_entries() -> None:
    entries = default_brush_palette_entries()

    assert any(entry.name == "grass" and entry.kind == "ground" for entry in entries)
    assert any(entry.name == "stone wall" and entry.kind == "wall" for entry in entries)
    assert all(not entry.name.startswith("Terrain Brush") for entry in entries)


def test_brush_palette_entry_active_id_and_search_text() -> None:
    entry = BrushPaletteEntry(
        brush_id=10,
        name="grass",
        kind="ground",
        palette_name="Terrain",
        look_id=4526,
        related_item_ids=(4526, 4527),
    )

    assert entry.active_brush_id == "brush:ground:10"
    assert entry.search_text == "grass ground terrain 10 4526 4527"


def test_entries_by_palette_filters_visible_entries() -> None:
    grouped = entries_by_palette(
        (
            BrushPaletteEntry(1, "grass", "ground", "Terrain", 4526, (4526,)),
            BrushPaletteEntry(2, "hidden", "ground", "Terrain", 1, (1,), False),
            BrushPaletteEntry(3, "stone wall", "wall", "Terrain", 3361, (3361,)),
        )
    )

    assert [entry.name for entry in grouped["Terrain"]] == ["grass", "stone wall"]


def _display_values(dock: BrushPaletteDock, palette: str) -> list[str]:
    proxy = dock._proxies[palette]
    return [
        proxy.data(proxy.index(row, 0), int(Qt.ItemDataRole.DisplayRole))
        for row in range(proxy.rowCount())
    ]


def test_brush_palette_uses_catalog_entries(qtbot) -> None:
    dock = BrushPaletteDock()
    qtbot.addWidget(dock)

    values = _display_values(dock, "Terrain")

    assert "grass" in values
    assert "stone wall" in values
    assert all(not value.startswith("Terrain Brush") for value in values)


def test_brush_palette_search_filters_catalog_entries(qtbot) -> None:
    dock = BrushPaletteDock()
    qtbot.addWidget(dock)
    dock.select_palette("Terrain")

    dock._search_bar.setText("wall")

    assert _display_values(dock, "Terrain") == ["stone wall", "wooden wall"]


def test_brush_palette_emits_selected_catalog_brush(qtbot) -> None:
    dock = BrushPaletteDock()
    qtbot.addWidget(dock)
    selected = []
    dock.brush_selected.connect(selected.append)

    dock.select_palette("Terrain")
    view = dock._views["Terrain"]
    view.clicked.emit(view.model().index(0, 0))

    assert selected
    assert selected[0].active_brush_id == "brush:ground:10"


def test_main_window_catalog_brush_selection_updates_shell_state(
    qtbot,
    settings_workspace,
) -> None:
    window = MainWindow(settings=_build_settings(settings_workspace, "brush-ui.ini"))
    qtbot.addWidget(window)

    assert window.brush_palette_dock is not None
    window.brush_palette_dock.select_palette("Terrain")
    view = window.brush_palette_dock._views["Terrain"]
    view.clicked.emit(view.model().index(0, 0))

    assert window._active_brush_name == "grass"
    assert window._active_brush_id == "brush:ground:10"
    assert window._active_item_id is None
    assert window._editor_context.session.active_brush_id == "brush:ground:10"
    assert window._editor_context.session.active_item_id is None
    assert "brush: grass" in window.statusBar().currentMessage().lower()
