from __future__ import annotations

import pytest
from pyrme.rme_core import render

SPRITE_BYTE_LEN = 32 * 32 * 4


def test_native_render_submodule_exposes_sprite_atlas() -> None:
    assert hasattr(render, "SpriteAtlas")
    atlas = render.SpriteAtlas()
    assert atlas.mapped_byte_len() == 0


def test_sprite_atlas_maps_exact_rgba_sprite_bytes_to_cpu_staging() -> None:
    pixels = bytes(index % 256 for index in range(SPRITE_BYTE_LEN))
    atlas = render.SpriteAtlas()

    assert atlas.map_buffer(pixels) is True

    assert atlas.mapped_pixels() == pixels
    assert atlas.mapped_byte_len() == SPRITE_BYTE_LEN
    assert atlas.mapped_sprite_count() == 1


def test_sprite_atlas_rejects_non_single_sprite_rgba_payloads() -> None:
    atlas = render.SpriteAtlas()

    for byte_len in (SPRITE_BYTE_LEN - 1, SPRITE_BYTE_LEN * 2):
        with pytest.raises(ValueError, match=str(SPRITE_BYTE_LEN)):
            atlas.map_buffer(b"\x00" * byte_len)
