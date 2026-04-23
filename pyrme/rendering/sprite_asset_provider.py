"""Sprite draw asset input providers.

The provider seam owns already-materialized sprite catalog and atlas inputs.
File discovery, decoding, and texture upload remain separate renderer slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pyrme.rendering.sprite_draw_commands import SpriteAtlas
    from pyrme.rendering.sprite_frame import SpriteCatalog


@dataclass(frozen=True, slots=True)
class SpriteDrawAssetInputs:
    catalog: SpriteCatalog
    atlas: SpriteAtlas


class SpriteDrawAssetProvider(Protocol):
    def sprite_draw_inputs(self) -> SpriteDrawAssetInputs: ...


@dataclass(frozen=True, slots=True)
class StaticSpriteDrawAssetProvider:
    inputs: SpriteDrawAssetInputs

    def sprite_draw_inputs(self) -> SpriteDrawAssetInputs:
        return self.inputs
