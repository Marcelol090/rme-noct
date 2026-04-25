# M019 - DAT item metadata summary

## Completed

- Added a pure Python DAT metadata parser.
- Parsed DAT signature and item/creature/effect/distance counts.
- Emitted `DatSpriteRecord` rows for item client ids from `100..item_count`.
- Consumed creature entries for stream alignment while excluding them from item records by default.
- Supported compact `u16` and extended `u32` sprite ids.
- Added explicit DAT format flag remapping for `7.4`, `7.55`, `7.8`, `8.6+`, and `10.10+` style flag layouts.
- Exported parser symbols from `pyrme.rendering`.

## Verification

- `../../.venv/bin/python3.12 -m pytest tests/python/test_dat_item_metadata.py -q --tb=short` - 11 passed.
- `../../.venv/bin/python3.12 -m pytest tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short` - 16 passed.
- `../../.venv/bin/python3.12 -m mypy pyrme/rendering pyrme/ui/canvas_host.py pyrme/ui/canvas_frame.py pyrme/ui/viewport.py --ignore-missing-imports` - passed.
- `../../.venv/bin/python3.12 -m ruff check pyrme/rendering/dat_item_metadata.py pyrme/rendering/sprite_draw_commands.py pyrme/rendering/__init__.py tests/python/test_dat_item_metadata.py` - passed.
- `gh auth status` - passed.
- `timeout 45s ../../.venv/bin/python3.12 -m pyrme stack --quiet` - environment-blocked by Qt wayland platform timeout during closeout rerun.

## Deferred

- Automatic DAT format detection.
- SPR frame table parsing.
- SPR pixel decoding.
- Atlas texture construction.
- Sprite painting.
- `grounds.xml` parsing.
