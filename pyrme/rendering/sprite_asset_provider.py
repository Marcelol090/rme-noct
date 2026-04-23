"""Sprite draw asset input providers.

The provider seam owns already-materialized sprite catalog and atlas inputs.
File discovery, decoding, and texture upload remain separate renderer slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from pyrme.rendering.sprite_catalog_adapter import build_sprite_catalog_from_asset_records
from pyrme.rendering.sprite_draw_commands import SpriteAtlas

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyrme.rendering.sprite_catalog_adapter import DatSpriteRecord, SprFrameRecord
    from pyrme.rendering.sprite_draw_commands import SpriteAtlasRegion
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


@dataclass(frozen=True, slots=True)
class SpriteDrawAssetBundle:
    dat_records: tuple[DatSpriteRecord, ...] = ()
    spr_frames: tuple[SprFrameRecord, ...] = ()
    atlas_regions: tuple[SpriteAtlasRegion, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "dat_records", tuple(self.dat_records))
        object.__setattr__(self, "spr_frames", tuple(self.spr_frames))
        object.__setattr__(self, "atlas_regions", tuple(self.atlas_regions))

    def sprite_draw_inputs(self) -> SpriteDrawAssetInputs:
        return SpriteDrawAssetInputs(
            catalog=build_sprite_catalog_from_asset_records(
                dat_records=self.dat_records,
                spr_frames=self.spr_frames,
            ),
            atlas=SpriteAtlas(self.atlas_regions),
        )


def build_sprite_draw_asset_bundle(
    *,
    dat_records: Iterable[DatSpriteRecord] = (),
    spr_frames: Iterable[SprFrameRecord] = (),
    atlas_regions: Iterable[SpriteAtlasRegion] = (),
) -> SpriteDrawAssetBundle:
    return SpriteDrawAssetBundle(
        dat_records=tuple(dat_records),
        spr_frames=tuple(spr_frames),
        atlas_regions=tuple(atlas_regions),
    )
