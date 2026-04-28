from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pyrme.rendering.spr_frame_metadata import (
    SprMetadataParseError,
    parse_spr_frame_metadata,
    read_spr_frame_metadata,
)
from pyrme.rendering.sprite_catalog_adapter import (
    DatSpriteRecord,
    SprFrameRecord,
    build_sprite_catalog_from_asset_records,
)

if TYPE_CHECKING:
    from pathlib import Path


def _u16(value: int) -> bytes:
    return value.to_bytes(2, "little")


def _u32(value: int) -> bytes:
    return value.to_bytes(4, "little")


def _spr_blob(
    offsets: tuple[int, ...],
    *,
    signature: int = 0x12345678,
    extended: bool = False,
) -> bytes:
    count = len(offsets)
    header = bytearray(_u32(signature))
    header.extend(_u32(count) if extended else _u16(count))
    for offset in offsets:
        header.extend(_u32(offset))
    return bytes(header)


def test_parse_compact_spr_frame_table_emits_non_empty_sprite_records() -> None:
    metadata = parse_spr_frame_metadata(_spr_blob((0, 40, 96)))

    assert metadata.signature == 0x12345678
    assert metadata.sprite_count == 3
    assert metadata.extended is False
    assert metadata.records == (
        SprFrameRecord(
            sprite_id=2,
            frame_index=0,
            width=32,
            height=32,
            archive_offset=40,
        ),
        SprFrameRecord(
            sprite_id=3,
            frame_index=0,
            width=32,
            height=32,
            archive_offset=96,
        ),
    )


def test_parse_extended_spr_uses_u32_sprite_count() -> None:
    metadata = parse_spr_frame_metadata(
        _spr_blob((20,), extended=True),
        extended=True,
    )

    assert metadata.sprite_count == 1
    assert metadata.extended is True
    assert metadata.records == (
        SprFrameRecord(
            sprite_id=1,
            frame_index=0,
            width=32,
            height=32,
            archive_offset=20,
        ),
    )


def test_read_spr_frame_metadata_from_path(tmp_path: Path) -> None:
    spr_path = tmp_path / "Tibia.spr"
    spr_path.write_bytes(_spr_blob((24, 0)))

    metadata = read_spr_frame_metadata(spr_path)

    assert metadata.records == (
        SprFrameRecord(
            sprite_id=1,
            frame_index=0,
            width=32,
            height=32,
            archive_offset=24,
        ),
    )


def test_spr_frame_metadata_feeds_catalog_archive_offsets() -> None:
    spr_metadata = parse_spr_frame_metadata(_spr_blob((0, 44)))
    catalog = build_sprite_catalog_from_asset_records(
        dat_records=(DatSpriteRecord(item_id=100, sprite_id=2),),
        spr_frames=spr_metadata.records,
    )

    entry = catalog.resolve(100)

    assert entry is not None
    assert entry.metadata is not None
    assert entry.metadata["sprite_frames"] == (
        {
            "frame_index": 0,
            "size": (32, 32),
            "offset": (0, 0),
            "archive_offset": 44,
        },
    )


def test_zero_sprite_archive_is_valid_empty_metadata() -> None:
    metadata = parse_spr_frame_metadata(_spr_blob(()))

    assert metadata.sprite_count == 0
    assert metadata.records == ()


def test_excessive_spr_count_is_rejected_before_offsets() -> None:
    with pytest.raises(SprMetadataParseError, match="exceeds limit"):
        parse_spr_frame_metadata(_spr_blob((0, 0, 0)), max_sprite_count=2)


def test_truncated_spr_offset_table_fails_with_context() -> None:
    blob = _spr_blob((16, 32))

    with pytest.raises(SprMetadataParseError, match="Unexpected end of SPR data"):
        parse_spr_frame_metadata(blob[:-1])
