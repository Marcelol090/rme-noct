# S02: CANVAS-61-FRAME-SPRITE-RESOURCES

**Goal:** Let frame-plan tile commands request sprite resources for ground and stack items through the S01 resolver.

**Demo:** A pure builder consumes `RenderFramePlan` plus `SpriteResourceResolver` and returns ordered sprite resource records for visible ground and stack items, while renderer host output remains diagnostic-only.

## Must-Haves

- Keep resource collection pure and independent of Qt widgets.
- Preserve frame-plan tile order.
- Resolve ground item before stack item ids for each tile.
- Preserve missing-item and missing-sprite results.
- Keep renderer host drawing unchanged.

## Non Goals

- No OpenGL or wgpu sprite drawing.
- No atlas packing.
- No sprite diagnostics overlay; that belongs to S03.
- No item catalog loading UI.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short`
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short`
- `npm run preflight --silent`

## Tasks

- [x] **T01: Define frame sprite resource records** `est:10m`
  - Why: frame integration needs an immutable data shape separate from renderer drawing.
  - Files: `pyrme/rendering/frame_sprite_resources.py`, `tests/python/test_frame_sprite_resources.py`
  - Do: add a record containing tile position, item id, stack layer, and `SpriteResourceResult`.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short`
  - Done when: tests prove the public fields and immutability.

- [x] **T02: Resolve ground sprite resources from frame plan** `est:15m`
  - Why: ground items are the minimum useful frame-to-sprite seam.
  - Files: `pyrme/rendering/frame_sprite_resources.py`, `tests/python/test_frame_sprite_resources.py`
  - Do: build resource records for non-null `ground_item_id` values using `SpriteResourceResolver`.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short`
  - Done when: visible ground tiles produce ordered resource records.

- [x] **T03: Resolve stack item sprite resources in order** `est:15m`
  - Why: item stacks must be represented before any draw pass can be correct.
  - Files: `pyrme/rendering/frame_sprite_resources.py`, `tests/python/test_frame_sprite_resources.py`
  - Do: append stack item resources after the ground item for each tile, preserving `item_ids` order.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py -q --tb=short`
  - Done when: mixed ground/stack commands produce deterministic resource order.

- [x] **T04: Preserve missing resource outcomes** `est:10m`
  - Why: missing items or sprites must remain visible to later diagnostics.
  - Files: `pyrme/rendering/frame_sprite_resources.py`, `tests/python/test_frame_sprite_resources.py`
  - Do: keep `missing_item` and `missing_sprite` results in output instead of filtering them.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_frame_sprite_resources.py tests/python/test_sprite_resolver.py -q --tb=short`
  - Done when: failure-state records stay in the frame resource list.

- [x] **T05: Regression batch and closeout notes** `est:10m`
  - Why: frame-resource integration must not change current renderer host behavior.
  - Files: `.gsd/milestones/M005-sprite-resolver/slices/S02/S02-SUMMARY.md`, `.gsd/STATE.md`
  - Do: run verification, summarize results, and mark S02 complete only after review and score gates pass.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resolver.py tests/python/test_render_frame_plan.py tests/python/test_renderer_frame_plan_integration.py -q --tb=short`
  - Done when: S02 summary records real test output and S03 remains the next diagnostics slice.

## Closeout

- S02 completes when frame-plan commands can be converted into ordered sprite-resource records.
- S03 remains responsible for renderer diagnostics text/counts.
