# M009 — Sprite Draw Diagnostics Roadmap

| Slice | Status | Goal |
|---|---|---|
| S01 — CANVAS-100-SPRITE-DRAW-DIAGNOSTICS | Complete | Let canvas hosts accept sprite draw plans and report command/unresolved-sprite diagnostics without painting pixels. |

## Stop Condition

Stop after tests prove default diagnostics, explicit draw-plan updates, and protocol detection on placeholder and renderer-host canvas widgets. Do not add live sprite frame generation, atlas construction, GL upload, image drawing, screenshots, lighting, or `wgpu` work in this milestone.
