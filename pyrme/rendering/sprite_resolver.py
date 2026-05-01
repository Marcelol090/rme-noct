"""Sprite resource lookup result contracts."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if sys.version_info >= (3, 11):  # noqa: UP036
    from enum import StrEnum
else:  # pragma: no cover - Python <3.11 local fallback.
    from enum import Enum

    class StrEnum(str, Enum):  # noqa: UP042
        pass

if TYPE_CHECKING:
    from collections.abc import Mapping


class SpriteLookupStatus(StrEnum):
    """Explicit sprite lookup outcome."""

    RESOLVED = "resolved"
    MISSING_ITEM = "missing_item"
    MISSING_SPRITE = "missing_sprite"


@dataclass(frozen=True, slots=True)
class SpriteResourceResult:
    """Immutable result for an item-id to sprite-resource lookup."""

    item_id: int
    status: SpriteLookupStatus
    sprite_id: int | None = None
    pixels: bytes | None = None
    reason: str = ""

    @property
    def available(self) -> bool:
        return self.status is SpriteLookupStatus.RESOLVED

    @classmethod
    def resolved(
        cls,
        *,
        item_id: int,
        sprite_id: int,
        pixels: bytes,
    ) -> SpriteResourceResult:
        return cls(
            item_id=item_id,
            status=SpriteLookupStatus.RESOLVED,
            sprite_id=sprite_id,
            pixels=pixels,
        )

    @classmethod
    def missing_item(cls, item_id: int) -> SpriteResourceResult:
        return cls(
            item_id=item_id,
            status=SpriteLookupStatus.MISSING_ITEM,
            reason="item id not found",
        )

    @classmethod
    def missing_sprite(cls, *, item_id: int, sprite_id: int) -> SpriteResourceResult:
        return cls(
            item_id=item_id,
            status=SpriteLookupStatus.MISSING_SPRITE,
            sprite_id=sprite_id,
            reason="sprite id not found",
        )


@dataclass(frozen=True, slots=True)
class SpriteItemMetadata:
    """Minimal item metadata needed to choose sprite resources."""

    item_id: int
    sprite_ids: tuple[int, ...]

    @property
    def primary_sprite_id(self) -> int | None:
        return self.sprite_ids[0] if self.sprite_ids else None


class SpriteResourceResolver:
    """Resolve item ids into sprite resource results."""

    def __init__(
        self,
        *,
        items: Mapping[int, SpriteItemMetadata],
        sprites: Mapping[int, bytes] | None = None,
    ) -> None:
        self._cache: dict[int, SpriteResourceResult] = {}
        self.replace_sources(items=items, sprites=sprites)

    def replace_sources(
        self,
        *,
        items: Mapping[int, SpriteItemMetadata],
        sprites: Mapping[int, bytes] | None = None,
    ) -> None:
        self._items = dict(items)
        self._sprites = dict(sprites or {})
        self._cache.clear()

    def resolve_item(self, item_id: int) -> SpriteResourceResult:
        cached = self._cache.get(item_id)
        if cached is not None:
            return cached

        item = self._items.get(item_id)
        if item is None:
            result = SpriteResourceResult.missing_item(item_id)
            self._cache[item_id] = result
            return result

        sprite_id = item.primary_sprite_id
        if sprite_id is None:
            result = SpriteResourceResult(
                item_id=item_id,
                status=SpriteLookupStatus.MISSING_SPRITE,
                reason="item has no sprite ids",
            )
            self._cache[item_id] = result
            return result
        pixels = self._sprites.get(sprite_id)
        if pixels is not None:
            result = SpriteResourceResult.resolved(
                item_id=item_id,
                sprite_id=sprite_id,
                pixels=pixels,
            )
            self._cache[item_id] = result
            return result
        result = SpriteResourceResult.missing_sprite(
            item_id=item_id,
            sprite_id=sprite_id,
        )
        self._cache[item_id] = result
        return result
