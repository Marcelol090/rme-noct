# S01 - Parser and catalog records

## Stop condition

Stop when a tested Python DAT metadata parser emits `DatSpriteRecord` rows from DAT bytes/path without decoding SPR pixels or touching UI/rendering.

## Tasks

- [x] T01 - Add RED parser tests for compact DAT metadata.
- [x] T02 - Implement DAT metadata parser and public exports.
- [x] T03 - Add extended sprite id and error-path coverage.
- [x] T04 - Verify slice, run gap review, write summary, update GSD state.

## Tests

Run slice-relevant tests before marking done:

```bash
python3 -m pytest tests/python/test_dat_item_metadata.py -q --tb=short
```

Run broader rendering-adjacent tests if parser exports affect package imports:

```bash
python3 -m pytest tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short
```

Verified on 2026-04-25 with the root WSL Python 3.12 venv:

```bash
../../.venv/bin/python3.12 -m pytest tests/python/test_dat_item_metadata.py -q --tb=short
../../.venv/bin/python3.12 -m pytest tests/python/test_sprite_catalog_adapter.py tests/python/test_dat_item_metadata.py -q --tb=short
../../.venv/bin/python3.12 -m ruff check pyrme/rendering/dat_item_metadata.py pyrme/rendering/__init__.py tests/python/test_dat_item_metadata.py
```

## Non-goals

- No SPR pixel decoding.
- No atlas textures.
- No sprite painting.
- No automatic client-version detection.
- No `grounds.xml` parsing.
