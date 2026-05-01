# GSD State

**Active Milestone:** M027-sidecar-ui-bridge
**Active Slice:** S01
**Active Task:** T01
**Phase:** review
**Next Action:** Caveman-review diff, then decide commit/push/PR for `gsd/M027/S01-sidecar-ui-bridge`.
**Last Updated:** 2026-05-01T15:51:42-03:00
**Requirements Status:** 0 active · 23 validated · 0 deferred · 3 out of scope

## Recent Decisions

- `M018-otbm-xml-serialization` is complete: Python `save_otbm` now writes `.otbm` plus waypoint, spawn, and house XML sidecars through `rme_core`.
- `M026-xml-sidecar-readback` has a green draft PR (#67): native `load_otbm` now loads waypoint, spawn, creature, and house XML sidecars.
- `M027-sidecar-ui-bridge` starts from the approved A route: connect existing waypoint and house UI workflows to editor-core sidecar state.
- `M027-sidecar-ui-bridge/S01/T01` is implemented locally: waypoint and house UI workflows now bridge to editor-core sidecar state with targeted Rust/Python tests passing.
- OTBM XML sidecars intentionally use legacy RME tag and attribute names from `source/io/map_xml_io.cpp`; M026 covers native readback, while M027 covers UI/domain workflows that populate those collections.
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
- Workflow health remediation now also holds in WSL: npm Python scripts launch through `scripts/run-python.mjs`, and the repo no longer forces Windows `cmd.exe` as the npm script shell.
- `M005-sprite-resolver` was completed in manual GSD mode: Ollama/GSD auto were not required, and the milestone added an honest item-id to sprite-resource resolver before any draw pass.
- `CANVAS-60-SPRITE-RESOLVER-CONTRACT/T01` is complete: immutable sprite lookup result statuses and payload fields are covered by `tests/python/test_sprite_resolver.py`.
- `CANVAS-60-SPRITE-RESOLVER-CONTRACT/T02` is complete: `SpriteResourceResolver` maps known item ids to primary sprite ids and reports unknown items explicitly.
- `CANVAS-60-SPRITE-RESOLVER-CONTRACT/T03` is complete: sprite payload lookup resolves pixel bytes when available and keeps missing-sprite status explicit when absent.
- `CANVAS-60-SPRITE-RESOLVER-CONTRACT/T04` is complete: repeated item lookups are cached and cache invalidation is tied to explicit source replacement.
- `CANVAS-60-SPRITE-RESOLVER-CONTRACT` is complete: S01 verified the sprite resolver contract with 249 local Python tests passing and S02 is now open for frame-plan resource integration.
- `CANVAS-61-FRAME-SPRITE-RESOURCES/T01` is complete: immutable frame sprite resource records carry tile position, item id, stack layer, and resolver result without changing renderer drawing.
- `CANVAS-61-FRAME-SPRITE-RESOURCES/T02` is complete: pure frame sprite resource collection resolves ordered ground items through `SpriteResourceResolver`.
- `CANVAS-61-FRAME-SPRITE-RESOURCES/T03` is complete: frame sprite resource collection appends stack item resources after each tile ground item while preserving item order.
- `CANVAS-61-FRAME-SPRITE-RESOURCES/T04` is complete: missing item and missing sprite resolver outcomes stay in frame sprite resource output.
- `CANVAS-61-FRAME-SPRITE-RESOURCES` is complete: S02 verified pure frame-plan sprite resource records with 254 local Python tests passing and S03 is now open for renderer diagnostics.
- `CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS/T01` is complete: pure immutable diagnostics count total, resolved, missing-item, and missing-sprite resource outcomes.
- `CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS/T02` is complete: sprite resource diagnostics expose stable summary text for empty, resolved, and missing states.
- `CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS/T03` is complete: renderer host diagnostic text now includes initialized sprite resource diagnostics without changing drawing behavior.
- `CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS/T04` is complete: renderer host sync now builds frame sprite diagnostics through an explicit resolver seam and reports honest missing-item defaults.
- `CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS` is complete: S03 verified sprite resource diagnostics with 260 local Python tests passing.
- `M005-sprite-resolver` is complete: item-id sprite resolution, frame resource records, and renderer diagnostic counts are tested while renderer drawing remains diagnostic-only.
- `M006-item-palette` was completed in manual GSD mode: the brush palette `Item` tab is search-first, model-backed, cached, and tested without claiming sprite rendering or full brush backend activation.
- `ITEM-10-MODEL-VIEW-PALETTE/T01` is complete: immutable item/category/query data contracts and cached catalog/result/category models are covered by item palette model tests.
- `ITEM-10-MODEL-VIEW-PALETTE/T02` is complete: `ItemPaletteWidget` loads item entries, filters through public search API, narrows by category, emits selected items, and shows honest empty state.
- `ITEM-10-MODEL-VIEW-PALETTE/T03` is complete: `BrushPaletteDock` mounts the real Item palette, delegates search, re-emits item selection, and preserves other tab navigation.
- `ITEM-10-MODEL-VIEW-PALETTE/T04` is complete: 50k-item load/search/category/cache performance assumptions and adjacent brush palette behavior are verified.
- `ITEM-10-MODEL-VIEW-PALETTE/T05` is complete: caveman-review gap on empty-state alignment was fixed with RED/GREEN test evidence.
- `ITEM-10-MODEL-VIEW-PALETTE` is complete: S01 verified item palette model/view behavior with 49 targeted Python tests passing, 261 full Python tests passing, preflight passing, and ruff clean.
- `M007-brush-activation-backend` was completed in manual GSD mode: backend mode, active brush id, active item id, and tool application behavior are covered without mixing pending UI-shell changes.
- `BRUSH-10-ACTIVATION-BACKEND-CONTRACT/T01` is complete: session activation fields delegate to `EditorModel`.
- `BRUSH-10-ACTIVATION-BACKEND-CONTRACT/T02` is complete: backend activation commands and invalid mode normalization are covered.
- `BRUSH-10-ACTIVATION-BACKEND-CONTRACT/T03` is complete: selection, drawing, erasing, preserved stack, and unsupported/no-active-item no-op paths are tested.
- `BRUSH-10-ACTIVATION-BACKEND-CONTRACT/T04` is complete: M007 closeout recorded verification and kept UI-shell dirty work unstaged.
- `BRUSH-10-ACTIVATION-BACKEND-CONTRACT` is complete: S01 verified backend activation behavior with 9 targeted Python tests passing, 261 full Python tests passing, preflight passing, and ruff clean.
- `M008-brush-shell-wiring` was completed in manual GSD mode: local jump dialogs, palette switching, brush mode toolbar state, and WSL preflight now align the UI shell with the canonical backend contract without widening into renderer work.
- `BRUSH-20-SHELL-COMMAND-WIRING/T01` is complete: WSL preflight now launches through a repo-local Python helper and platform-default npm script shell instead of hardcoded Windows `py -3` / `cmd.exe`.
- `BRUSH-20-SHELL-COMMAND-WIRING/T02` is complete: `FindBrushDialog` exposes palette and item-backed brush search results through a public dialog export seam.
- `BRUSH-20-SHELL-COMMAND-WIRING/T03` is complete: `Jump to Brush`, `Jump to Item`, palette switching, brush mode toolbar state, and adjacent editor shell actions now drive canonical backend/session state through focused `MainWindow` tests.
- `BRUSH-20-SHELL-COMMAND-WIRING/T04` is complete: activation backend, new-view, and canvas seam regressions remain green alongside the new shell wiring tests.
- `BRUSH-20-SHELL-COMMAND-WIRING/T05` is complete: M008 closeout recorded real verification, corrected the stale UI smoke command, and kept next action limited to scoped review/staging.
- `BRUSH-20-SHELL-COMMAND-WIRING` is complete: S01 verified shell wiring behavior with 53 targeted Python tests passing, preflight passing in WSL, and an honest offscreen startup smoke that kept the known `QOpenGLWidget` limitation explicit.
- `M015-core-map-model` is complete: basic sparse map storage and metadata logic was ported to `rme_core` and exposed via PyO3, with 50 targeted Rust tests passing and 268 Python tests passing.
- `M016-otbm-persistence` (Read phase) is complete: binary tree parsing of OTBM nodes, metadata attributes, tile areas, and items successfully ported to `rme_core`, with 59 targeted Rust tests and 268 Python tests passing.
- `M017-otbm-persistence` (Write phase) is complete: binary tree generation of OTBM nodes, metadata attributes, tile areas, and items successfully ported to `rme_core`, integrating Python bridge test coverage for `save_otbm`.
## Blockers

- `GSD auto` still stalls with the installed local `qwen2.5-coder:3b` model: it completes with 0 tool calls while planning `M001-1pt4oy/S12`. Manual materialization was used for S12-S15 after local verification.
- `QOpenGLWidget` under `QT_QPA_PLATFORM=offscreen` still reports invalid contexts locally, so slice verification relies on protocol behavior and honest diagnostics rather than requiring a live GL context in CI.
- Local network/socket health is restored: `git fetch origin` works and Ollama `/v1/models` responds. Branch remains `ahead 5, behind 6` with a dirty worktree after the M007 local commit, so do not rebase or publish until scoped changes are staged and committed cleanly.
- Current dirty worktree mixes older legacy-shell/tooling changes. Do not stage `pyrme/ui/main_window.py` file-wide without reviewing mixed hunks.
- `npm run gsd:status --silent` timed out in this WSL session without returning output, so M008 closeout used direct artifact updates instead of GSD status output.
- GSD status works in degraded filesystem mode on Windows; native addon/registry warnings remain non-blocking for manual GSD updates.
