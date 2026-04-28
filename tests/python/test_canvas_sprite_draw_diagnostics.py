from __future__ import annotations

from PyQt6.QtWidgets import QWidget

import pyrme.ui.canvas_host as canvas_host
from pyrme.rendering import SpriteDrawCommand, SpriteDrawPlan
from pyrme.ui.canvas_host import PlaceholderCanvasWidget, RendererHostCanvasWidget


def _draw_plan(
    *,
    command_count: int = 2,
    unresolved_sprite_ids: tuple[int, ...] = (777, 888),
) -> SpriteDrawPlan:
    commands = tuple(
        SpriteDrawCommand(
            sprite_id=1000 + index,
            item_id=2000 + index,
            layer=index,
            source_rect=(index, index + 1, 32, 32),
            destination_rect=(index * 32, index * 32, 32, 32),
        )
        for index in range(command_count)
    )
    return SpriteDrawPlan(
        commands=commands,
        unresolved_sprite_ids=unresolved_sprite_ids,
    )


def test_placeholder_canvas_reports_default_sprite_draw_diagnostics(qtbot) -> None:
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)

    text = canvas.diagnostic_text()

    assert "Sprite Draw Commands: 0" in text
    assert "Unresolved Sprites: none" in text


def test_placeholder_canvas_accepts_sprite_draw_plan_and_reports_counts(qtbot) -> None:
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)
    setter = getattr(canvas, "set_sprite_draw_plan", None)
    assert callable(setter)

    setter(_draw_plan())

    text = canvas.diagnostic_text()
    assert "Sprite Draw Commands: 2" in text
    assert "Unresolved Sprites: 777, 888" in text
    assert canvas.sprite_draw_command_count() == 2
    assert canvas.unresolved_sprite_ids() == (777, 888)


def test_sprite_draw_plan_diagnostics_normalize_repeated_updates(qtbot) -> None:
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)
    setter = getattr(canvas, "set_sprite_draw_plan", None)
    assert callable(setter)

    setter(_draw_plan(unresolved_sprite_ids=(888, 777, 888)))

    assert canvas.unresolved_sprite_ids() == (777, 888)
    assert "Unresolved Sprites: 777, 888" in canvas.diagnostic_text()

    setter(_draw_plan(command_count=0, unresolved_sprite_ids=()))

    assert canvas.sprite_draw_command_count() == 0
    assert canvas.unresolved_sprite_ids() == ()
    assert "Sprite Draw Commands: 0" in canvas.diagnostic_text()
    assert "Unresolved Sprites: none" in canvas.diagnostic_text()


def test_sprite_draw_plan_protocol_helper_detects_canvas_hosts(qtbot) -> None:
    helper = getattr(
        canvas_host,
        "implements_editor_sprite_draw_plan_canvas_protocol",
        None,
    )
    assert callable(helper)
    placeholder = PlaceholderCanvasWidget()
    renderer = RendererHostCanvasWidget()
    plain = QWidget()
    qtbot.addWidget(placeholder)
    qtbot.addWidget(renderer)
    qtbot.addWidget(plain)

    assert helper(placeholder)
    assert helper(renderer)
    assert not helper(plain)
