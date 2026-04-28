# M020 - SPR frame table metadata summary

## Completed

- Added a pure Python SPR frame table parser.
- Parsed SPR signature and compact or extended sprite counts.
- Read one `u32` archive offset per sprite id.
- Skipped zero-offset sprites as missing/empty archive entries.
- Emitted `SprFrameRecord` rows with fixed 32x32 frame size and archive offsets.
- Preserved `archive_offset` in catalog frame metadata for later pixel decoding.
- Exported parser symbols from `pyrme.rendering`.

## Verification

- `../../.venv/bin/python3.12 -m pytest tests/python/test_spr_frame_metadata.py -q --tb=short` - 7 passed under WSL.
- `../../.venv/bin/python3.12 -m pytest tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short` - 23 passed under WSL.
- `../../.venv/bin/python3.12 -m mypy pyrme/rendering --ignore-missing-imports` - passed under WSL.
- `../../.venv/bin/python3.12 -m ruff check pyrme/rendering/spr_frame_metadata.py pyrme/rendering/sprite_catalog_adapter.py pyrme/rendering/__init__.py tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py` - passed under WSL.
- `../../.venv/bin/python3.12 -m json.tool .gsd/task-registry.json` - passed under WSL.
- `git diff --check` - passed with Windows git.
- `gh auth status` - passed.

## Environment notes

- `npm run preflight` is environment-blocked in WSL because npm tries to spawn `C:\Windows\System32\cmd.exe`.
- `pyrme stack --quiet` is environment-blocked in WSL by Qt platform setup (`wayland`; `offscreen` reports `QOpenGLWidget is not supported on this platform`).

## Deferred

- Automatic client-version detection.
- Compressed SPR payload reads.
- Pixel decoding.
- Atlas texture construction.
- Sprite painting.
