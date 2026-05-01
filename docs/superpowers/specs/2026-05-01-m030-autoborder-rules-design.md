# Autoborder Rules Design

## Goal
Expose a pure autoborder rule engine in `rme_core` that can classify an 8-neighbour tile neighborhood and resolve legacy ground border item placements deterministically, without Qt, preview widgets, or direct tile mutation.

## Sources of Truth
- Legacy ground border model: `remeres-map-editor-redux/source/brushes/ground/auto_border.h`
- Legacy border resolution: `remeres-map-editor-redux/source/brushes/ground/ground_border_calculator.cpp`
- Legacy ground brush metadata: `remeres-map-editor-redux/source/brushes/ground/ground_brush.h`
- Legacy ground brush loading rules: `remeres-map-editor-redux/source/brushes/ground/ground_brush_loader.cpp`
- Legacy brush enums and border names: `remeres-map-editor-redux/source/brushes/brush_enums.h`
- Legacy border preview entrypoint: `remeres-map-editor-redux/source/ui/gui_autoborder_ext.cpp`
- Legacy overlay behavior: `remeres-map-editor-redux/source/rendering/drawers/overlays/brush_overlay_drawer.cpp`

## Scope
- Add pure Rust data types for autoborder rules, border edge names, and border item tables.
- Add a deterministic resolver for legacy-style ground border placement based on the 8 surrounding tiles.
- Preserve legacy concepts such as `optional` borders, `group` matching, `ground_equivalent` validation, and the `to=all|none` target filter.
- Keep preview rendering, menu toggles, and actual map mutation out of this gate.

## Non-Goals
- No Qt widgets.
- No `Gui::UpdateAutoborderPreview` integration.
- No `TileOperations::borderize` or direct tile mutation.
- No full XML loader for the legacy brush format.
- No wall brush rewrite; wall parity stays separate.

## Architecture
### Module Layout
- Add a new Rust module, `crates/rme_core/src/autoborder.rs`, for the rule engine.
- Keep `crates/rme_core/src/brushes.rs` as the brush catalog entrypoint, but move autoborder-specific types into the new module.
- Re-export the new border-rule types from `lib.rs` only if the implementation needs them at the Python boundary later.

### Core Types
- `BorderType`: legacy alignment names for ground borders, using the same semantic buckets as the C++ code.
- `AutoBorderDefinition`: immutable rule table containing the border id, group, ground flag, and the 13 tile ids used by legacy edge mapping.
- `GroundBorderRule`: a ground brush border rule with `outer`/`inner` target flags, `to` filter, and optional `AutoBorderDefinition`.
- `AutoborderNeighborhood`: the center tile plus the 8 neighbours needed to classify a border pattern.
- `AutoborderPlacement`: the resolved output for one tile, including the item id, alignment mask, and rule source.
- `AutoborderPlan`: ordered placement output that downstream code can later consume.

### Resolution Flow
1. Normalize the neighborhood into the same 8-neighbour mask used by the legacy calculator.
2. Match the current ground brush against the neighbour brushes and target filters.
3. Resolve `optional` and outer/inner border choices deterministically.
4. Sort the resulting placements by the legacy z-order rules so the same input always produces the same output.
5. Return an empty plan when no rule matches instead of raising on missing neighbours.

### Validation Flow
- Validate edge names at load time with the legacy `n`, `w`, `s`, `e`, `cnw`, `cne`, `csw`, `cse`, `dnw`, `dne`, `dsw`, and `dse` mappings.
- Reject duplicate border ids and duplicate brush names in the same way the brush catalog already rejects duplicate brush entries.
- Reject malformed border tables early with explicit errors rather than silently skipping them.
- Keep the rule engine pure so it can be tested without the map editor shell or Qt.

## Data Flow
Brush catalog data feeds the autoborder rule model. The resolver reads a center brush plus the eight neighbouring tiles, computes the matching legacy alignment, and emits a stable placement plan. Later slices can consume that plan inside `MapModel` or preview code, but this gate stops at the pure plan output.

## Error Handling
- Unknown edge names return a validation error, not a fallback alignment.
- Duplicate border ids, duplicate rule names, or conflicting brush references fail validation.
- Missing neighbours, empty rule sets, or an absent match return a `Noop` plan.
- The resolver should never panic on incomplete map data.

## Testing
- Unit test legacy edge name mapping against the C++ `AutoBorder::edgeNameToID` contract.
- Unit test duplicate-id and duplicate-name validation for autoborder rule tables.
- Unit test deterministic placement resolution for:
  - matching neighbour patterns
  - missing rules
  - optional border precedence
  - stable sort order for repeated inputs
- Unit test that the resolver returns an empty plan for an empty or disconnected neighbourhood.
- Keep tests in Rust only for this gate; UI and preview tests are out of scope until the rule engine exists.

## First Slice Contract
`M030/S01` should deliver the pure autoborder rule core:
- legacy edge mapping
- autoborder table validation
- deterministic neighbourhood resolution
- stable placement plan output
- Rust unit tests for the above

## Definition of Done
This gate is complete only if:
- the autoborder rule model is isolated from Qt and preview code
- the resolver is deterministic for the same neighbourhood input
- the legacy edge naming contract is covered by tests
- error cases are explicit and testable
- the next slice can consume the placement plan without reinterpreting legacy rules
