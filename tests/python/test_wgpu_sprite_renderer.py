from __future__ import annotations

import pytest

from pyrme.rme_core import render


def _solid(r: int, g: int, b: int, a: int = 255) -> bytes:
    return bytes((r, g, b, a)) * (32 * 32)


def test_render_headless_returns_tightly_packed_clear_buffer() -> None:
    atlas = render.SpriteAtlas()

    try:
        result = atlas.render_headless(4, 3)
    except RuntimeError as error:
        if "WGPU renderer unavailable: no compatible adapter" in str(error):
            pytest.skip(str(error))
        raise

    assert result["width"] == 4
    assert result["height"] == 3
    assert len(result["rgba"]) == 4 * 3 * 4
    assert result["rendered_sprite_count"] == 0
    assert result["missing_sprite_count"] == 0
    assert {
        result["rgba"][index : index + 4] for index in range(0, len(result["rgba"]), 4)
    } == {
        bytes((10, 10, 18, 255))
    }


def test_render_headless_draws_last_staged_frame_sprite() -> None:
    atlas = render.SpriteAtlas()
    atlas.render_frame(
        [
            {
                "x": 0,
                "y": 0,
                "layer": 0,
                "sprite_id": 55,
                "pixels": _solid(255, 0, 0),
            }
        ]
    )

    try:
        result = atlas.render_headless(32, 32)
    except RuntimeError as error:
        if "WGPU renderer unavailable: no compatible adapter" in str(error):
            pytest.skip(str(error))
        raise

    assert result["rendered_sprite_count"] == 1
    assert result["missing_sprite_count"] == 0
    assert result["rgba"] == _solid(255, 0, 0)
