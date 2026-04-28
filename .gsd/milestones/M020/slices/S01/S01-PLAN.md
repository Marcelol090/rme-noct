# S01 - SPR frame table parser

## Stop condition

Stop when a tested Python SPR metadata parser emits `SprFrameRecord` rows from SPR bytes/path without decoding compressed pixel payloads or touching UI/rendering paint paths.

## Tasks

- [x] T01 - Add RED parser tests for compact SPR frame tables.
- [x] T02 - Implement SPR frame table parser and public exports.
- [x] T03 - Add extended count, path read, catalog integration, and error coverage.
- [x] T04 - Verify slice, run gap review, write summary, update GSD state.

## Tests

Run slice-relevant tests before marking done:

```bash
../../.venv/bin/python3.12 -m pytest tests/python/test_spr_frame_metadata.py -q --tb=short
```

Run broader rendering-adjacent tests because parser exports and `SprFrameRecord` metadata changed:

```bash
../../.venv/bin/python3.12 -m pytest tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short
```

## Non-goals

- No compressed SPR payload reads.
- No pixel decoding.
- No atlas textures.
- No sprite painting.
- No automatic client-version detection.
