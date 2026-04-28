# S01 Context - CANVAS-60-SPRITE-RESOLVER-CONTRACT

## Purpose

Build the minimal resolver contract for item-id to sprite-resource lookup before integrating it with frame plans.

## Existing Inputs

- `TileState.ground_item_id` and `TileState.item_ids` are already present in `pyrme/editor/model.py`.
- DAT and SPR parser surfaces already exist in `crates/rme_core/src/io/dat.rs` and `crates/rme_core/src/io/spr.rs`.
- Python tests already prove basic Rust IO behavior in `tests/python/test_rust_io.py`.

## Honest Boundary

This slice may expose sprite ids and pixel payload/status, but it must not introduce atlas packing or visual sprite drawing. Missing item and sprite data must be represented as explicit statuses, not fake empty art.
