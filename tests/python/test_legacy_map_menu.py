from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog

from pyrme.ui.legacy_menu_contract import LEGACY_MAP_MENU_SEQUENCE, PHASE1_ACTIONS
from pyrme.ui.main_window import MainWindow

if TYPE_CHECKING:
    from pathlib import Path

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


class _MapStatisticsDialog:
    opened = False
    parent = None
    shell_state = None

    def __init__(self, parent=None, shell_state=None) -> None:
        type(self).parent = parent
        type(self).shell_state = shell_state

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)


class _TownManagerDialog:
    opened = False
    parent = None
    bridge = None

    def __init__(self, bridge=None, parent=None) -> None:
        type(self).opened = False  # Reset
        type(self).bridge = bridge
        type(self).parent = parent

    def exec(self) -> int:
        type(self).opened = True
        return int(QDialog.DialogCode.Accepted)


def test_legacy_map_contract_matches_xml() -> None:
    assert LEGACY_MAP_MENU_SEQUENCE == (
        "Edit Towns",
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


def test_map_backend_gap_actions_are_safe_until_backend_exists(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-stubs.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    for action, expected in (
        (window.map_cleanup_invalid_tiles_action, "cleanup invalid tiles"),
        (window.map_cleanup_invalid_zones_action, "cleanup invalid zones"),
    ):
        action.trigger()
        message = window.statusBar().currentMessage().lower()
        assert expected in message
        assert "not available" in message


def test_map_edit_towns_action_uses_town_manager_dialog(
    qtbot,
    settings_workspace: Path,
) -> None:
    _TownManagerDialog.opened = False
    _TownManagerDialog.parent = None
    _TownManagerDialog.bridge = None
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-town-manager-action.ini"),
        enable_docks=False,
        town_manager_dialog_factory=_TownManagerDialog,
    )
    qtbot.addWidget(window)

    window.map_edit_towns_action.trigger()

    assert _TownManagerDialog.opened is True
    assert _TownManagerDialog.parent is window
    assert _TownManagerDialog.bridge is not None


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


def test_map_statistics_action_uses_dialog_seam(qtbot, settings_workspace: Path) -> None:
    _MapStatisticsDialog.opened = False
    _MapStatisticsDialog.parent = None
    _MapStatisticsDialog.shell_state = None
    window = MainWindow(
        settings=_build_settings(settings_workspace, "map-statistics-action.ini"),
        enable_docks=False,
        map_statistics_dialog_factory=_MapStatisticsDialog,
    )
    qtbot.addWidget(window)

    window.map_statistics_action.trigger()

    assert _MapStatisticsDialog.opened is True
    assert _MapStatisticsDialog.parent is window
    assert _MapStatisticsDialog.shell_state is not None
