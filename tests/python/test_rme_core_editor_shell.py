from __future__ import annotations

import pytest


def test_native_rme_core_exposes_editor_shell_state() -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )

    if not hasattr(rme_core, "EditorShellState"):
        pytest.skip(
            "pyrme.rme_core binary was not rebuilt with EditorShellState in this environment"
        )

    assert hasattr(rme_core, "EditorShellState")

    shell = rme_core.EditorShellState()
    assert shell.position() == (32000, 32000, 7)
    assert shell.set_position(99_999, -10, 99) == (65000, 0, 15)
    assert shell.set_floor(4) == 4
    assert shell.set_zoom_percent(5) == 10
    assert shell.set_show_grid(True) is True
    assert shell.set_view_flag("show_all_floors", True) is True
    assert shell.view_flag("show_all_floors") is True
    assert shell.set_show_flag("show_spawns", True) is True
    assert shell.show_flag("show_spawns") is True
    assert "worker_threads=" in shell.render_summary()

def test_native_rme_core_save_otbm(tmp_path) -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )
    if not hasattr(rme_core.EditorShellState, "save_otbm"):
        pytest.skip("pyrme.rme_core binary was not rebuilt with save_otbm")

    shell = rme_core.EditorShellState()

    # Place a tile and save it
    shell.set_tile_ground(100, 100, 7, 4526)
    assert shell.tile_count() == 1

    out_file = tmp_path / "test_save.otbm"
    shell.save_otbm(str(out_file))

    assert out_file.exists()
    assert out_file.stat().st_size > 0
    assert not shell.map_is_dirty()


def test_native_rme_core_save_otbm_writes_xml_sidecars(tmp_path) -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )
    if not hasattr(rme_core.EditorShellState, "save_otbm"):
        pytest.skip("pyrme.rme_core binary was not rebuilt with save_otbm")

    shell = rme_core.EditorShellState()
    shell.add_waypoint("Temple & Shop", 100, 200, 7)
    spawn_index = shell.add_spawn(101, 201, 7, 5)
    shell.add_spawn_creature(spawn_index, "Rat \"Scout\"", 1, -1, 60, False, 2)
    shell.add_spawn_creature(spawn_index, "Guide", 0, 0, 30, True, 0)
    shell.add_house(12, "Depot \"North\"", 102, 202, 7, 500, 3, True, 14)

    out_file = tmp_path / "xml_map.otbm"
    shell.save_otbm(str(out_file))

    assert (tmp_path / "xml_map-waypoint.xml").read_text(encoding="utf-8") == (
        '<?xml version="1.0"?>\n'
        "<waypoints>\n"
        '\t<waypoint name="Temple &amp; Shop" x="100" y="200" z="7" />\n'
        "</waypoints>\n"
    )
    assert (tmp_path / "xml_map-spawn.xml").read_text(encoding="utf-8") == (
        '<?xml version="1.0"?>\n'
        "<spawns>\n"
        '\t<spawn centerx="101" centery="201" centerz="7" radius="5">\n'
        '\t\t<monster name="Rat &quot;Scout&quot;" x="1" y="-1" spawntime="60" '
        'direction="2" />\n'
        '\t\t<npc name="Guide" x="0" y="0" spawntime="30" />\n'
        "\t</spawn>\n"
        "</spawns>\n"
    )
    assert (tmp_path / "xml_map-house.xml").read_text(encoding="utf-8") == (
        '<?xml version="1.0"?>\n'
        "<houses>\n"
        '\t<house name="Depot &quot;North&quot;" houseid="12" entryx="102" entryy="202" '
        'entryz="7" rent="500" guildhall="true" townid="3" size="14" />\n'
        "</houses>\n"
    )


def test_native_rme_core_load_otbm_reads_xml_sidecars(tmp_path) -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )
    if not hasattr(rme_core.EditorShellState, "load_otbm"):
        pytest.skip("pyrme.rme_core binary was not rebuilt with load_otbm")
    if not hasattr(rme_core.EditorShellState, "sidecar_counts"):
        pytest.skip("pyrme.rme_core binary was not rebuilt with sidecar_counts")

    writer = rme_core.EditorShellState()
    writer.add_waypoint("Temple", 100, 200, 7)
    spawn_index = writer.add_spawn(101, 201, 7, 5)
    writer.add_spawn_creature(spawn_index, "Rat", 1, -1, 60, False, 2)
    writer.add_house(12, "Depot", 102, 202, 7, 500, 3, True, 14)

    out_file = tmp_path / "roundtrip.otbm"
    writer.save_otbm(str(out_file))

    reader = rme_core.EditorShellState()
    assert reader.load_otbm(str(out_file)) == (0, 0, 0)
    assert tuple(reader.sidecar_counts()) == (1, 1, 1, 1)
    assert reader.map_is_dirty() is False
