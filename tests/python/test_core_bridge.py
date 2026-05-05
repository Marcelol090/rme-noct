from __future__ import annotations

from pyrme.core_bridge import (
    SHOW_FLAG_DEFAULTS,
    VIEW_FLAG_DEFAULTS,
    EditorShellCoreBridge,
    _FallbackEditorShellState,
    create_editor_shell_state,
)


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


def test_editor_shell_core_bridge_resolves_autoborder_items() -> None:
    core = EditorShellCoreBridge(_FallbackEditorShellState(), native=False)

    assert core.resolve_autoborder_items(
        center_brush_id=10,
        neighbor_brush_ids=(None, 99, None, None, None, None, None, None),
        rule_id=10,
        border_item_id=4527,
    ) == (4527,)
    assert core.resolve_autoborder_items(
        center_brush_id=10,
        neighbor_brush_ids=(None, None, None, None, None, None, None, None),
        rule_id=10,
        border_item_id=4527,
    ) == ()


def test_fallback_bridge_stores_waypoints() -> None:
    core = EditorShellCoreBridge(_FallbackEditorShellState(), native=False)

    assert core.add_waypoint("Temple", 100, 200, 7) is True
    assert core.get_waypoints() == [("Temple", 100, 200, 7)]
    assert core.update_waypoint(0, "Depot", 101, 201, 8) is True
    assert core.get_waypoints() == [("Depot", 101, 201, 8)]
    assert core.remove_waypoint(0) is True
    assert core.get_waypoints() == []


def test_fallback_bridge_stores_houses() -> None:
    core = EditorShellCoreBridge(_FallbackEditorShellState(), native=False)

    assert core.add_house(12, "Depot", 0) is True
    assert core.get_houses() == [(12, "Depot", 0, 0, False, 32000, 32000, 7)]
    assert core.update_house(12, "Depot North", 3, 500, True, 100, 200, 7) is True
    assert core.get_houses() == [(12, "Depot North", 3, 500, True, 100, 200, 7)]
    assert core.remove_house(12) is True
    assert core.get_houses() == []
