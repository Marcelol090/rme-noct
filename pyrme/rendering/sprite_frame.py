"""Sprite catalog seam for renderer-facing frame planning."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from typing import Any

    from pyrme.editor import MapPosition
    from pyrme.rendering.frame_plan import RenderFramePlan, RenderTileCommand
    from pyrme.ui.viewport import ViewportSnapshot


@dataclass(frozen=True, slots=True)
class SpriteCatalogEntry:
    item_id: int
    sprite_id: int
    metadata: Mapping[str, Any] | None = None


class SpriteCatalog:
    """Immutable lookup seam between item ids and sprite catalog entries."""

    __slots__ = ("_entries_by_item_id",)

    def __init__(self, entries: Iterable[SpriteCatalogEntry] = ()) -> None:
        self._entries_by_item_id = MappingProxyType(
            {entry.item_id: entry for entry in entries}
        )

    def resolve(self, item_id: int) -> SpriteCatalogEntry | None:
        return self._entries_by_item_id.get(item_id)

    @property
    def item_ids(self) -> tuple[int, ...]:
        return tuple(sorted(self._entries_by_item_id))


@dataclass(frozen=True, slots=True)
class SpriteTileCommand:
    position: MapPosition
    ground_entry: SpriteCatalogEntry | None
    item_entries: tuple[SpriteCatalogEntry, ...]
    unresolved_item_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SpriteFrame:
    viewport: ViewportSnapshot
    visible_rect: tuple[float, float, float, float]
    tile_commands: tuple[SpriteTileCommand, ...]
    unresolved_item_ids: tuple[int, ...]

    @property
    def tile_count(self) -> int:
        return len(self.tile_commands)


def build_sprite_frame(
    frame_plan: RenderFramePlan,
    catalog: SpriteCatalog,
) -> SpriteFrame:
    tile_commands = tuple(
        _build_sprite_tile_command(command, catalog)
        for command in frame_plan.tile_commands
    )
    unresolved_item_ids = tuple(
        sorted(
            {
                item_id
                for command in tile_commands
                for item_id in command.unresolved_item_ids
            }
        )
    )
    return SpriteFrame(
        viewport=frame_plan.viewport,
        visible_rect=frame_plan.visible_rect,
        tile_commands=tile_commands,
        unresolved_item_ids=unresolved_item_ids,
    )


def _build_sprite_tile_command(
    command: RenderTileCommand,
    catalog: SpriteCatalog,
) -> SpriteTileCommand:
    ground_entry = (
        catalog.resolve(command.ground_item_id)
        if command.ground_item_id is not None
        else None
    )
    item_entries = tuple(
        entry
        for item_id in command.item_ids
        if (entry := catalog.resolve(item_id)) is not None
    )
    unresolved_item_ids = tuple(
        sorted(
            {
                item_id
                for item_id in _tile_item_ids(command.ground_item_id, command.item_ids)
                if catalog.resolve(item_id) is None
            }
        )
    )
    return SpriteTileCommand(
        position=command.position,
        ground_entry=ground_entry,
        item_entries=item_entries,
        unresolved_item_ids=unresolved_item_ids,
    )


def _tile_item_ids(
    ground_item_id: int | None,
    item_ids: tuple[int, ...],
) -> tuple[int, ...]:
    if ground_item_id is None:
        return item_ids
    return (ground_item_id, *item_ids)
