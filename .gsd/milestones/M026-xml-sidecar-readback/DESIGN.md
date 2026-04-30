# M026 XML Sidecar Readback Design

## Goal
Load legacy RME sidecar XML files for waypoints, spawns, and houses when an OTBM map is loaded.

## Source Of Truth
- Legacy behavior: `remeres-map-editor-redux/source/io/map_xml_io.cpp`.
- Current write contract: `crates/rme_core/src/io/xml.rs` from M018.
- Current OTBM attributes: `spawnfile` and `housefile` from `crates/rme_core/src/io/otbm.rs`.
- Library docs: Context7 `quick-xml` Reader/event/attribute API.

## Decision
Use Rust-first readback inside `rme_core`.

`EditorShellState.load_otbm(path)` will:
1. parse the binary OTBM with existing `io::otbm::load_otbm`,
2. resolve sidecar XML paths,
3. load present sidecars into `MapModel`,
4. mark the loaded map clean,
5. keep missing sidecar files as non-fatal.

## Parser
Add `quick-xml` to `crates/rme_core`.

The parser uses:
- `Reader::from_str`
- `reader.config_mut().trim_text(true)`
- `read_event_into(&mut buf)`
- `Event::Start` / `Event::Empty`
- attribute decoding from event attributes

Malformed XML returns a load error. Malformed individual nodes are skipped, matching legacy forgiving behavior.

## Path Resolution
For `spawn` and `house`:
- prefer OTBM `spawnfile` / `housefile` when present,
- if relative, resolve beside the OTBM path,
- if absolute, use as-is,
- fallback to `<stem>-spawn.xml` and `<stem>-house.xml`.

For `waypoint`:
- use `waypointfile` if present in `MapModel`,
- otherwise fallback to `<stem>-waypoint.xml`.

## Data Rules
Waypoints:
- root: `waypoints`
- node: `waypoint`
- required: non-empty `name`, `x`, `y`, `z`
- skip node when `name` empty or `x == 0` or `y == 0`

Spawns:
- root: `spawns`
- node: `spawn`
- required: `centerx`, `centery`, `centerz`, `radius`
- skip spawn when `centerx == 0`, `centery == 0`, or `radius < 1`
- child nodes: `monster` and `npc`
- skip creature when `name` empty, `x` missing, or `y` missing

Houses:
- root: `houses`
- node: `house`
- required: `houseid`, `townid`
- skip house when `townid` missing
- Rust divergence: legacy updates an existing house registry. Current Rust model has no registry, so load creates house records directly.

## External Fixture Scope
Use read-only fixtures from:
- Windows: `C:\Users\Marcelo Henrique\Desktop\PROJETOS TIBIA\PROJETOS TIBIA`
- WSL: `/mnt/c/Users/Marcelo Henrique/Desktop/PROJETOS TIBIA/PROJETOS TIBIA`

Observed fixture inventory:
- 268 `.otbm`
- 19 Canary-like paths
- 75 TFS/OTServBR-like paths
- 154 OTBM files with matching sidecar XML
- 154 house XML, 93 spawn XML, 2 waypoint XML

Automated fixture test is env-gated with `RME_NOCT_EXTERNAL_TIBIA_FIXTURES`. It must not copy or mutate fixture data.

## Non Goals
- No UI changes.
- No server startup.
- No client asset decoding.
- No external fixture writes.
- No full house registry port.

## Verification
- `npm run preflight --silent`
- `cargo test -p rme_core io::xml`
- `cargo test -p rme_core editor`
- `/tmp/rme-noct-m026-py312/bin/python -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short`
- Optional external fixture smoke:
  `RME_NOCT_EXTERNAL_TIBIA_FIXTURES='/mnt/c/Users/Marcelo Henrique/Desktop/PROJETOS TIBIA/PROJETOS TIBIA' cargo test -p rme_core external_canary_tfs_sidecar_xml_parse_when_configured -- --nocapture`
