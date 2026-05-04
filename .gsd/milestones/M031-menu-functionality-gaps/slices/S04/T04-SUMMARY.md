# T04 Summary - Unsupported Transform Evidence

- Randomize Selection/Map deferred: `TileState` has no ground variant catalog.
- Remove all Corpses deferred: `TileState` has no item type flags.
- Remove all Unreachable Tiles deferred: no pathing or visibility graph exists.
- Clear Invalid Houses deferred: tiles do not store house IDs.

Verification:
- `tests/python/test_legacy_edit_menu.py` asserts each exact status message.
