"""SPR frame table metadata parsing for sprite catalog records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyrme.rendering.sprite_catalog_adapter import SprFrameRecord

if TYPE_CHECKING:
    from os import PathLike


MAX_SPR_SPRITES = 3_000_000
SPR_FRAME_SIZE = 32


class SprMetadataParseError(ValueError):
    """Raised when SPR frame metadata cannot be parsed safely."""


@dataclass(frozen=True, slots=True)
class SprFrameMetadata:
    signature: int
    sprite_count: int
    extended: bool
    records: tuple[SprFrameRecord, ...]


class _SprReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    def read_u16(self) -> int:
        return self._read_int(2)

    def read_u32(self) -> int:
        return self._read_int(4)

    def _read_int(self, length: int) -> int:
        self._require(length)
        start = self._offset
        self._offset += length
        return int.from_bytes(self._data[start : start + length], "little")

    def _require(self, length: int) -> None:
        if self._offset + length > len(self._data):
            raise SprMetadataParseError(
                f"Unexpected end of SPR data at offset {self._offset}."
            )


def parse_spr_frame_metadata(
    data: bytes | bytearray | memoryview,
    *,
    extended: bool = False,
    max_sprite_count: int = MAX_SPR_SPRITES,
) -> SprFrameMetadata:
    """Parse SPR header and offset table without decoding sprite pixels.

    Legacy SPR archives store one fixed 32x32 sprite frame per sprite id. The
    offset table points to compressed pixel payloads; this parser records those
    offsets for future pixel decoding while keeping pixel reads out of scope.
    """

    reader = _SprReader(bytes(data))
    signature = reader.read_u32()
    sprite_count = reader.read_u32() if extended else reader.read_u16()
    if sprite_count > max_sprite_count:
        raise SprMetadataParseError(
            f"SPR sprite count {sprite_count} exceeds limit {max_sprite_count}."
        )

    records: list[SprFrameRecord] = []
    for sprite_id in range(1, sprite_count + 1):
        archive_offset = reader.read_u32()
        if archive_offset == 0:
            continue
        records.append(
            SprFrameRecord(
                sprite_id=sprite_id,
                frame_index=0,
                width=SPR_FRAME_SIZE,
                height=SPR_FRAME_SIZE,
                archive_offset=archive_offset,
            )
        )

    return SprFrameMetadata(
        signature=signature,
        sprite_count=sprite_count,
        extended=extended,
        records=tuple(records),
    )


def read_spr_frame_metadata(
    path: str | PathLike[str],
    *,
    extended: bool = False,
    max_sprite_count: int = MAX_SPR_SPRITES,
) -> SprFrameMetadata:
    return parse_spr_frame_metadata(
        Path(path).read_bytes(),
        extended=extended,
        max_sprite_count=max_sprite_count,
    )


__all__ = [
    "MAX_SPR_SPRITES",
    "SPR_FRAME_SIZE",
    "SprFrameMetadata",
    "SprMetadataParseError",
    "parse_spr_frame_metadata",
    "read_spr_frame_metadata",
]
