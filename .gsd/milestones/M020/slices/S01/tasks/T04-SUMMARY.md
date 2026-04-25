# T04 - Verification Summary

## Completed

- Added RED tests for compact SPR frame table parsing.
- Added `SprFrameMetadata` and `SprMetadataParseError`.
- Added `parse_spr_frame_metadata()` and `read_spr_frame_metadata()`.
- Parsed compact `u16` and extended `u32` sprite counts.
- Converted nonzero sprite offsets into `SprFrameRecord` rows.
- Preserved `archive_offset` in sprite frame metadata.
- Added deterministic error coverage for excessive sprite counts and truncated offset tables.
- Exported parser symbols from `pyrme.rendering`.

## Verification

- `../../.venv/bin/python3.12 -m pytest tests/python/test_spr_frame_metadata.py -q --tb=short` - 7 passed under WSL.
- `../../.venv/bin/python3.12 -m pytest tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short` - 23 passed under WSL.
- `../../.venv/bin/python3.12 -m mypy pyrme/rendering --ignore-missing-imports` - passed under WSL.
- `../../.venv/bin/python3.12 -m ruff check pyrme/rendering/spr_frame_metadata.py pyrme/rendering/sprite_catalog_adapter.py pyrme/rendering/__init__.py tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py` - passed under WSL.
- `../../.venv/bin/python3.12 -m json.tool .gsd/task-registry.json` - passed under WSL.
- `git diff --check` - passed with Windows git.
- `gh auth status` - passed.

## Notes

The parser reads only the SPR header and offset table. It does not decode compressed pixels, build atlas textures, paint sprites, auto-detect client versions, or parse `grounds.xml`.

`npm run preflight` is blocked in WSL because npm tries to spawn `C:\Windows\System32\cmd.exe`. `pyrme stack --quiet` is blocked by the current Qt platform setup (`wayland`; `offscreen` reports `QOpenGLWidget is not supported on this platform`).
