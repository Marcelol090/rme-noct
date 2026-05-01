# T02 Summary - Autoborder resolver

## Done

- Added `AutoborderNeighbor`, `AutoborderNeighborhood`, `AutoborderPlacement`, and `AutoborderPlan`.
- Added deterministic mask translation through `legacy_border_types_from_mask`.
- Added `resolve_autoborder_plan` with optional border emitted before regular border.

## Verification

- RED: `cargo test -p rme_core autoborder --quiet` failed on missing resolver symbols.
- GREEN: `cargo test -p rme_core autoborder --quiet` passed with 8 tests and no warnings.
