from __future__ import annotations

from pyrme.core_bridge import SHOW_FLAG_DEFAULTS, VIEW_FLAG_DEFAULTS, create_editor_shell_state


def test_editor_shell_core_bridge_exposes_clamped_shell_state() -> None:
    core = create_editor_shell_state()

    assert core.position() == (32000, 32000, 7)
    assert core.set_position(99_999, -10, 99) == (65000, 0, 15)
    assert core.set_floor(6) == 6
    assert core.position() == (65000, 0, 6)
    assert core.set_zoom_percent(1) == 10
    assert core.set_show_grid(True) is True
    assert core.set_ghost_higher(True) is True
    assert core.set_show_lower(False) is False

    assert core.set_view_flag("show_all_floors", True) is True
    assert core.view_flag("show_all_floors") is True
    assert core.set_show_flag("show_spawns", True) is True
    assert core.show_flag("show_spawns") is True

    assert set(core.view_flags()) == set(VIEW_FLAG_DEFAULTS)
    assert set(core.show_flags()) == set(SHOW_FLAG_DEFAULTS)
    assert "worker_threads=" in core.render_summary()
