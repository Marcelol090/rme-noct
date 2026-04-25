# T04 - Verification Summary

## Completed

- Added RED tests for compact DAT item metadata parsing.
- Added `DatItemMetadata` and `DatMetadataParseError`.
- Added `parse_dat_item_metadata()` and `read_dat_item_metadata()`.
- Parsed item client ids into `DatSpriteRecord` rows.
- Added compact and extended sprite id coverage.
- Added deterministic error coverage for invalid counts, unknown flags, zero dimensions, excessive sprite counts, and truncated data.
- Added legacy DAT flag remap coverage for `10.10+` and `7.4` light flags.
- Exported parser symbols from `pyrme.rendering`.

## Verification

- `../../.venv/bin/python3.12 -m pytest tests/python/test_dat_item_metadata.py -q --tb=short` - 11 passed.
- `../../.venv/bin/python3.12 -m pytest tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short` - 16 passed.
- `../../.venv/bin/python3.12 -m ruff check pyrme/rendering/dat_item_metadata.py pyrme/rendering/__init__.py tests/python/test_dat_item_metadata.py` - passed.
- `gh auth status` - passed.
- `timeout 45s ../../.venv/bin/python3.12 -m pyrme stack --quiet` - environment-blocked by Qt wayland platform timeout during closeout rerun.

## Notes

The parser reads metadata only. It does not decode SPR pixels, build atlas textures, paint sprites, auto-detect client versions, or parse `grounds.xml`.
