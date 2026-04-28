from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pyrme.rendering.spr_compressed_payload import (
    SprCompressedPayload,
    SprCompressedPayloadError,
    parse_spr_compressed_payload,
    read_spr_compressed_payload,
)
from pyrme.rendering.spr_frame_metadata import parse_spr_frame_metadata
from pyrme.rendering.sprite_catalog_adapter import SprFrameRecord

if TYPE_CHECKING:
    from pathlib import Path


def _u16(value: int) -> bytes:
    return value.to_bytes(2, "little")


def _u32(value: int) -> bytes:
    return value.to_bytes(4, "little")


def _frame(
    *,
    sprite_id: int = 7,
    archive_offset: int = 10,
) -> SprFrameRecord:
    return SprFrameRecord(
        sprite_id=sprite_id,
        frame_index=0,
        width=32,
        height=32,
        archive_offset=archive_offset,
    )


def _payload_blob(
    payload: bytes,
    *,
    archive_offset: int = 10,
    sprite_data_header: bytes = b"\x10\x20\x30",
) -> bytes:
    blob = bytearray(b"\0" * archive_offset)
    blob.extend(sprite_data_header)
    blob.extend(_u16(len(payload)))
    blob.extend(payload)
    return bytes(blob)


def _spr_blob_with_payload(payload: bytes, *, archive_offset: int = 10) -> bytes:
    header = bytearray(_u32(0x12345678))
    header.extend(_u16(1))
    header.extend(_u32(archive_offset))
    assert len(header) == archive_offset
    header.extend(b"\x10\x20\x30")
    header.extend(_u16(len(payload)))
    header.extend(payload)
    return bytes(header)


def test_parse_spr_compressed_payload_skips_legacy_sprite_data_header() -> None:
    frame = _frame(archive_offset=10)

    payload = parse_spr_compressed_payload(_payload_blob(b"abc", archive_offset=10), frame)

    assert payload == SprCompressedPayload(
        sprite_id=7,
        archive_offset=10,
        compressed_size=3,
        payload=b"abc",
    )


def test_parse_spr_compressed_payload_uses_frame_table_archive_offset() -> None:
    spr = _spr_blob_with_payload(b"\x01\x02\x03\x04")
    metadata = parse_spr_frame_metadata(spr)

    payload = parse_spr_compressed_payload(spr, metadata.records[0])

    assert payload == SprCompressedPayload(
        sprite_id=1,
        archive_offset=10,
        compressed_size=4,
        payload=b"\x01\x02\x03\x04",
    )


def test_read_spr_compressed_payload_from_path(tmp_path: Path) -> None:
    spr_path = tmp_path / "Tibia.spr"
    spr_path.write_bytes(_payload_blob(b"\xaa\xbb", archive_offset=8))

    payload = read_spr_compressed_payload(spr_path, _frame(archive_offset=8))

    assert payload.payload == b"\xaa\xbb"
    assert payload.compressed_size == 2


def test_zero_sprite_id_returns_explicit_empty_payload_without_reading() -> None:
    payload = parse_spr_compressed_payload(b"", _frame(sprite_id=0, archive_offset=999))

    assert payload == SprCompressedPayload(
        sprite_id=0,
        archive_offset=999,
        compressed_size=0,
        payload=b"",
        empty=True,
    )


def test_zero_archive_offset_returns_explicit_empty_payload() -> None:
    payload = parse_spr_compressed_payload(b"", _frame(archive_offset=0))

    assert payload == SprCompressedPayload(
        sprite_id=7,
        archive_offset=0,
        compressed_size=0,
        payload=b"",
        empty=True,
    )


def test_negative_archive_offset_fails_with_context() -> None:
    with pytest.raises(SprCompressedPayloadError, match="negative"):
        parse_spr_compressed_payload(b"", _frame(archive_offset=-1))


def test_payload_offset_past_end_fails_with_context() -> None:
    with pytest.raises(SprCompressedPayloadError, match="outside SPR data"):
        parse_spr_compressed_payload(b"\0" * 10, _frame(archive_offset=9))


def test_truncated_payload_size_fails_with_context() -> None:
    with pytest.raises(SprCompressedPayloadError, match="compressed size"):
        parse_spr_compressed_payload(b"\0" * 10 + b"\x10\x20\x30\x04", _frame())


def test_truncated_payload_bytes_fail_with_context() -> None:
    blob = b"\0" * 10 + b"\x10\x20\x30" + _u16(4) + b"\xaa\xbb"

    with pytest.raises(SprCompressedPayloadError, match="compressed payload"):
        parse_spr_compressed_payload(blob, _frame())
