"""Pure sprite draw command planning before real atlas rendering exists."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyrme.rendering.sprite_frame import SpriteCatalogEntry, SpriteFrame
    from pyrme.ui.viewport import EditorViewport


@dataclass(frozen=True, slots=True)
class SpriteAtlasRegion:
    sprite_id: int
    source_rect: tuple[int, int, int, int]


class SpriteAtlas:
    __slots__ = ("_regions_by_sprite_id",)

    def __init__(self, regions: Iterable[SpriteAtlasRegion] = ()) -> None:
        self._regions_by_sprite_id = MappingProxyType(
            {region.sprite_id: region for region in regions}
        )

    def resolve(self, sprite_id: int) -> SpriteAtlasRegion | None:
        return self._regions_by_sprite_id.get(sprite_id)


@dataclass(frozen=True, slots=True)
class SpriteDrawCommand:
    sprite_id: int
    item_id: int
    layer: int
    source_rect: tuple[int, int, int, int]
    destination_rect: tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class SpriteDrawPlan:
    commands: tuple[SpriteDrawCommand, ...]
    unresolved_sprite_ids: tuple[int, ...]


def build_sprite_draw_plan(
    sprite_frame: SpriteFrame,
    atlas: SpriteAtlas,
    viewport: EditorViewport,
) -> SpriteDrawPlan:
    commands: list[SpriteDrawCommand] = []
    unresolved: set[int] = set()
    for tile in sprite_frame.tile_commands:
        tile_x, tile_y = viewport.map_to_screen(
            tile.position.x,
            tile.position.y,
            tile.position.z,
        )
        for layer, entry in enumerate(_tile_entries(tile.ground_entry, tile.item_entries)):
            region = atlas.resolve(entry.sprite_id)
            if region is None:
                unresolved.add(entry.sprite_id)
                continue
            destination_rect = _destination_rect(tile_x, tile_y, entry)
            if destination_rect is None:
                unresolved.add(entry.sprite_id)
                continue
            commands.append(
                SpriteDrawCommand(
                    sprite_id=entry.sprite_id,
                    item_id=entry.item_id,
                    layer=layer,
                    source_rect=region.source_rect,
                    destination_rect=destination_rect,
                )
            )
    return SpriteDrawPlan(
        commands=tuple(commands),
        unresolved_sprite_ids=tuple(sorted(unresolved)),
    )


def _tile_entries(
    ground_entry: SpriteCatalogEntry | None,
    item_entries: tuple[SpriteCatalogEntry, ...],
) -> tuple[SpriteCatalogEntry, ...]:
    if ground_entry is None:
        return item_entries
    return (ground_entry, *item_entries)


def _destination_rect(
    tile_x: int,
    tile_y: int,
    entry: SpriteCatalogEntry,
) -> tuple[int, int, int, int] | None:
    frame_metadata = _first_sprite_frame(entry.metadata)
    if frame_metadata is None:
        return None
    size = _int_pair(frame_metadata.get("size"))
    offset = _int_pair(frame_metadata.get("offset"))
    if size is None or offset is None:
        return None
    width, height = size
    offset_x, offset_y = offset
    return (
        tile_x + int(offset_x),
        tile_y + int(offset_y),
        int(width),
        int(height),
    )


def _first_sprite_frame(
    metadata: Mapping[str, object] | None,
) -> Mapping[str, object] | None:
    if metadata is None:
        return None
    frames = metadata.get("sprite_frames")
    if not isinstance(frames, tuple) or not frames:
        return None
    first_frame = frames[0]
    if not isinstance(first_frame, Mapping):
        return None
    return first_frame


def _int_pair(value: object) -> tuple[int, int] | None:
    if not isinstance(value, tuple) or len(value) != 2:
        return None
    first, second = value
    if not isinstance(first, int) or not isinstance(second, int):
        return None
    return (first, second)
