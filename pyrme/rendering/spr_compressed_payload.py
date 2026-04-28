"""SPR compressed payload reads for sprite frame records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike

    from pyrme.rendering.sprite_catalog_adapter import SprFrameRecord


SPR_LEGACY_PAYLOAD_HEADER_SIZE = 3


class SprCompressedPayloadError(ValueError):
    """Raised when raw SPR compressed payload bytes cannot be read safely."""


@dataclass(frozen=True, slots=True)
class SprCompressedPayload:
    sprite_id: int
    archive_offset: int
    compressed_size: int
    payload: bytes
    empty: bool = False


def parse_spr_compressed_payload(
    data: bytes | bytearray | memoryview,
    frame: SprFrameRecord,
) -> SprCompressedPayload:
    """Read raw compressed bytes for one SPR frame without decompression."""

    archive_offset = frame.archive_offset
    if frame.sprite_id == 0 or archive_offset == 0:
        return SprCompressedPayload(
            sprite_id=frame.sprite_id,
            archive_offset=archive_offset,
            compressed_size=0,
            payload=b"",
            empty=True,
        )
    if archive_offset < 0:
        raise SprCompressedPayloadError(
            f"SPR archive offset {archive_offset} is negative."
        )

    raw = bytes(data)
    size_offset = archive_offset + SPR_LEGACY_PAYLOAD_HEADER_SIZE
    if size_offset > len(raw):
        raise SprCompressedPayloadError(
            f"SPR archive offset {archive_offset} is outside SPR data length {len(raw)}."
        )
    if size_offset + 2 > len(raw):
        raise SprCompressedPayloadError(
            f"Unexpected end of SPR data while reading compressed size at offset {size_offset}."
        )

    compressed_size = int.from_bytes(raw[size_offset : size_offset + 2], "little")
    payload_start = size_offset + 2
    payload_end = payload_start + compressed_size
    if payload_end > len(raw):
        raise SprCompressedPayloadError(
            "Unexpected end of SPR data while reading compressed payload "
            f"at offset {payload_start} with size {compressed_size}."
        )

    return SprCompressedPayload(
        sprite_id=frame.sprite_id,
        archive_offset=archive_offset,
        compressed_size=compressed_size,
        payload=raw[payload_start:payload_end],
    )


def read_spr_compressed_payload(
    path: str | PathLike[str],
    frame: SprFrameRecord,
) -> SprCompressedPayload:
    return parse_spr_compressed_payload(Path(path).read_bytes(), frame)


__all__ = [
    "SPR_LEGACY_PAYLOAD_HEADER_SIZE",
    "SprCompressedPayload",
    "SprCompressedPayloadError",
    "parse_spr_compressed_payload",
    "read_spr_compressed_payload",
]
