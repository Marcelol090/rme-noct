# Project

## What This Is

PyRME is converging the Python editor shell to the legacy RME menu contract, using `remeres-map-editor-redux/data/menubar.xml` as the behavioral source of truth and executing the work as explicit GSD slices.

## Core Value

Legacy parity should advance in small, verifiable slices with XML-backed tests, honest reuse of prior shell work, and durable state recorded under `.gsd/`.

## Current State

Milestone `M001-1pt4oy` remains closed on disk: all legacy parity slices `LEGACY-00-CONTRACT` through `LEGACY-140-FINAL-AUDIT` are completed and summarized, and the Python shell is verified against `remeres-map-editor-redux/data/menubar.xml` for every in-scope top-level legacy menu family. Milestone `M002-canvas-renderer` is closed: the production default canvas is a real `QOpenGLWidget` host, each editor view owns an independent viewport model, and default canvas input uses legacy-style screen/map translation over that viewport model. Milestone `M003-render` is closed with the first draw-planning seam: map tiles are converted into a stable frame plan. Milestone `M004-render-primitives` is closed with diagnostic tile primitives. Milestones `M005` through `M013` now close the sprite planning ladder from catalog seam through client asset path discovery, while real sprite painting remains future work.

## Architecture / Key Patterns

- `pyrme/ui/legacy_menu_contract.py` freezes the legacy-facing menu and action metadata.
- `pyrme/ui/main_window.py` renders the shell from that contract and reuses the verified shell-state seams from `M5-SHELL-NAVIGATION`.
- Narrow pytest slices and XML-backed audits prove each legacy menu delta before it is recorded in `.gsd/task-registry.json`.

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract and slice ownership map.

## Milestone Sequence

| ID | Title | Status |
|---|---|---|
| M001-1pt4oy | Legacy menu parity | Complete - all slices `S01` through `S15` verified and closed |
| M002-canvas-renderer | Renderer-backed canvas foundation | Complete - `S01 / CANVAS-10-RENDERER-HOST`, `S02 / CANVAS-20-VIEWPORT-MODEL`, and `S03 / CANVAS-30-MAP-VIEW-MATH` verified and summarized |
| M003-render | Renderer draw foundation | Complete - `S01 / CANVAS-40-RENDER-FRAME-PLAN` verified and summarized |
| M004-render-primitives | Diagnostic tile primitives | Complete - `S01 / CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES` verified and summarized |
| M005 | Sprite catalog seam | Complete - `S01 / CANVAS-60-SPRITE-CATALOG-SEAM` verified and summarized |
| M006 | Sprite catalog DAT adapter | Complete - `S01 / CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` verified and summarized |
| M007 | SPR frame metadata | Complete - `S01 / CANVAS-80-SPR-FRAME-METADATA` verified and summarized |
| M008 | Sprite draw command plan | Complete - `S01 / CANVAS-90-SPRITE-DRAW-COMMAND-PLAN` verified and summarized |
| M009 | Sprite draw diagnostics | Complete - `S01 / CANVAS-100-SPRITE-DRAW-DIAGNOSTICS` verified and summarized |
| M010 | Live sprite draw plan integration | Complete - `S01 / CANVAS-110-LIVE-SPRITE-DRAW-PLAN` verified and summarized |
| M011 | Sprite asset provider | Complete - `S01 / CANVAS-120-SPRITE-ASSET-PROVIDER` verified and summarized |
| M012 | Sprite asset bundle | Complete - `S01 / CANVAS-130-SPRITE-ASSET-BUNDLE` verified and summarized |
| M013 | Client asset discovery | Complete - `S01 / CANVAS-140-CLIENT-ASSET-DISCOVERY` verified and summarized |
