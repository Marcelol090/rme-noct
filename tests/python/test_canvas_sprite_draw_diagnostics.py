from __future__ import annotations

from PyQt6.QtWidgets import QWidget

import pyrme.ui.canvas_host as canvas_host
from pyrme.editor import MapPosition, TileState
from pyrme.rendering import SpriteDrawCommand, SpriteDrawPlan
from pyrme.rendering.sprite_catalog_adapter import (
    DatSpriteRecord,
    SprFrameRecord,
    build_sprite_catalog_from_asset_records,
)
from pyrme.rendering.sprite_draw_commands import SpriteAtlas, SpriteAtlasRegion
from pyrme.rendering.sprite_frame import SpriteCatalog, SpriteCatalogEntry
from pyrme.ui.canvas_host import PlaceholderCanvasWidget, RendererHostCanvasWidget
from pyrme.ui.editor_context import EditorContext
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot


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


def _live_context() -> EditorContext:
    context = EditorContext()
    context.session.editor.map_model.set_tile(
        TileState(position=MapPosition(32000, 32000, 7), ground_item_id=2148)
    )
    return context


def _viewport_snapshot() -> ViewportSnapshot:
    viewport = EditorViewport(
        ViewportSnapshot(center_x=32000, center_y=32000, floor=7)
    )
    viewport.set_view_size(128, 128)
    return viewport.snapshot()


def _fixture_catalog_and_atlas():
    catalog = build_sprite_catalog_from_asset_records(
        dat_records=(DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground"),),
        spr_frames=(
            SprFrameRecord(
                sprite_id=9001,
                frame_index=0,
                width=32,
                height=32,
            ),
        ),
    )
    atlas = SpriteAtlas(
        (SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32)),)
    )
    return catalog, atlas


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


def test_placeholder_canvas_builds_sprite_draw_plan_from_live_frame(qtbot) -> None:
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)
    canvas.set_viewport_snapshot(_viewport_snapshot())
    canvas.bind_editor_context(_live_context())
    catalog, atlas = _fixture_catalog_and_atlas()
    setter = getattr(canvas, "set_sprite_draw_inputs", None)
    assert callable(setter)

    setter(catalog, atlas)

    assert canvas.sprite_draw_command_count() == 1
    assert canvas.unresolved_sprite_ids() == ()
    text = canvas.diagnostic_text()
    assert "Visible Tiles: 1" in text
    assert "Sprite Draw Commands: 1" in text
    assert "Unresolved Sprites: none" in text


def test_live_sprite_draw_plan_updates_when_frame_changes(qtbot) -> None:
    context = _live_context()
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)
    canvas.set_viewport_snapshot(_viewport_snapshot())
    canvas.bind_editor_context(context)
    canvas.set_sprite_draw_inputs(*_fixture_catalog_and_atlas())
    assert canvas.sprite_draw_command_count() == 1

    context.session.editor.map_model.remove_tile(MapPosition(32000, 32000, 7))
    canvas.set_position(32000, 32000, 7)

    assert "Visible Tiles: 0" in canvas.diagnostic_text()
    assert canvas.sprite_draw_command_count() == 0


def test_explicit_sprite_draw_plan_overrides_live_fixture_inputs(qtbot) -> None:
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)
    canvas.set_viewport_snapshot(_viewport_snapshot())
    canvas.bind_editor_context(_live_context())
    canvas.set_sprite_draw_inputs(*_fixture_catalog_and_atlas())
    assert canvas.sprite_draw_command_count() == 1

    canvas.set_sprite_draw_plan(_draw_plan(command_count=2))
    canvas.set_position(32000, 32000, 7)

    assert canvas.sprite_draw_command_count() == 2


def test_failed_live_sprite_draw_generation_clears_stale_commands(qtbot) -> None:
    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)
    canvas.set_viewport_snapshot(_viewport_snapshot())
    canvas.bind_editor_context(_live_context())
    canvas.set_sprite_draw_inputs(*_fixture_catalog_and_atlas())
    assert canvas.sprite_draw_command_count() == 1
    broken_catalog = SpriteCatalog(
        (
            SpriteCatalogEntry(
                item_id=2148,
                sprite_id=9001,
                metadata={"sprite_frames": (object(),)},
            ),
        )
    )

    canvas.set_sprite_draw_inputs(
        broken_catalog,
        SpriteAtlas((SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32)),)),
    )

    assert canvas.sprite_draw_command_count() == 0
    text = canvas.diagnostic_text()
    assert "Visible Tiles: 1" in text
    assert "Sprite Draw Commands: 0" in text
    assert "sprite draw plan unavailable:" in text
