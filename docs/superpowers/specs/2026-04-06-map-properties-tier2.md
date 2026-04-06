# Map Properties Tier 2 Spec

## Goal
Retrofit the existing `Map Properties` dialog so it matches the Tier 2 local-behavior milestone while staying ready for future editor/map integration.

## Local Interface
`MapPropertiesState`
- `description: str`
- `map_version: str`
- `client_version: str`
- `width: int`
- `height: int`
- `house_file: str`
- `spawn_file: str`
- `waypoint_file: str`

## Behavior
- Dialog loads from a `MapPropertiesState`
- Dialog returns a fully populated `MapPropertiesState` on accept
- Field order follows the legacy structure:
  - description
  - map version
  - client version
  - width and height
  - house, spawn, waypoint file fields
- Styling must remain aligned to `.stitch/DESIGN.md`

## Acceptance Tests
- Dialog renders all required controls
- Dialog can be initialized from a `MapPropertiesState`
- Dialog returns edited values on accept
