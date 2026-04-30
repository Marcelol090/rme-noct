# T01 Summary: XML Sidecar Readback

## Done
- Added Rust XML sidecar readback for waypoints, spawns, and houses.
- Integrated sidecar readback into `EditorShellState.load_otbm`.
- Added native `sidecar_counts()` for focused verification.
- Added env-gated Canary/TFS fixture smoke using `RME_NOCT_EXTERNAL_TIBIA_FIXTURES`.
- Added malformed XML coverage for unexpected EOF and mismatched end tags.

## Verification
- `npm run preflight --silent`
- `cargo test -p rme_core io::xml` -> 9 passed
- `cargo test -p rme_core editor` -> 8 passed
- `RME_NOCT_EXTERNAL_TIBIA_FIXTURES="/mnt/c/Users/Marcelo Henrique/Desktop/PROJETOS TIBIA/PROJETOS TIBIA" cargo test -p rme_core external_canary_tfs_sidecar_xml_parse_when_configured -- --nocapture` -> 1 passed
- `/tmp/rme-noct-m026-py312/bin/python -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short` -> 4 passed
- `rustfmt --edition 2021 --check crates/rme_core/src/io/xml.rs crates/rme_core/src/editor.rs crates/rme_core/src/map.rs`
- `/tmp/rme-noct-m026-py312/bin/python -m ruff check tests/python/test_rme_core_editor_shell.py`
- `git diff --check`

## Notes
- Missing sidecar files are non-fatal.
- Malformed XML returns a load error.
- Invalid individual XML nodes are skipped.
- House load creates Rust house records directly because current Rust model has no preexisting house registry.
- Full `cargo fmt --check` still reports inherited formatting drift in `crates/rme_core/src/io/otbm.rs`; touched Rust files pass targeted rustfmt.
