# Project

## What This Is

PyRME is converging the Python editor shell to the legacy RME menu contract, using `remeres-map-editor-redux/data/menubar.xml` as the behavioral source of truth and executing the work as explicit GSD slices.

## Core Value

Legacy parity should advance in small, verifiable slices with XML-backed tests, honest reuse of prior shell work, and durable state recorded under `.gsd/`.

## Current State

Milestone `M001-1pt4oy` remains closed on disk: all legacy parity slices `LEGACY-00-CONTRACT` through `LEGACY-140-FINAL-AUDIT` are completed and summarized, and the Python shell is verified against `remeres-map-editor-redux/data/menubar.xml` for every in-scope top-level legacy menu family. Milestone `M002-canvas-renderer` is closed: the production default canvas is a real `QOpenGLWidget` host, each editor view owns an independent viewport model, and default canvas input uses legacy-style screen/map translation over that viewport model. Milestone `M003-render` is closed with the first draw-planning seam: map tiles are converted into a stable frame plan. Milestone `M004-render-primitives` is closed with diagnostic tile primitives. Milestone `M005-sprite-resolver` is closed: item-id sprite resolution, frame resource records, and renderer diagnostic counts are tested while renderer drawing remains diagnostic-only. Milestone `M006-item-palette` is closed: the brush palette `Item` tab is now search-first, model-backed, cached, and tested while sprite rendering remains explicit follow-up work. Milestone `M007-brush-activation-backend` is closed: backend mode, brush activation, item activation, and active tool behavior are covered by focused contract tests. Milestone `M008-brush-shell-wiring` is closed: local jump dialogs, palette switching, brush mode toolbar behavior, and WSL preflight now align the UI shell with the canonical brush backend contract. Milestones `M015`, `M016`, and `M017` moved OTBM map persistence into `rme_core` for map model, read, and write paths. Milestone `M018-otbm-xml-serialization` is closed: Python `save_otbm` writes legacy waypoint, spawn, and house XML sidecars beside the binary `.otbm`.

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
| M005-sprite-resolver | Sprite resolver seam | Complete - `S01 / CANVAS-60-SPRITE-RESOLVER-CONTRACT`, `S02 / CANVAS-61-FRAME-SPRITE-RESOURCES`, and `S03 / CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS` verified and summarized |
| M006-item-palette | Item palette model/view seam | Complete - `S01 / ITEM-10-MODEL-VIEW-PALETTE` verified and summarized |
| M007-brush-activation-backend | Brush activation backend contract | Complete - `S01 / BRUSH-10-ACTIVATION-BACKEND-CONTRACT` verified and summarized |
| M008-brush-shell-wiring | Brush shell wiring | Complete - `S01 / BRUSH-20-SHELL-COMMAND-WIRING` verified and summarized |
| M015-core-map-model | Rust map model bridge | Complete - sparse map storage and metadata exposed through PyO3 |
| M016-otbm-persistence | OTBM read persistence | Complete - binary OTBM read path ported to `rme_core` |
| M017-otbm-persistence | OTBM write persistence | Complete - binary OTBM save path ported to `rme_core` |
| M018-otbm-xml-serialization | OTBM XML sidecars | Complete - `S01 / XML Writing implementation` verified and summarized |
