# S01: CANVAS-60-SPRITE-RESOLVER-CONTRACT

**Goal:** Add a tested resolver contract that maps item ids to sprite-resource lookup results using the existing DAT/SPR foundation.

**Demo:** A Python-facing resolver can return a known item's primary sprite result, report missing item ids, report missing sprite payloads, and reuse cached repeated lookups without changing the renderer host draw path.

## Must-Haves

- Define immutable Python-facing result types for sprite lookup status.
- Resolve item id to at least one sprite id using existing item metadata.
- Resolve sprite id to pixel payload when SPR data is available.
- Cache repeated item lookups behind an explicit resolver object.
- Represent missing item and missing sprite as explicit statuses.
- Keep renderer host diagnostics unchanged in this slice.

## Non Goals

- No OpenGL or wgpu sprite draw pass.
- No atlas packing.
- No animation, lighting, transparency policy, or screenshot work.
- No UI redesign.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py -q --tb=short`
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_rust_io.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short`
- `npm run preflight --silent`

## Tasks

- [x] **T01: Lock resolver result contract** `est:10m`
  - Why: renderer code needs one stable status shape before frame integration.
  - Files: `pyrme/rendering/sprite_resolver.py`, `tests/python/test_sprite_resolver.py`
  - Do: add immutable result types for resolved, missing-item, and missing-sprite outcomes.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py -q --tb=short`
  - Done when: tests prove each public status and payload field.

- [x] **T02: Add item metadata lookup seam** `est:15m`
  - Why: DAT item metadata should be consumed through a narrow Python seam instead of renderer code knowing parser details.
  - Files: `pyrme/rendering/sprite_resolver.py`, `tests/python/test_sprite_resolver.py`
  - Do: resolve a known item id to its primary sprite id from a supplied catalog object or fixture.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py -q --tb=short`
  - Done when: known item ids return sprite ids and unknown item ids return missing-item status.

- [x] **T03: Add sprite payload lookup seam** `est:15m`
  - Why: SPR access should return bytes/status without coupling renderer planning to the Rust parser API.
  - Files: `pyrme/rendering/sprite_resolver.py`, `tests/python/test_sprite_resolver.py`
  - Do: resolve a sprite id to pixel payload when available and missing-sprite status when unavailable.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py tests/python/test_rust_io.py -q --tb=short`
  - Done when: success and failure paths are covered.

- [x] **T04: Cache repeated item lookups** `est:10m`
  - Why: visible frames may ask for the same item id many times.
  - Files: `pyrme/rendering/sprite_resolver.py`, `tests/python/test_sprite_resolver.py`
  - Do: cache item-id lookup results and clear cache only when resolver data sources are replaced.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py -q --tb=short`
  - Done when: repeated lookup returns the cached result object and does not repeat source calls.

- [x] **T05: Regression batch and closeout notes** `est:10m`
  - Why: this slice must not regress existing frame planning or renderer diagnostics.
  - Files: `.gsd/milestones/M005-sprite-resolver/slices/S01/S01-SUMMARY.md`, `.gsd/STATE.md`
  - Do: run verification, record summary, then mark S01 complete only after score/review gates pass.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_rust_io.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short`
  - Done when: GSD summary records real test output and remaining renderer draw work stays explicit.

## Closeout

- R046 moves from active to validated only when S01 tests pass and the resolver API is documented by tests.
- S02 remains the next slice for frame-plan resource integration.
