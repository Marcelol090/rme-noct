"""Renderer planning helpers for the Python editor shell."""

from pyrme.rendering.client_asset_discovery import (
    ClientAssetFiles,
    ClientAssetSignatures,
    ClientSpriteAssetBundle,
    discover_client_asset_files,
    read_client_asset_signatures,
)
from pyrme.rendering.diagnostic_primitives import (
    DiagnosticTilePrimitive,
    build_diagnostic_tile_primitives,
)
from pyrme.rendering.frame_plan import (
    RenderFramePlan,
    RenderTileCommand,
    build_render_frame_plan,
)
from pyrme.rendering.frame_sprite_resources import (
    FrameSpriteResource,
    build_frame_sprite_resources,
)
from pyrme.rendering.sprite_asset_provider import (
    SpriteDrawAssetBundle,
    SpriteDrawAssetInputs,
    SpriteDrawAssetProvider,
    StaticSpriteDrawAssetProvider,
    build_sprite_draw_asset_bundle,
)
from pyrme.rendering.sprite_catalog_adapter import (
    DatSpriteRecord,
    SprFrameRecord,
    build_sprite_catalog_from_asset_records,
    build_sprite_catalog_from_dat_records,
)
from pyrme.rendering.sprite_draw_commands import (
    SpriteAtlas,
    SpriteAtlasRegion,
    SpriteDrawCommand,
    SpriteDrawPlan,
    build_sprite_draw_plan,
)
from pyrme.rendering.sprite_frame import (
    SpriteCatalog,
    SpriteCatalogEntry,
    SpriteFrame,
    SpriteTileCommand,
    build_sprite_frame,
)
from pyrme.rendering.sprite_resolver import (
    SpriteItemMetadata,
    SpriteLookupStatus,
    SpriteResourceResolver,
    SpriteResourceResult,
)
from pyrme.rendering.sprite_resource_diagnostics import (
    SpriteResourceDiagnostics,
    build_sprite_resource_diagnostics,
)

__all__ = [
    "ClientAssetFiles",
    "ClientAssetSignatures",
    "ClientSpriteAssetBundle",
    "DatSpriteRecord",
    "DiagnosticTilePrimitive",
    "FrameSpriteResource",
    "RenderFramePlan",
    "RenderTileCommand",
    "SprFrameRecord",
    "SpriteAtlas",
    "SpriteAtlasRegion",
    "SpriteCatalog",
    "SpriteCatalogEntry",
    "SpriteDrawAssetBundle",
    "SpriteDrawAssetInputs",
    "SpriteDrawAssetProvider",
    "SpriteDrawCommand",
    "SpriteDrawPlan",
    "SpriteFrame",
    "SpriteItemMetadata",
    "SpriteLookupStatus",
    "SpriteResourceDiagnostics",
    "SpriteResourceResolver",
    "SpriteResourceResult",
    "SpriteTileCommand",
    "StaticSpriteDrawAssetProvider",
    "build_sprite_catalog_from_asset_records",
    "build_sprite_catalog_from_dat_records",
    "build_diagnostic_tile_primitives",
    "build_frame_sprite_resources",
    "build_render_frame_plan",
    "build_sprite_draw_asset_bundle",
    "build_sprite_draw_plan",
    "build_sprite_frame",
    "build_sprite_resource_diagnostics",
    "discover_client_asset_files",
    "read_client_asset_signatures",
]
