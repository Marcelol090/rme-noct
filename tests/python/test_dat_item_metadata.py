from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pyrme.rendering.dat_item_metadata import (
    DatMetadataParseError,
    parse_dat_item_metadata,
    read_dat_item_metadata,
)
from pyrme.rendering.sprite_catalog_adapter import DatSpriteRecord

if TYPE_CHECKING:
    from pathlib import Path


def _u16(value: int) -> bytes:
    return value.to_bytes(2, "little")


def _u32(value: int) -> bytes:
    return value.to_bytes(4, "little")


def _entry(
    sprite_ids: tuple[int, ...],
    *,
    extended: bool = False,
    flags: bytes = b"\xff",
    width: int = 1,
    height: int = 1,
    layers: int = 1,
    pattern_x: int = 1,
    pattern_y: int = 1,
    pattern_z: int = 1,
    frames: int = 1,
    include_pattern_z: bool = True,
) -> bytes:
    data = bytearray(flags)
    data.extend((width, height))
    if width > 1 or height > 1:
        data.append(0)
    data.extend((layers, pattern_x, pattern_y))
    if include_pattern_z:
        data.append(pattern_z)
    data.append(frames)
    for sprite_id in sprite_ids:
        data.extend(_u32(sprite_id) if extended else _u16(sprite_id))
    return bytes(data)


def _dat_blob(
    item_entry: bytes,
    creature_entry: bytes,
    *,
    signature: int = 0x12345678,
    item_count: int = 100,
    creature_count: int = 1,
    effect_count: int = 0,
    distance_count: int = 0,
) -> bytes:
    return b"".join(
        (
            _u32(signature),
            _u16(item_count),
            _u16(creature_count),
            _u16(effect_count),
            _u16(distance_count),
            item_entry,
            creature_entry,
        )
    )


def test_parse_compact_dat_emits_item_sprite_record() -> None:
    metadata = parse_dat_item_metadata(
        _dat_blob(_entry((9001,)), _entry((9002,)))
    )

    assert metadata.signature == 0x12345678
    assert metadata.item_count == 100
    assert metadata.creature_count == 1
    assert metadata.records == (
        DatSpriteRecord(item_id=100, sprite_id=9001),
    )


def test_read_dat_item_metadata_from_path(tmp_path: Path) -> None:
    dat_path = tmp_path / "Tibia.dat"
    dat_path.write_bytes(_dat_blob(_entry((9001,)), _entry((9002,))))

    metadata = read_dat_item_metadata(dat_path)

    assert metadata.records == (
        DatSpriteRecord(item_id=100, sprite_id=9001),
    )


def test_ground_flag_payload_is_skipped_and_named() -> None:
    ground_flags = bytes((0,)) + _u16(150) + bytes((255,))
    metadata = parse_dat_item_metadata(
        _dat_blob(_entry((9001,), flags=ground_flags), _entry((9002,)))
    )

    assert metadata.records == (
        DatSpriteRecord(item_id=100, sprite_id=9001, flags=frozenset({"ground"})),
    )


def test_extended_dat_uses_u32_sprite_ids() -> None:
    metadata = parse_dat_item_metadata(
        _dat_blob(
            _entry((70000,), extended=True),
            _entry((70001,), extended=True),
        ),
        extended=True,
    )

    assert metadata.records == (
        DatSpriteRecord(item_id=100, sprite_id=70000),
    )


def test_dat_1010_remaps_raw_light_flag_before_payload_skip() -> None:
    light_flags = bytes((22,)) + _u16(10) + _u16(215) + bytes((255,))
    metadata = parse_dat_item_metadata(
        _dat_blob(_entry((9001,), flags=light_flags), _entry((9002,))),
        dat_format="1010",
    )

    assert metadata.records == (
        DatSpriteRecord(item_id=100, sprite_id=9001, flags=frozenset({"light"})),
    )


def test_dat_74_remaps_raw_light_flag_and_omits_pattern_z() -> None:
    light_flags = bytes((16,)) + _u16(10) + _u16(215) + bytes((255,))
    metadata = parse_dat_item_metadata(
        _dat_blob(
            _entry((9001,), flags=light_flags, include_pattern_z=False),
            _entry((9002,), include_pattern_z=False),
        ),
        dat_format="74",
    )

    assert metadata.records == (
        DatSpriteRecord(item_id=100, sprite_id=9001, flags=frozenset({"light"})),
    )


def test_invalid_header_counts_are_rejected() -> None:
    with pytest.raises(DatMetadataParseError, match="Invalid DAT header counts"):
        parse_dat_item_metadata(
            _dat_blob(
                _entry((9001,)),
                _entry((9002,)),
                item_count=99,
            )
        )


def test_unknown_dat_flag_is_rejected() -> None:
    unknown_flags = bytes((39, 255))

    with pytest.raises(DatMetadataParseError, match="Unknown DAT flag 39"):
        parse_dat_item_metadata(
            _dat_blob(_entry((9001,), flags=unknown_flags), _entry((9002,)))
        )


def test_zero_dimensions_are_rejected() -> None:
    with pytest.raises(
        DatMetadataParseError,
        match="Invalid DAT sprite dimensions for client id 100",
    ):
        parse_dat_item_metadata(
            _dat_blob(_entry((9001,), width=0), _entry((9002,)))
        )


def test_excessive_sprite_count_is_rejected_before_sprite_ids() -> None:
    with pytest.raises(DatMetadataParseError, match="expands to .* exceeding limit"):
        parse_dat_item_metadata(
            _dat_blob(
                _entry(
                    (9001,),
                    width=255,
                    height=255,
                    layers=255,
                    pattern_x=255,
                    pattern_y=255,
                    pattern_z=255,
                    frames=255,
                ),
                _entry((9002,)),
            )
        )


def test_truncated_sprite_id_fails_with_context() -> None:
    blob = _dat_blob(_entry((9001,)), _entry((9002,)))

    with pytest.raises(DatMetadataParseError, match="Unexpected end of DAT data"):
        parse_dat_item_metadata(blob[:-1])
