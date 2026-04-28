# M013 - Client Asset Discovery

## Context

`M012/S01` introduced a fixture sprite asset bundle that groups already-materialized DAT-like records, SPR-like frame records, and atlas regions.

The next narrow step is real client asset discovery: locate configured metadata and sprite files in a client directory, with legacy-style fallback to `Tibia.dat` and `Tibia.spr`, without opening or parsing those files.

## Constraints

- No DAT or SPR binary parsing.
- No signature reads.
- No item or frame record extraction from files.
- No pixel decoding.
- No atlas texture construction or GL upload.
- No sprite painting, screenshots, lighting, or `wgpu`.

## Legacy Reference

Legacy redux resolves configured `metadataFile` and `spritesFile` inside the selected client path, sanitizes each configured name to a basename, then falls back to `Tibia.dat` and `Tibia.spr` when configured files are missing.
