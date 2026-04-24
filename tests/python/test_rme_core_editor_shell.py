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
