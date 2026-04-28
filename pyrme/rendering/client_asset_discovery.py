"""Client asset file discovery before DAT/SPR parsing exists."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike

    from pyrme.rendering.sprite_asset_provider import (
        SpriteDrawAssetBundle,
        SpriteDrawAssetInputs,
    )

DEFAULT_METADATA_FILE_NAME = "Tibia.dat"
DEFAULT_SPRITES_FILE_NAME = "Tibia.spr"
MISSING_ROOT_WARNING = (
    "Client asset detection skipped: selected client path does not exist."
)
MISSING_DAT_WARNING = (
    "Client asset detection failed: DAT file was not found in the selected client path."
)
MISSING_SPR_WARNING = (
    "Client asset detection failed: SPR file was not found in the selected client path."
)


@dataclass(frozen=True, slots=True)
class ClientAssetFiles:
    client_root: Path
    metadata_file_name: str
    sprites_file_name: str
    metadata_path: Path | None
    sprites_path: Path | None
    warnings: tuple[str, ...] = ()

    @property
    def is_complete(self) -> bool:
        return self.metadata_path is not None and self.sprites_path is not None


@dataclass(frozen=True, slots=True)
class ClientAssetSignatures:
    dat_signature: int | None
    spr_signature: int | None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ClientSpriteAssetBundle:
    files: ClientAssetFiles
    bundle: SpriteDrawAssetBundle

    def sprite_draw_inputs(self) -> SpriteDrawAssetInputs:
        return self.bundle.sprite_draw_inputs()


@dataclass(frozen=True, slots=True)
class _ResolvedClientFile:
    file_name: str
    path: Path | None


def discover_client_asset_files(
    client_root: str | PathLike[str],
    *,
    metadata_file_name: str = DEFAULT_METADATA_FILE_NAME,
    sprites_file_name: str = DEFAULT_SPRITES_FILE_NAME,
) -> ClientAssetFiles:
    root = Path(client_root)
    configured_metadata = _sanitize_file_name(metadata_file_name)
    configured_sprites = _sanitize_file_name(sprites_file_name)
    if not root.is_dir():
        return ClientAssetFiles(
            client_root=root,
            metadata_file_name=configured_metadata,
            sprites_file_name=configured_sprites,
            metadata_path=None,
            sprites_path=None,
            warnings=(MISSING_ROOT_WARNING,),
        )

    metadata = _resolve_client_file(
        root,
        configured_metadata,
        DEFAULT_METADATA_FILE_NAME,
    )
    sprites = _resolve_client_file(
        root,
        configured_sprites,
        DEFAULT_SPRITES_FILE_NAME,
    )
    warnings: list[str] = []
    if metadata.path is None:
        warnings.append(MISSING_DAT_WARNING)
    if sprites.path is None:
        warnings.append(MISSING_SPR_WARNING)
    return ClientAssetFiles(
        client_root=root,
        metadata_file_name=metadata.file_name,
        sprites_file_name=sprites.file_name,
        metadata_path=metadata.path,
        sprites_path=sprites.path,
        warnings=tuple(warnings),
    )


def read_client_asset_signatures(files: ClientAssetFiles) -> ClientAssetSignatures:
    if not files.is_complete:
        return ClientAssetSignatures(
            dat_signature=None,
            spr_signature=None,
            warnings=files.warnings,
        )

    dat_signature, dat_warnings = _read_signature(files.metadata_path, "DAT")
    spr_signature, spr_warnings = _read_signature(files.sprites_path, "SPR")
    return ClientAssetSignatures(
        dat_signature=dat_signature,
        spr_signature=spr_signature,
        warnings=(*files.warnings, *dat_warnings, *spr_warnings),
    )


def _resolve_client_file(
    client_root: Path,
    configured_name: str,
    fallback_name: str,
) -> _ResolvedClientFile:
    configured_path = client_root / configured_name
    if configured_name and configured_path.is_file():
        return _ResolvedClientFile(file_name=configured_name, path=configured_path)
    sanitized_fallback = _sanitize_file_name(fallback_name)
    fallback_path = client_root / sanitized_fallback
    return _ResolvedClientFile(
        file_name=sanitized_fallback,
        path=fallback_path if fallback_path.is_file() else None,
    )


def _sanitize_file_name(raw_name: str) -> str:
    posix_name = PurePosixPath(raw_name).name
    return PureWindowsPath(posix_name).name


def _read_signature(path: Path | None, label: str) -> tuple[int | None, tuple[str, ...]]:
    if path is None:
        return None, ()
    try:
        with path.open("rb") as handle:
            data = handle.read(4)
    except OSError:
        return None, (f"{label} signature detection failed: could not open {path}",)
    if len(data) != 4:
        return None, (
            f"{label} signature detection failed: could not read header from {path}",
        )
    return int.from_bytes(data, byteorder="little"), ()
