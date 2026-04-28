# M014 - Client Asset Signatures Summary

## Result

`M014/S01` adds signature reads for discovered client DAT/SPR files.

`ClientAssetSignatures` records optional DAT and SPR signatures plus warnings. `read_client_asset_signatures()` preserves discovery warnings for incomplete discovery, opens only discovered files, reads the first 4 bytes as little-endian unsigned values, and reports legacy-style warnings when a file cannot be opened or its header cannot be read.

## Verification

- `tests/python/test_client_asset_discovery.py`
- Adjacent canvas/render/sprite planning regression paths
- Ruff on touched rendering and test files
- `python3 -m json.tool .gsd/task-registry.json`
- `git diff --check`

## Remaining Gaps

- DAT item record parsing.
- SPR frame table parsing.
- Pixel decoding.
- Atlas texture construction and GL upload.
- Sprite painting, screenshots, lighting, and `wgpu`.
