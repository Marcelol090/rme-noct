# M008 — Sprite Draw Command Plan Roadmap

| Slice | Status | Goal |
|---|---|---|
| S01 — CANVAS-90-SPRITE-DRAW-COMMAND-PLAN | Complete | Convert resolved sprite frames and atlas regions into deterministic draw command data without painting. |

## Stop Condition

Stop after tests prove draw command ordering, source/destination rectangles, offsets, and missing atlas reporting. Do not add GL uploads, real image drawing, screenshots, lighting, or `wgpu` work in this milestone.
