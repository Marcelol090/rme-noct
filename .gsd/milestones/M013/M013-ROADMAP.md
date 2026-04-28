# M013 - Client Asset Discovery Roadmap

## Goal

Add pure client asset file discovery that can be paired with the existing fixture sprite asset bundle provider.

## Slices

| Slice | Title | Status |
|---|---|---|
| S01 | CANVAS-140-CLIENT-ASSET-DISCOVERY | Complete |

## Future Work

- Read DAT/SPR signatures after path discovery is stable.
- Parse DAT-like item records and SPR-like frame metadata into bundle records.
- Add atlas placement and texture ownership after record parsing is verified.
- Add renderer-host sprite painting only after asset lifecycle and command data stay verified.
