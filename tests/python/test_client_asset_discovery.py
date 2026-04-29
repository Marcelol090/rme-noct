from __future__ import annotations

from unittest.mock import patch

from pyrme.rendering import (
    ClientSpriteAssetBundle,
    SpriteAtlasRegion,
    build_sprite_draw_asset_bundle,
    discover_client_asset_files,
    read_client_asset_signatures,
)
from pyrme.rendering.sprite_catalog_adapter import DatSpriteRecord, SprFrameRecord


def test_discover_client_asset_files_uses_configured_names_before_fallback(
    tmp_path,
) -> None:
    (tmp_path / "custom.dat").touch()
    (tmp_path / "custom.spr").touch()
    (tmp_path / "Tibia.dat").touch()
    (tmp_path / "Tibia.spr").touch()

    files = discover_client_asset_files(
        tmp_path,
        metadata_file_name="../custom.dat",
        sprites_file_name="nested/custom.spr",
    )

    assert files.is_complete
    assert files.metadata_file_name == "custom.dat"
    assert files.sprites_file_name == "custom.spr"
    assert files.metadata_path == tmp_path / "custom.dat"
    assert files.sprites_path == tmp_path / "custom.spr"
    assert files.warnings == ()


def test_discover_client_asset_files_falls_back_to_tibia_names(tmp_path) -> None:
    (tmp_path / "Tibia.dat").touch()
    (tmp_path / "Tibia.spr").touch()

    files = discover_client_asset_files(
        tmp_path,
        metadata_file_name="missing.dat",
        sprites_file_name="missing.spr",
    )

    assert files.is_complete
    assert files.metadata_file_name == "Tibia.dat"
    assert files.sprites_file_name == "Tibia.spr"
    assert files.metadata_path == tmp_path / "Tibia.dat"
    assert files.sprites_path == tmp_path / "Tibia.spr"
    assert files.warnings == ()


def test_discover_client_asset_files_reports_missing_assets(tmp_path) -> None:
    files = discover_client_asset_files(tmp_path)

    assert not files.is_complete
    assert files.metadata_path is None
    assert files.sprites_path is None
    assert files.warnings == (
        "Client asset detection failed: DAT file was not found in the selected client path.",
        "Client asset detection failed: SPR file was not found in the selected client path.",
    )


def test_discover_client_asset_files_reports_partial_missing_dat(tmp_path) -> None:
    (tmp_path / "Tibia.spr").touch()
    files = discover_client_asset_files(tmp_path)

    assert not files.is_complete
    assert files.metadata_path is None
    assert files.sprites_path == tmp_path / "Tibia.spr"
    assert files.warnings == (
        "Client asset detection failed: DAT file was not found in the selected client path.",
    )


def test_discover_client_asset_files_reports_partial_missing_spr(tmp_path) -> None:
    (tmp_path / "Tibia.dat").touch()
    files = discover_client_asset_files(tmp_path)

    assert not files.is_complete
    assert files.metadata_path == tmp_path / "Tibia.dat"
    assert files.sprites_path is None
    assert files.warnings == (
        "Client asset detection failed: SPR file was not found in the selected client path.",
    )


def test_discover_client_asset_files_reports_missing_root(tmp_path) -> None:
    missing_root = tmp_path / "missing-client"

    files = discover_client_asset_files(missing_root)

    assert not files.is_complete
    assert files.client_root == missing_root
    assert files.metadata_path is None
    assert files.sprites_path is None
    assert files.warnings == (
        "Client asset detection skipped: selected client path does not exist.",
    )


def test_discover_client_asset_files_sanitizes_windows_paths(tmp_path) -> None:
    (tmp_path / "Tibia.dat").touch()
    (tmp_path / "Tibia.spr").touch()

    files = discover_client_asset_files(
        tmp_path,
        metadata_file_name="C:\\Program Files\\Tibia\\Tibia.dat",
        sprites_file_name="D:/Assets/Tibia.spr",
    )

    assert files.is_complete
    assert files.metadata_file_name == "Tibia.dat"
    assert files.sprites_file_name == "Tibia.spr"


