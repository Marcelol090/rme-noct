from __future__ import annotations

from dataclasses import dataclass

from pyrme.ui.dialogs.map_statistics import MapStatisticsDialog


@dataclass(slots=True)
class _Stats:
    tile_count: int = 10
    blocking_tile_count: int = 3
    walkable_tile_count: int = 7
    item_count: int = 15
    spawn_count: int = 2
    creature_count: int = 4
    house_count: int = 2
    total_house_sqm: int = 20
    town_count: int = 1
    waypoint_count: int = 5


class _ShellState:
    def collect_statistics(self) -> _Stats:
        return _Stats()


def test_map_statistics_dialog_reads_core_stat_fields(qtbot) -> None:
    dialog = MapStatisticsDialog(shell_state=_ShellState())
    qtbot.addWidget(dialog)

    assert dialog.tile_count.text() == "10"
    assert dialog.item_count.text() == "15"
    assert dialog.blocking_tiles.text() == "3"
    assert dialog.walkable_tiles.text() == "7"
    assert dialog.spawn_count.text() == "2"
    assert dialog.creature_count.text() == "4"
    assert dialog.waypoint_count.text() == "5"
    assert dialog.house_count.text() == "2"
    assert dialog.house_sqm.text() == "20"
    assert dialog.town_count.text() == "1"
    assert dialog.pathable_perc.text() == "70.0%"
    assert dialog.sqm_per_house.text() == "10.0"
