from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

from pyrme.editor.model import MapPosition, TileState
from pyrme.ui.legacy_menu_contract import LEGACY_MAP_MENU_SEQUENCE, PHASE1_ACTIONS
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

    import pytest
    from PyQt6.QtWidgets import QMenu


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


def _map_menu(window: MainWindow) -> QMenu:
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menu = next(action.menu() for action in menu_bar.actions() if action.text() == "Map")
    assert menu is not None
    return menu


def _menu_sequence(menu: QMenu) -> tuple[str | None, ...]:
    return tuple(None if action.isSeparator() else action.text() for action in menu.actions())


class _MapPropertiesDialog:
    opened = False

    def __init__(self, parent=None) -> None:
        self.parent = parent

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)


class _TownManagerDialog:
    opened = False

    def __init__(self, parent=None) -> None:
        self.parent = parent

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)


class _HouseManagerDialog:
    opened = False

    def __init__(self, parent=None) -> None:
        self.parent = parent

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)


class _MapStatisticsDialog:
    opened = False
    received_stats = None

    def __init__(self, parent=None, *, statistics=None) -> None:
        self.parent = parent
        self.statistics = statistics
        type(self).received_stats = statistics

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)


def test_legacy_map_contract_matches_xml() -> None:
    assert LEGACY_MAP_MENU_SEQUENCE == (
        "Edit Towns",
        "Edit Houses",
        None,
        "Cleanup invalid tiles...",
        "Cleanup invalid zones...",
        "Properties...",
        "Statistics",
    )
    assert "map_edit_items" not in PHASE1_ACTIONS
    assert "map_edit_monsters" not in PHASE1_ACTIONS
    assert PHASE1_ACTIONS["map_edit_towns"].shortcut == "Ctrl+T"
    assert PHASE1_ACTIONS["map_edit_towns"].status_tip == "Edit towns."
    assert PHASE1_ACTIONS["map_cleanup_invalid_tiles"].status_tip == (
        "Removes all invalid or unresolved items from the map."
    )
    assert PHASE1_ACTIONS["map_cleanup_invalid_zones"].status_tip == (
        "Removes preserved invalid tile flags and opaque OTBM tile fragments from the map."
    )
    assert PHASE1_ACTIONS["map_properties"].shortcut == "Ctrl+P"
    assert PHASE1_ACTIONS["map_statistics"].shortcut == "F8"


def test_main_window_map_menu_matches_legacy_order(qtbot, settings_workspace: Path) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-menu.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert _menu_sequence(_map_menu(window)) == LEGACY_MAP_MENU_SEQUENCE
    assert window.map_edit_towns_action.objectName() == "action_map_edit_towns"
    assert window.map_cleanup_invalid_tiles_action.objectName() == (
        "action_map_cleanup_invalid_tiles"
    )
    assert window.map_cleanup_invalid_zones_action.objectName() == (
        "action_map_cleanup_invalid_zones"
    )
    assert window.map_properties_action.objectName() == "action_map_properties"
    assert window.map_statistics_action.objectName() == "action_map_statistics"


def test_map_cleanup_gap_actions_report_exact_missing_core_data(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-stubs.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    for action, expected in (
        (
            window.map_cleanup_invalid_tiles_action,
            "Cleanup invalid tiles deferred: TileState has no invalid item or "
            "unresolved item flags.",
        ),
        (
            window.map_cleanup_invalid_zones_action,
            "Cleanup invalid zones deferred: TileState has no invalid zone or "
            "opaque OTBM fragment fields.",
        ),
    ):
        action.trigger()
        assert window.statusBar().currentMessage() == expected


def test_map_statistics_action_uses_current_editor_map_data(
    qtbot,
    settings_workspace: Path,
) -> None:
    _MapStatisticsDialog.opened = False
    _MapStatisticsDialog.received_stats = None
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-statistics-action.ini"),
        enable_docks=False,
        map_statistics_dialog_factory=_MapStatisticsDialog,
    )
    qtbot.addWidget(window)

    editor = window._editor_context.session.editor
    editor.map_model.set_tile(
        TileState(
            position=MapPosition(32000, 32000, 7),
            ground_item_id=100,
            item_ids=(200, 300),
        )
    )
    editor.map_model.set_tile(
        TileState(position=MapPosition(32001, 32000, 7), ground_item_id=400)
    )

    window.map_statistics_action.trigger()

    assert _MapStatisticsDialog.opened is True
    assert _MapStatisticsDialog.received_stats is not None
    assert _MapStatisticsDialog.received_stats.tile_count == 2
    assert _MapStatisticsDialog.received_stats.item_count == 4
    assert _MapStatisticsDialog.received_stats.walkable_tile_count == 2
    assert _MapStatisticsDialog.received_stats.blocking_tile_count == 0


def test_map_edit_towns_action_uses_town_manager_dialog(
    qtbot,
    settings_workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _TownManagerDialog.opened = False
    monkeypatch.setattr("pyrme.ui.main_window.TownManagerDialog", _TownManagerDialog)
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-town-manager-action.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.map_edit_towns_action.trigger()

    assert _TownManagerDialog.opened is True


def test_map_properties_action_uses_dialog_seam(qtbot, settings_workspace: Path) -> None:
    _MapPropertiesDialog.opened = False
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-properties-action.ini"),
        enable_docks=False,
        map_properties_dialog_factory=_MapPropertiesDialog,
    )
    qtbot.addWidget(window)

    window.map_properties_action.trigger()

    assert _MapPropertiesDialog.opened is True


def test_map_edit_houses_action_uses_house_manager_dialog(
    qtbot,
    settings_workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _HouseManagerDialog.opened = False
    monkeypatch.setattr("pyrme.ui.main_window.HouseManagerDialog", _HouseManagerDialog)
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-house-manager-action.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.map_edit_houses_action.trigger()

    assert _HouseManagerDialog.opened is True
