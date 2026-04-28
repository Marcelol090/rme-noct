# M014 - Client Asset Signatures

## Context

`M013/S01` introduced pure client asset path discovery. It resolves configured DAT/SPR file names under a selected client root, falls back to `Tibia.dat` and `Tibia.spr`, and keeps files unopened.

The next narrow step is legacy-style signature reading: open the discovered DAT and SPR files and read only the first 4 bytes as little-endian unsigned values.

## Constraints

- No DAT item record parsing.
- No SPR frame table parsing.
- No pixel decoding.
- No atlas texture construction or GL upload.
- No sprite painting, screenshots, lighting, or `wgpu`.
- Preserve discovery warnings when discovered files are incomplete.

## Legacy Reference

Legacy redux `source/app/client_asset_detector.cpp::readSignature()` opens each discovered file and reads a `uint32_t` header value. It reports separate warnings for open failures and short or unreadable headers.
