# T04 - Verification Summary

## Completed

- Added RED tests for legacy compressed SPR payload reads.
- Added `SprCompressedPayload` and `SprCompressedPayloadError`.
- Added `parse_spr_compressed_payload()` and `read_spr_compressed_payload()`.
- Matched legacy `archive_offset + 3` seek behavior before reading compressed size.
- Read little-endian `u16` compressed payload sizes and exact raw payload bytes.
- Preserved explicit empty outcomes for sprite id `0` and offset `0`.
- Added deterministic error coverage for negative offsets, offsets outside data, truncated size reads, and truncated payload bytes.
- Exported payload symbols from `pyrme.rendering`.

## Verification

- `../../.venv/bin/python3.12 -m pytest tests/python/test_spr_compressed_payload.py -q --tb=short` - 9 passed under WSL.
- `../../.venv/bin/python3.12 -m pytest tests/python/test_spr_compressed_payload.py tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py -q --tb=short` - 21 passed under WSL.
- `../../.venv/bin/python3.12 -m mypy pyrme/rendering --ignore-missing-imports` - passed under WSL.
- `../../.venv/bin/python3.12 -m ruff check pyrme/rendering/spr_compressed_payload.py pyrme/rendering/__init__.py tests/python/test_spr_compressed_payload.py` - passed under WSL.
- `../../.venv/bin/python3.12 -m json.tool .gsd/task-registry.json` - passed under WSL.
- `git diff --check` - passed with Windows git.
- `gh auth status` - passed.

## Notes

The reader returns only raw compressed payload bytes. It does not decode RLE pixels, interpret alpha, build atlas textures, paint sprites, auto-detect client versions, or parse `grounds.xml`.

`npm run preflight` is blocked in WSL because npm tries to spawn `C:\Windows\System32\cmd.exe`. `pyrme stack --quiet` is blocked by the current Qt platform setup (`wayland` plugin load failure).
