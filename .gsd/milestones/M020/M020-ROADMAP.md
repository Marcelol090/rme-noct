# M020 - Roadmap

## S01 - SPR frame table parser

Parse SPR signature, sprite count, and archive offset table into `SprFrameRecord` rows.

Stop when tested parser output feeds existing sprite catalog metadata without decoding pixels or touching renderer paint paths.
