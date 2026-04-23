# GSD State

**Active Milestone:** none
**Active Slice:** none
**Active Task:** none
**Phase:** complete
**Next Action:** Connect the fixture asset bundle to real client asset discovery, still without binary parsing beyond existing records, pixel decoding, atlas textures, or sprite painting.
**Last Updated:** 2026-04-23T19:14:05-03:00
**Requirements Status:** 0 active · 27 validated · 0 deferred · 3 out of scope

## Recent Decisions

- `remeres-map-editor-redux/data/menubar.xml` is the source of truth for legacy menu order, labels, and shortcuts.
- `LEGACY-00-CONTRACT` is treated as completed foundation work: top-level menu tree, action metadata, and contract tests exist in the current shell.
- `M5-SHELL-NAVIGATION` remains reusable shell-state infrastructure, but it is not counted as full legacy parity.
- `LEGACY-90-NAVIGATE`, `LEGACY-100-WINDOW`, `LEGACY-10-FILE`, `LEGACY-20-EDIT`, `LEGACY-30-EDITOR`, `LEGACY-40-SEARCH`, `LEGACY-50-MAP`, `LEGACY-60-SELECTION`, `LEGACY-70-VIEW`, and `LEGACY-80-SHOW` are complete and verified.
- `LEGACY-70-VIEW` now persists its checkable per-view flags in tab shell snapshots instead of keeping them only in window-global state.
- `LEGACY-20-EDIT` keeps backend-heavy actions as explicit safe gaps, but `Border Automagic` now restores from persisted settings and uses the legacy-style enable/disable status text.
- `LEGACY-60-SELECTION` now preserves selection-mode defaults and persistence, gates selection-dependent actions on real local selection presence, and couples `Selection Mode` honestly to `View -> Show all Floors`.
- `LEGACY-10-FILE` now matches the covered legacy `File` menu surface, including `Import`, `Export`, `Reload`, and an empty `Recent Files` submenu, while file-system work remains explicit safe gaps.
- `LEGACY-110-EXPERIMENTAL`, `LEGACY-120-SCRIPTS`, and `LEGACY-130-ABOUT` are fully wired to the menu system.
- `LEGACY-140-FINAL-AUDIT` is complete: XML-backed parity tests and the local Python suite pass in WSL.
- Tier 3 UI Dialogs (`Town Manager`, `Preferences`, `About`, `Goto Position`, `Find Item`, `Map Properties`) are fully implemented and integrated with the Noct design system.
- `CANVAS-10-RENDERER-HOST` is complete: the production default canvas is now `RendererHostCanvasWidget`, a real `QOpenGLWidget` host with an honest diagnostic overlay and preserved shell seams.
- `PlaceholderCanvasWidget` remains available only as an explicit fallback/test injection path; it is no longer the production default surface.
- `CANVAS-20-VIEWPORT-MODEL` is complete: each editor view owns an independent `EditorViewport` with center, scroll origin, floor, zoom, previous-position history, and snapshot/restore behavior.
- `CANVAS-30-MAP-VIEW-MATH` is complete: `EditorViewport` exposes legacy-style `screen_to_map`, `map_to_screen`, and visible-rect math, and default canvas click handling uses the viewport mapping instead of applying tools at the current center.
- `CANVAS-40-RENDER-FRAME-PLAN` is complete: the renderer path now builds a stable `CanvasFrame` from `MapModel` and the active `EditorViewport`, reports visible tiles, map generation, and visible rect, and still avoids pretending sprites are drawn.
- `CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES` is complete: frame-plan tile commands now project into screen-space diagnostic rectangles and the renderer host reports primitive count without claiming sprite parity.
- Workflow health remediation is complete: `npm run preflight` now reflects the integrated Codex session, optional local agent TOML files, optional standalone Context7 CLI, and Windows `.venv` Python runtime.
- `M005/S01` starts as a planning slice for a sprite catalog seam; metadata stays `None` by default, `build_sprite_frame` must not read metadata in this milestone, and `DatDatabase` remains adapter-level only.
- `CANVAS-60-SPRITE-CATALOG-SEAM` is complete: `SpriteCatalog`, `SpriteCatalogEntry`, and `build_sprite_frame` now resolve frame-plan item ids and report deterministic unresolved ids without reading metadata or importing DAT/SPR adapter types.
- `CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER` is complete: DAT-like item sprite records now build `SpriteCatalog` entries with adapter-owned metadata while frame planning remains free of DAT adapter imports.
- `CANVAS-80-SPR-FRAME-METADATA` is complete: SPR-like frame records now attach sorted frame metadata to matching `SpriteCatalog` entries without parsing files, decoding pixels, or planning atlas placement.
- `CANVAS-90-SPRITE-DRAW-COMMAND-PLAN` is complete: resolved sprite-frame data now converts into deterministic atlas-backed draw commands with source/destination rectangles and missing draw-input reporting, without painting pixels.
- `CANVAS-100-SPRITE-DRAW-DIAGNOSTICS` is complete: the canvas host now accepts sprite draw plans and reports command counts plus unresolved sprite ids in diagnostics, without painting sprites.
- `CANVAS-110-LIVE-SPRITE-DRAW-PLAN` is complete: canvas hosts now derive sprite draw plan diagnostics from live `CanvasFrame` data using injected fixture `SpriteCatalog` and `SpriteAtlas` inputs, while explicit draw-plan injection remains an override.
- `CANVAS-120-SPRITE-ASSET-PROVIDER` is complete: canvas hosts now consume live sprite draw assets through a provider seam that supplies catalog and atlas inputs together, while direct fixture inputs and explicit draw-plan overrides remain supported.
- `CANVAS-130-SPRITE-ASSET-BUNDLE` is complete: sprite draw assets can now be grouped as a fixture bundle of DAT-like records, SPR-like frames, and atlas regions that implements the provider seam without file IO or pixel work.

## Blockers

- `GSD auto` still stalls with the installed local `qwen2.5-coder:3b` model: it completes with 0 tool calls while planning `M001-1pt4oy/S12`. Manual materialization was used for S12-S15 after local verification.
- `QOpenGLWidget` under `QT_QPA_PLATFORM=offscreen` still reports invalid contexts locally, so slice verification relies on protocol behavior and honest diagnostics rather than requiring a live GL context in CI.
