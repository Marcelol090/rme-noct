# M013 - Client Asset Discovery Summary

## Result

`M013/S01` adds pure client asset file discovery.

`discover_client_asset_files()` resolves configured metadata and sprite names under a client root, sanitizes path-like names to basenames, falls back to `Tibia.dat` and `Tibia.spr`, and reports legacy-style warnings for missing roots or files.

`ClientSpriteAssetBundle` pairs discovered client files with the existing `SpriteDrawAssetBundle` provider without parsing the discovered files.

## Verification

- `tests/python/test_client_asset_discovery.py`
- Adjacent canvas/render/sprite planning regression paths
- Ruff on touched rendering and test files
- `git diff --check`

## Remaining Gaps

- DAT/SPR signature reads.
- DAT/SPR binary parsing.
- Pixel decoding.
- Atlas texture construction and GL upload.
- Sprite painting, screenshots, lighting, and `wgpu`.
