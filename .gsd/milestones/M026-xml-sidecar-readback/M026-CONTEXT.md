# M026: XML Sidecar Readback

## Objective
Complete the persistence loop for M018 sidecar XML by reading waypoint, spawn, and house XML when an OTBM map is loaded.

## Current State
- `save_otbm` writes `.otbm`, `<stem>-waypoint.xml`, `<stem>-spawn.xml`, and `<stem>-house.xml`.
- `load_otbm` reads only binary OTBM data.
- `MapModel` already stores waypoints, spawns, creatures, and houses.
- `otbm.rs` already reads `spawnfile` and `housefile` map attributes.

## Target State
- `io::xml` can parse sidecar XML strings and files.
- Missing sidecar files do not fail OTBM loading.
- Malformed XML fails clearly.
- Invalid individual sidecar nodes are skipped.
- `EditorShellState.load_otbm` returns a clean map with loaded sidecar domains.
- Canary/TFS fixture XML can be parsed when `RME_NOCT_EXTERNAL_TIBIA_FIXTURES` is set.

## Approved Approach
Rust-first parser with `quick-xml`, integrated in `EditorShellState.load_otbm`.

## Stop Condition
Native save/load roundtrip proves sidecar domains survive reload, targeted Rust/Python tests pass, and env-gated fixture smoke parses at least one Canary/TFS sidecar set when fixtures are available.
