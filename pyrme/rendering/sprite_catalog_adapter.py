"""Adapter helpers that turn DAT-like item records into sprite catalogs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from pyrme.rendering.sprite_frame import SpriteCatalog, SpriteCatalogEntry

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class DatSpriteRecord:
    item_id: int
    sprite_id: int
    name: str | None = None
    flags: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class SprFrameRecord:
    sprite_id: int
    frame_index: int
    width: int
    height: int
    offset_x: int = 0
    offset_y: int = 0


def build_sprite_catalog_from_dat_records(
    records: Iterable[DatSpriteRecord],
) -> SpriteCatalog:
    return build_sprite_catalog_from_asset_records(dat_records=records, spr_frames=())


def build_sprite_catalog_from_asset_records(
    dat_records: Iterable[DatSpriteRecord],
    spr_frames: Iterable[SprFrameRecord],
) -> SpriteCatalog:
    frames_by_sprite_id = _group_spr_frames(spr_frames)
    return SpriteCatalog(
        SpriteCatalogEntry(
            item_id=record.item_id,
            sprite_id=record.sprite_id,
            metadata=_record_metadata(record, frames_by_sprite_id.get(record.sprite_id, ())),
        )
        for record in dat_records
    )


def _record_metadata(
    record: DatSpriteRecord,
    spr_frames: tuple[SprFrameRecord, ...],
) -> Mapping[str, Any]:
    return MappingProxyType(
        {
            "source": "dat",
            "name": record.name,
            "flags": tuple(sorted(record.flags)),
            "sprite_frames": tuple(_frame_metadata(frame) for frame in spr_frames),
        }
    )


def _group_spr_frames(
    spr_frames: Iterable[SprFrameRecord],
) -> dict[int, tuple[SprFrameRecord, ...]]:
    groups: defaultdict[int, list[SprFrameRecord]] = defaultdict(list)
    for frame in spr_frames:
        groups[frame.sprite_id].append(frame)
    return {
        sprite_id: tuple(sorted(frames, key=lambda frame: frame.frame_index))
        for sprite_id, frames in groups.items()
    }


def _frame_metadata(frame: SprFrameRecord) -> Mapping[str, Any]:
    return MappingProxyType(
        {
            "frame_index": frame.frame_index,
            "size": (frame.width, frame.height),
            "offset": (frame.offset_x, frame.offset_y),
        }
    )
