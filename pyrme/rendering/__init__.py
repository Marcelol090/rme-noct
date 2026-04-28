"""Renderer planning helpers for the Python editor shell."""

from pyrme.rendering.client_asset_discovery import (
    ClientAssetFiles,
    ClientAssetSignatures,
    ClientSpriteAssetBundle,
    discover_client_asset_files,
    read_client_asset_signatures,
)
from pyrme.rendering.dat_item_metadata import (
    DAT_FIRST_ITEM_ID,
    DAT_FLAG_LAST,
    MAX_DAT_SPRITES,
    DatFormatName,
    DatItemMetadata,
    DatMetadataParseError,
    parse_dat_item_metadata,
    read_dat_item_metadata,
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
from pyrme.rendering.spr_compressed_payload import (
    SPR_LEGACY_PAYLOAD_HEADER_SIZE,
    SprCompressedPayload,
    SprCompressedPayloadError,
    parse_spr_compressed_payload,
    read_spr_compressed_payload,
)
from pyrme.rendering.spr_frame_metadata import (
    MAX_SPR_SPRITES,
    SPR_FRAME_SIZE,
    SprFrameMetadata,
    SprMetadataParseError,
    parse_spr_frame_metadata,
    read_spr_frame_metadata,
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

__all__ = [
    "DiagnosticTilePrimitive",
    "ClientAssetFiles",
    "ClientAssetSignatures",
    "ClientSpriteAssetBundle",
    "DAT_FIRST_ITEM_ID",
    "DAT_FLAG_LAST",
    "DatSpriteRecord",
    "DatFormatName",
    "DatItemMetadata",
    "DatMetadataParseError",
    "MAX_DAT_SPRITES",
    "MAX_SPR_SPRITES",
    "RenderFramePlan",
    "RenderTileCommand",
    "SPR_LEGACY_PAYLOAD_HEADER_SIZE",
    "SPR_FRAME_SIZE",
    "SprCompressedPayload",
    "SprCompressedPayloadError",
    "SprFrameRecord",
    "SprFrameMetadata",
    "SprMetadataParseError",
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
    "SpriteTileCommand",
    "StaticSpriteDrawAssetProvider",
    "build_diagnostic_tile_primitives",
    "discover_client_asset_files",
    "read_client_asset_signatures",
    "parse_dat_item_metadata",
    "read_dat_item_metadata",
    "parse_spr_compressed_payload",
    "read_spr_compressed_payload",
    "parse_spr_frame_metadata",
    "read_spr_frame_metadata",
    "build_render_frame_plan",
    "build_sprite_draw_asset_bundle",
    "build_sprite_catalog_from_asset_records",
    "build_sprite_catalog_from_dat_records",
    "build_sprite_draw_plan",
    "build_sprite_frame",
]
