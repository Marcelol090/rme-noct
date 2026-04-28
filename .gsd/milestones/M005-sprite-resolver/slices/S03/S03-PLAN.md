# S03: CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS

**Goal:** Surface sprite resolution counts and missing-resource diagnostics in the renderer host without drawing sprites.

**Demo:** After drawing a visible tile, the canvas diagnostic text reports sprite resource totals and missing outcomes while tile primitives still render as diagnostics only.

## Must-Haves

- Keep diagnostics pure and testable before UI wiring.
- Count total, resolved, missing-item, and missing-sprite resources.
- Preserve the diagnostic-only renderer boundary.
- Avoid DAT/SPR loading UI or atlas/draw-pass claims.
- Keep existing frame and primitive diagnostics stable.

## Non Goals

- No OpenGL or wgpu sprite drawing.
- No atlas packing.
- No item catalog loading UI.
- No generated placeholder sprites.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py -q --tb=short`
- `.\.venv\Scripts\python.exe -m pytest tests/python/test_renderer_frame_plan_integration.py tests/python/test_canvas_seam_m4.py -q --tb=short`
- `npm run preflight --silent`

## Tasks

- [x] **T01: Define pure sprite resource diagnostics summary** `est:10m`
  - Why: renderer text needs a stable summary contract independent of Qt.
  - Files: `pyrme/rendering/sprite_resource_diagnostics.py`, `tests/python/test_sprite_resource_diagnostics.py`
  - Do: add immutable diagnostics record and builder from `FrameSpriteResource` records.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py -q --tb=short`
  - Done when: tests prove total/resolved/missing-item/missing-sprite counts.

- [x] **T02: Add diagnostic summary text contract** `est:10m`
  - Why: canvas host should render one stable text line without recomputing counts.
  - Files: `pyrme/rendering/sprite_resource_diagnostics.py`, `tests/python/test_sprite_resource_diagnostics.py`
  - Do: add concise `summary()` output for zero, resolved, and missing states.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py -q --tb=short`
  - Done when: summary text remains explicit and non-visual.

- [x] **T03: Wire renderer host diagnostic storage** `est:15m`
  - Why: canvas diagnostics need a place to hold sprite resource counts.
  - Files: `pyrme/ui/canvas_host.py`, `tests/python/test_renderer_frame_plan_integration.py`
  - Do: initialize and display sprite resource diagnostics in `diagnostic_text()`.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_renderer_frame_plan_integration.py -q --tb=short`
  - Done when: existing canvas diagnostics include sprite resource count text.

- [x] **T04: Collect frame sprite diagnostics during canvas sync** `est:20m`
  - Why: diagnostics must reflect actual visible frame resources, not hardcoded text.
  - Files: `pyrme/ui/canvas_host.py`, `tests/python/test_renderer_frame_plan_integration.py`
  - Do: build resource diagnostics from the current frame plan through an explicit resolver seam, defaulting honestly when no DAT/SPR source is available.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_renderer_frame_plan_integration.py tests/python/test_frame_sprite_resources.py -q --tb=short`
  - Done when: drawing a visible item updates sprite resource diagnostics without changing primitive rendering.

- [x] **T05: Regression batch and closeout notes** `est:10m`
  - Why: diagnostic text changes must not regress renderer host behavior.
  - Files: `.gsd/milestones/M005-sprite-resolver/slices/S03/S03-SUMMARY.md`, `.gsd/STATE.md`
  - Do: run verification, summarize results, and mark S03 complete only after review and score gates pass.
  - Verify: `.\.venv\Scripts\python.exe -m pytest tests/python/test_sprite_resource_diagnostics.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_canvas_seam_m4.py -q --tb=short`
  - Done when: S03 summary records real test output and renderer remains diagnostic-only.

## Closeout

- S03 completes when renderer diagnostics report sprite resource counts and missing outcomes while still drawing only diagnostic tile primitives.
