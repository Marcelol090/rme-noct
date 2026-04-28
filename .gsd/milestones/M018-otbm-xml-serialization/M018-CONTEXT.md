# M018: OTBM XML Serialization

## Objective
Finalize the map persistence layer by introducing XML serialization for Waypoints, Spawns, and Houses.

## Rationale
The `rme_core` currently saves the binary `.otbm` correctly (completed in M017), but leaves out sidecar XML data required by the OpenTibia server and legacy RME. Adding the XML serialization fulfills the legacy contract for full map persistence.

## Current State
- `save_otbm` creates binary output.
- `MapModel` lacks domain models for Waypoints, Spawns, and Houses.
- No `xml.rs` exists.

## Target State
- `MapModel` extended with `Waypoint`, `Spawn`, `Creature`, `House`.
- `io/xml.rs` created to format Rust strings as valid OpenTibia XMLs.
- `save_otbm` bridged to Python to write both `.otbm` and associated XMLs to disk.
