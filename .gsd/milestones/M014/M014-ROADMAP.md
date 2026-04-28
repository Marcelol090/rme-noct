# M014 - Client Asset Signatures Roadmap

## Goal

Read DAT/SPR signatures from discovered client files before adding item record parsing or pixel work.

## Slices

| Slice | Title | Status |
|---|---|---|
| S01 | CANVAS-150-CLIENT-ASSET-SIGNATURES | Complete |

## Future Work

- Parse DAT-like item metadata records after signature reads are stable.
- Parse SPR-like frame metadata after DAT metadata contracts are stable.
- Add atlas placement and texture ownership after record parsing is verified.
- Add renderer-host sprite painting only after asset lifecycle and command data stay verified.
