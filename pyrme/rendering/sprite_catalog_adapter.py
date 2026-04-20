"""Adapter helpers that turn DAT-like item records into sprite catalogs."""

from __future__ import annotations

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


def build_sprite_catalog_from_dat_records(
    records: Iterable[DatSpriteRecord],
) -> SpriteCatalog:
    return SpriteCatalog(
        SpriteCatalogEntry(
            item_id=record.item_id,
            sprite_id=record.sprite_id,
            metadata=_record_metadata(record),
        )
        for record in records
    )


def _record_metadata(record: DatSpriteRecord) -> Mapping[str, Any]:
    return MappingProxyType(
        {
            "source": "dat",
            "name": record.name,
            "flags": tuple(sorted(record.flags)),
        }
    )
