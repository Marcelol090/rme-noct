# M025 Map Statistics S01 Summary

## Completed

- Added Rust `MapStatistics` aggregation on `MapModel`.
- Exposed `collect_statistics()` through `EditorShellState` and Python bridge.
- Added `MapStatisticsDialog`.
- Wired `Map -> Statistics` to real dialog seam.
- Kept cleanup actions as explicit safe gaps.

## Verification

- `npm run preflight --silent`: passed
- `QT_QPA_PLATFORM=offscreen /tmp/rme-noct-m025-py312/bin/python -m pytest tests/python/test_map_statistics_dialog.py tests/python/test_legacy_map_menu.py -q --tb=short`: 7 passed
- `cargo test -p rme_core map_model_collects_statistics_from_tiles_and_sidecars`: 1 passed
- `/tmp/rme-noct-m025-py312/bin/python -m ruff check ...`: passed
- `rustfmt --check --edition 2021 crates/rme_core/src/editor.rs crates/rme_core/src/map.rs`: passed
- `rustfmt --check --edition 2021 --config skip_children=true crates/rme_core/src/lib.rs`: passed
- `git diff --check`: passed

## Review

- `caveman-review`: no blocking gap found in touched diff.

## Notes

- Branch is intentionally based on `gsd/M018/S01` because `origin/main` lacks the full map sidecar domains this slice consumes.
- Fallback shell returns `None`; UI shows zeros instead of fake statistics.
- `rustfmt` on `lib.rs` without `skip_children=true` still traverses baseline `io/otbm.rs` formatting drift outside this slice.
