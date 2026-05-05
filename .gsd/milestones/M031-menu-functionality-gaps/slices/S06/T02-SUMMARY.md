# T02 Summary - Cleanup Gap Evidence

- Cleanup invalid tiles now reports: `TileState has no invalid item or unresolved item flags`.
- Cleanup invalid zones now reports: `TileState has no invalid zone or opaque OTBM fragment fields`.

Reason:
- Python `TileState` currently stores position, ground item ID, and stack item IDs only.
