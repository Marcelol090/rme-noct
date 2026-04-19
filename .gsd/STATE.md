# GSD State

**Active Milestone:** none
**Active Slice:** none
**Active Task:** none
**Phase:** complete
**Next Action:** Open the next renderer milestone only after choosing the next sprite/draw execution capability.
**Last Updated:** 2026-04-18T00:00:00-03:00
**Requirements Status:** 0 active · 20 validated · 0 deferred · 3 out of scope

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

## Blockers

- `GSD auto` still stalls with the installed local `qwen2.5-coder:3b` model: it completes with 0 tool calls while planning `M001-1pt4oy/S12`. Manual materialization was used for S12-S15 after local verification.
- `QOpenGLWidget` under `QT_QPA_PLATFORM=offscreen` still reports invalid contexts locally, so slice verification relies on protocol behavior and honest diagnostics rather than requiring a live GL context in CI.
