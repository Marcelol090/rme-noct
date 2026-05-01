# S01 Summary - M030 Autoborder rules

## Scope

- Added the pure autoborder rule model in `rme_core`.
- Matched legacy edge names and rejected invalid ones.
- Resolved deterministic 8-neighbour placement plans.

## Verification

- `cargo test -p rme_core autoborder --quiet`
- `git diff --check`

## Notes

- Qt, preview, and map mutation remain out of scope.
- Rust/PyO3 tests in WSL require `PYO3_PYTHON=/home/marcelo/.local/bin/python3.12`.
