"""DAT item metadata parsing for sprite catalog records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pyrme.rendering.sprite_catalog_adapter import DatSpriteRecord

if TYPE_CHECKING:
    from os import PathLike


MAX_DAT_SPRITES = 3_000_000
DAT_FIRST_ITEM_ID = 100
DAT_FLAG_LAST = 255
DatFormatName = Literal["74", "755", "78", "86", "96", "1010", "1050", "1057"]

_DAT_FORMAT_RANKS: dict[str, int] = {
    "74": 1,
    "755": 2,
    "78": 3,
    "86": 4,
    "96": 5,
    "1010": 6,
    "1050": 7,
    "1057": 8,
}


class DatMetadataParseError(ValueError):
    """Raised when DAT metadata cannot be parsed safely."""


@dataclass(frozen=True, slots=True)
class DatItemMetadata:
    signature: int
    item_count: int
    creature_count: int
    effect_count: int
    distance_count: int
    extended: bool
    records: tuple[DatSpriteRecord, ...]


_FLAG_NAMES: dict[int, str] = {
    0: "ground",
    1: "ground_border",
    2: "on_bottom",
    3: "on_top",
    4: "container",
    5: "stackable",
    6: "force_use",
    7: "multi_use",
    8: "writable",
    9: "writable_once",
    10: "fluid_container",
    11: "splash",
    12: "not_walkable",
    13: "not_moveable",
    14: "block_projectile",
    15: "not_pathable",
    16: "pickupable",
    17: "hangable",
    18: "hook_south",
    19: "hook_east",
    20: "rotateable",
    21: "light",
    22: "dont_hide",
    23: "translucent",
    24: "displacement",
    25: "elevation",
    26: "lying_corpse",
    27: "animate_always",
    28: "minimap_color",
    29: "lens_help",
    30: "full_ground",
    31: "look",
    32: "cloth",
    33: "market",
    34: "usable",
    35: "wrappable",
    36: "unwrappable",
    37: "top_effect",
    38: "wings",
    40: "default",
    252: "floor_change",
    253: "no_move_animation",
    254: "chargeable",
}


class _DatReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    def read_u8(self) -> int:
        return self._read_int(1)

    def read_u16(self) -> int:
        return self._read_int(2)

    def read_u32(self) -> int:
        return self._read_int(4)

    def skip(self, length: int) -> None:
        self._require(length)
        self._offset += length

    def skip_string(self) -> None:
        length = self.read_u16()
        self.skip(length)

    def _read_int(self, length: int) -> int:
        self._require(length)
        start = self._offset
        self._offset += length
        return int.from_bytes(self._data[start : start + length], "little")

    def _require(self, length: int) -> None:
        if self._offset + length > len(self._data):
            raise DatMetadataParseError(
                f"Unexpected end of DAT data at offset {self._offset}."
            )


def parse_dat_item_metadata(
    data: bytes | bytearray | memoryview,
    *,
    dat_format: DatFormatName | str = "86",
    extended: bool = False,
    include_creatures: bool = False,
    has_frame_durations: bool = False,
    has_frame_groups: bool = False,
    legacy_74_pattern_z: bool | None = None,
    max_sprite_count: int = MAX_DAT_SPRITES,
) -> DatItemMetadata:
    """Parse DAT item metadata into sprite catalog adapter records.

    The default layout matches the legacy parser's modern non-frame-group path:
    header counts, item ids from 100, compact or extended sprite ids, and no SPR
    pixel decoding.
    """

    format_rank = _dat_format_rank(dat_format)
    if legacy_74_pattern_z is None:
        legacy_74_pattern_z = format_rank == _DAT_FORMAT_RANKS["74"]

    reader = _DatReader(bytes(data))
    signature = reader.read_u32()
    item_count = reader.read_u16()
    creature_count = reader.read_u16()
    effect_count = reader.read_u16()
    distance_count = reader.read_u16()

    if item_count < DAT_FIRST_ITEM_ID or creature_count == 0:
        raise DatMetadataParseError(
            "Invalid DAT header counts: "
            f"item_count={item_count}, creature_count={creature_count}."
        )

    records: list[DatSpriteRecord] = []
    last_client_id = item_count + creature_count
    for client_id in range(DAT_FIRST_ITEM_ID, last_client_id + 1):
        flags = _read_flags(reader, client_id, format_rank)
        group_count = 1
        is_creature = client_id > item_count
        if has_frame_groups and is_creature:
            group_count = reader.read_u8()

        first_sprite_id: int | None = None
        for group_index in range(group_count):
            group_first_sprite_id = _read_sprite_group(
                reader,
                client_id=client_id,
                extended=extended,
                has_frame_durations=has_frame_durations,
                has_frame_groups=has_frame_groups and is_creature,
                legacy_74_pattern_z=legacy_74_pattern_z,
                max_sprite_count=max_sprite_count,
            )
            if group_index == 0:
                first_sprite_id = group_first_sprite_id

        if first_sprite_id is None:
            raise DatMetadataParseError(
                f"Missing sprite group for DAT client id {client_id}."
            )
        if client_id <= item_count or include_creatures:
            records.append(
                DatSpriteRecord(
                    item_id=client_id,
                    sprite_id=first_sprite_id,
                    flags=frozenset(flags),
                )
            )

    return DatItemMetadata(
        signature=signature,
        item_count=item_count,
        creature_count=creature_count,
        effect_count=effect_count,
        distance_count=distance_count,
        extended=extended,
        records=tuple(records),
    )


def read_dat_item_metadata(
    path: str | PathLike[str],
    **parse_options: object,
) -> DatItemMetadata:
    return parse_dat_item_metadata(Path(path).read_bytes(), **parse_options)


def _dat_format_rank(dat_format: DatFormatName | str) -> int:
    key = str(dat_format)
    try:
        return _DAT_FORMAT_RANKS[key]
    except KeyError as exc:
        supported = ", ".join(_DAT_FORMAT_RANKS)
        raise DatMetadataParseError(
            f"Unsupported DAT format {key!r}; expected one of: {supported}."
        ) from exc


def _read_flags(reader: _DatReader, client_id: int, format_rank: int) -> set[str]:
    flags: set[str] = set()
    previous_flag = DAT_FLAG_LAST

    for _ in range(DAT_FLAG_LAST):
        raw_flag = reader.read_u8()
        if raw_flag == DAT_FLAG_LAST:
            return flags

        flag = _remap_flag(raw_flag, format_rank)
        flag_name = _FLAG_NAMES.get(flag)
        if flag_name is None:
            raise DatMetadataParseError(
                f"Unknown DAT flag {flag} from raw flag {raw_flag} "
                f"after {previous_flag} for client id {client_id}."
            )
        flags.add(flag_name)
        _skip_flag_payload(reader, flag, format_rank)
        previous_flag = raw_flag

    raise DatMetadataParseError(
        f"DAT flag list exceeded limit for client id {client_id}."
    )


def _remap_flag(flag: int, format_rank: int) -> int:
    if format_rank >= _DAT_FORMAT_RANKS["1010"]:
        if flag == 16:
            return 253
        if flag > 16:
            return flag - 1
    elif format_rank >= _DAT_FORMAT_RANKS["86"]:
        return flag
    elif format_rank >= _DAT_FORMAT_RANKS["78"]:
        if flag == 8:
            return 254
        if flag > 8:
            return flag - 1
    elif format_rank >= _DAT_FORMAT_RANKS["755"]:
        if flag == 23:
            return 252
    elif format_rank >= _DAT_FORMAT_RANKS["74"]:
        if 0 < flag <= 15:
            return flag + 1
        return {
            16: 21,
            17: 252,
            18: 30,
            19: 25,
            20: 24,
            22: 28,
            23: 20,
            24: 26,
            25: 17,
            26: 18,
            27: 19,
            28: 27,
        }.get(flag, flag)
    return flag


def _skip_flag_payload(reader: _DatReader, flag: int, format_rank: int) -> None:
    if flag in {0, 8, 9, 25, 28, 29, 32, 34}:
        reader.skip(2)
    elif flag in {21, 24}:
        if flag != 24 or format_rank >= _DAT_FORMAT_RANKS["755"]:
            reader.skip(4)
    elif flag == 33:
        reader.skip(6)
        reader.skip_string()
        reader.skip(4)
    elif flag == 38:
        reader.skip(16)


def _read_sprite_group(
    reader: _DatReader,
    *,
    client_id: int,
    extended: bool,
    has_frame_durations: bool,
    has_frame_groups: bool,
    legacy_74_pattern_z: bool,
    max_sprite_count: int,
) -> int:
    if has_frame_groups:
        reader.skip(1)

    width = reader.read_u8()
    height = reader.read_u8()
    if width > 1 or height > 1:
        reader.skip(1)
    layers = reader.read_u8()
    pattern_x = reader.read_u8()
    pattern_y = reader.read_u8()
    pattern_z = 1 if legacy_74_pattern_z else reader.read_u8()
    frames = reader.read_u8()

    _skip_frame_durations(reader, frames, has_frame_durations)
    _validate_sprite_dimensions(
        client_id=client_id,
        width=width,
        height=height,
        layers=layers,
        pattern_x=pattern_x,
        pattern_y=pattern_y,
        pattern_z=pattern_z,
        frames=frames,
    )

    sprite_count = _sprite_count(
        width=width,
        height=height,
        layers=layers,
        pattern_x=pattern_x,
        pattern_y=pattern_y,
        pattern_z=pattern_z,
        frames=frames,
    )
    if sprite_count > max_sprite_count:
        raise DatMetadataParseError(
            f"DAT sprite group for client id {client_id} expands to "
            f"{sprite_count} sprites, exceeding limit {max_sprite_count}."
        )

    first_sprite_id = _read_sprite_id(reader, extended)
    if first_sprite_id >= max_sprite_count:
        raise DatMetadataParseError(
            f"DAT sprite id {first_sprite_id} for client id {client_id} "
            f"exceeds limit {max_sprite_count}."
        )
    for _ in range(sprite_count - 1):
        sprite_id = _read_sprite_id(reader, extended)
        if sprite_id >= max_sprite_count:
            raise DatMetadataParseError(
                f"DAT sprite id {sprite_id} for client id {client_id} "
                f"exceeds limit {max_sprite_count}."
            )
    return first_sprite_id


def _skip_frame_durations(
    reader: _DatReader,
    frames: int,
    has_frame_durations: bool,
) -> None:
    if frames <= 1 or not has_frame_durations:
        return
    reader.skip(1)
    reader.skip(4)
    reader.skip(1)
    reader.skip(frames * 8)


def _validate_sprite_dimensions(
    *,
    client_id: int,
    width: int,
    height: int,
    layers: int,
    pattern_x: int,
    pattern_y: int,
    pattern_z: int,
    frames: int,
) -> None:
    dimensions = {
        "width": width,
        "height": height,
        "layers": layers,
        "pattern_x": pattern_x,
        "pattern_y": pattern_y,
        "pattern_z": pattern_z,
        "frames": frames,
    }
    zero_names = [name for name, value in dimensions.items() if value == 0]
    if zero_names:
        joined = ", ".join(zero_names)
        raise DatMetadataParseError(
            f"Invalid DAT sprite dimensions for client id {client_id}: {joined}."
        )


def _sprite_count(
    *,
    width: int,
    height: int,
    layers: int,
    pattern_x: int,
    pattern_y: int,
    pattern_z: int,
    frames: int,
) -> int:
    return width * height * layers * pattern_x * pattern_y * pattern_z * frames


def _read_sprite_id(reader: _DatReader, extended: bool) -> int:
    return reader.read_u32() if extended else reader.read_u16()


__all__ = [
    "DAT_FIRST_ITEM_ID",
    "DAT_FLAG_LAST",
    "MAX_DAT_SPRITES",
    "DatFormatName",
    "DatItemMetadata",
    "DatMetadataParseError",
    "parse_dat_item_metadata",
    "read_dat_item_metadata",
]
