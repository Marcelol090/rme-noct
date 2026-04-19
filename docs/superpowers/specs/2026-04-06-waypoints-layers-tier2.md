# Waypoints and Layers Tier 2 Spec

## Goal
Implement the Tier 2 local behavior for the `Waypoints` dock and `Layers` toolbar while keeping clear seams for future map/editor wiring.

## Local Interface
`WaypointEntry`
- `name: str`
- `x: int`
- `y: int`
- `z: int`
- `linked_spawn: str | None`

## Waypoints Behavior
- `WaypointsDock` remains multi-column
- Required columns:
  - `Name`
  - `Coordinates`
  - `Linked Spawn`
- `Coordinates` use JetBrains Mono formatting
- Dock uses a local waypoint model, not hardcoded widget rows
- Tier 2 supports:
  - add
  - rename
  - remove
  - select

## Layers Behavior
- Preserve floor selection and floor up/down actions
- Preserve `Ghost Higher Floors` and `Show Lower Floors`
- Keep backend calls as stubs, but names, defaults, and action wiring must stay testable

## Acceptance Tests
- Waypoints dock renders the three required columns
- Waypoints dock supports add, rename, remove, and selection
- Coordinate formatting preserves the expected `Z` representation
- Layers toolbar exposes required actions and stable checked defaults
