# T01 Summary - Autoborder edge contract

## Done

- Created `crates/rme_core/src/autoborder.rs`.
- Exported `pub mod autoborder`.
- Added `BorderType`, `BorderTarget`, `AutoBorderDefinition`, `GroundBorderRule`, and validation errors.
- Covered legacy edge names and duplicate id/name validation.

## Verification

- RED: `cargo test -p rme_core autoborder --quiet` failed on missing autoborder symbols.
- GREEN: `cargo test -p rme_core autoborder --quiet` passed with 4 tests.
