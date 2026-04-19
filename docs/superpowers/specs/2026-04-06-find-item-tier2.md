# Find Item Tier 2 Spec

## Goal
Turn the existing `Find Item` dialog into a backend-agnostic local search surface with stable interfaces for future Tibia catalog integration.

## Local Interfaces
`FindItemResult`
- `server_id: int`
- `client_id: int`
- `name: str`
- `sprite_hash: str`
- `kind: str`
- `flags: set[str]`

`FindItemQuery`
- `search_text: str`
- `type_filters: set[str]`
- `property_filters: set[str]`
- `result_mode: FindItemResultMode`

`FindItemResultMode`
- `list`
- `grid`

## Behavior
- Results come from a local in-memory catalog only for Tier 2
- Search text and filters update visible results locally
- Result modes switch between `List` and `Grid`
- `Search Map` stays a UI action seam only
- Confirm/select returns the selected `FindItemResult`
- Interface shape is intentionally compatible with future Tibia catalog work and cross-instance clipboard identifiers

## Acceptance Tests
- Dialog renders search, filters, result area, and footer actions
- Dialog supports `List` and `Grid`
- Search and filters update visible/local results
- Confirm returns the selected `FindItemResult`
