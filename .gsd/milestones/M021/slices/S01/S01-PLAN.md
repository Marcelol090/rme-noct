# S01 - SPR compressed payload reader

## Stop condition

Stop when a tested Python payload reader consumes SPR bytes/path plus `SprFrameRecord.archive_offset`, seeks to `archive_offset + 3`, reads a little-endian `u16` compressed size and exact raw payload bytes, and keeps decompression, alpha interpretation, atlas textures, and sprite painting out of scope.

## Tasks

- [x] T01 - Add RED payload reader tests for legacy `offset + 3` reads.
- [x] T02 - Implement compressed payload records, parser, path reader, and public exports.
- [x] T03 - Add empty outcome and deterministic truncation/error coverage.
- [x] T04 - Verify slice, run gap review, write summary, update GSD state.

## Tests

Run slice-relevant tests before marking done:

```bash
../../.venv/bin/python3.12 -m pytest tests/python/test_spr_compressed_payload.py -q --tb=short
```

Run broader rendering-adjacent tests because payload reads depend on SPR frame metadata records:

```bash
../../.venv/bin/python3.12 -m pytest tests/python/test_spr_compressed_payload.py tests/python/test_spr_frame_metadata.py tests/python/test_sprite_catalog_adapter.py -q --tb=short
```

## Non-goals

- No RLE decompression.
- No alpha interpretation.
- No atlas textures.
- No sprite painting.
- No automatic client-version detection.
