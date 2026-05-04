# T04 Summary - MainWindow Selection Wiring

- Wired Replace Items on Selection through `EditTransformService.choose_replace_items`.
- Wired Find Item/Remove Item on Selection through `choose_remove_items_by_id`.
- Wired Find Everything and Find Unique to `selection_item_counts`.
- Kept Find Action/Container/Writeable explicit deferred gaps.

Verification:
- `QT_QPA_PLATFORM=offscreen rtk python3 -m pytest tests/python/test_legacy_selection_menu.py -q --tb=short` -> 9 passed.