def test_discover_client_asset_files_handles_empty_names(tmp_path) -> None:
    (tmp_path / "Tibia.dat").touch()
    (tmp_path / "Tibia.spr").touch()

    files = discover_client_asset_files(
        tmp_path,
        metadata_file_name="",
        sprites_file_name="",
    )

    assert files.is_complete
    assert files.metadata_file_name == "Tibia.dat"
    assert files.sprites_file_name == "Tibia.spr"


def test_client_sprite_asset_bundle_pairs_discovery_with_existing_bundle(
    tmp_path,
) -> None:
    (tmp_path / "Tibia.dat").touch()
    (tmp_path / "Tibia.spr").touch()
    files = discover_client_asset_files(tmp_path)
    bundle = build_sprite_draw_asset_bundle(
        dat_records=(DatSpriteRecord(item_id=2148, sprite_id=9001, name="Ground"),),
        spr_frames=(SprFrameRecord(sprite_id=9001, frame_index=0, width=32, height=32),),
        atlas_regions=(
            SpriteAtlasRegion(sprite_id=9001, source_rect=(0, 0, 32, 32)),
        ),
    )

    source = ClientSpriteAssetBundle(files=files, bundle=bundle)
    inputs = source.sprite_draw_inputs()

    assert source.files.is_complete
    assert inputs.catalog.resolve(2148) is not None
    assert inputs.atlas.resolve(9001) is not None


def test_read_client_asset_signatures_reads_little_endian_values(tmp_path) -> None:
    (tmp_path / "Tibia.dat").write_bytes(bytes.fromhex("12345678aabbccdd"))
    (tmp_path / "Tibia.spr").write_bytes(bytes.fromhex("90abcdef00112233"))
    files = discover_client_asset_files(tmp_path)

    signatures = read_client_asset_signatures(files)

    assert signatures.dat_signature == 0x78563412
    assert signatures.spr_signature == 0xEFCDAB90
    assert signatures.warnings == ()


def test_read_client_asset_signatures_reports_short_files(tmp_path) -> None:
    (tmp_path / "Tibia.dat").write_bytes(b"\x12\x34")
    (tmp_path / "Tibia.spr").write_bytes(b"\x90\xab\xcd")
    files = discover_client_asset_files(tmp_path)

    signatures = read_client_asset_signatures(files)

    assert signatures.dat_signature is None
    assert signatures.spr_signature is None
    assert signatures.warnings == (
        f"DAT signature detection failed: could not read header from {tmp_path / 'Tibia.dat'}",
        f"SPR signature detection failed: could not read header from {tmp_path / 'Tibia.spr'}",
    )


def test_read_client_asset_signatures_keeps_discovery_warnings(tmp_path) -> None:
    files = discover_client_asset_files(tmp_path)

    signatures = read_client_asset_signatures(files)

    assert signatures.dat_signature is None
    assert signatures.spr_signature is None
    assert signatures.warnings == files.warnings


def test_read_client_asset_signatures_reports_deleted_files(tmp_path) -> None:
    (tmp_path / "Tibia.dat").write_bytes(bytes.fromhex("12345678"))
    (tmp_path / "Tibia.spr").write_bytes(bytes.fromhex("90abcdef"))
    files = discover_client_asset_files(tmp_path)
    (tmp_path / "Tibia.dat").unlink()
    (tmp_path / "Tibia.spr").unlink()

    signatures = read_client_asset_signatures(files)

    assert signatures.dat_signature is None
    assert signatures.spr_signature is None
    assert signatures.warnings == (
        f"DAT signature detection failed: could not open {tmp_path / 'Tibia.dat'}",
        f"SPR signature detection failed: could not open {tmp_path / 'Tibia.spr'}",
    )


def test_read_client_asset_signatures_reports_permission_errors(tmp_path) -> None:
    (tmp_path / "Tibia.dat").write_bytes(bytes.fromhex("12345678"))
    (tmp_path / "Tibia.spr").write_bytes(bytes.fromhex("90abcdef"))
    files = discover_client_asset_files(tmp_path)

    with patch("pathlib.Path.open", side_effect=PermissionError("Access denied")):
        signatures = read_client_asset_signatures(files)

    assert signatures.dat_signature is None
    assert signatures.spr_signature is None
    assert signatures.warnings == (
        f"DAT signature detection failed: could not open {tmp_path / 'Tibia.dat'}",
        f"SPR signature detection failed: could not open {tmp_path / 'Tibia.spr'}",
    )
