# Requirements

This file is the explicit capability and coverage contract for the project.

Use it to track what is actively in scope, what has been validated by completed work, what is intentionally deferred, and what is explicitly out of scope.

## Active

- None.

## Validated

### R054 - Renderer asset provider must read DAT/SPR signatures before parsing records
- Class: core-capability
- Status: validated
- Description: The renderer asset path must read DAT and SPR signature headers from discovered client files before parsing item records, frame tables, pixels, or texture data.
- Why it matters: Legacy client asset detection validates file identity through signatures before deeper parsing, and this keeps the binary-reading boundary narrow enough to verify.
- Source: execution
- Primary owning slice: CANVAS-150-CLIENT-ASSET-SIGNATURES
- Supporting slices: CANVAS-140-CLIENT-ASSET-DISCOVERY, CANVAS-130-SPRITE-ASSET-BUNDLE, CANVAS-120-SPRITE-ASSET-PROVIDER
- Validation: validated
- Notes: Verified by `tests/python/test_client_asset_discovery.py`; signature reads open discovered files only, read one 4-byte little-endian header from each DAT/SPR file, preserve discovery warnings, and report legacy-style open/header warnings without parsing records or decoding pixels.

### R053 - Renderer asset provider must discover client DAT/SPR paths before parsing
- Class: core-capability
- Status: validated
- Description: The renderer asset path must locate configured client metadata and sprite files under a selected client root, with fallback to `Tibia.dat` and `Tibia.spr`, before reading or parsing those files.
- Why it matters: This mirrors the legacy client asset detection boundary and creates a safe discovery seam before signature reads, binary parsing, pixel decoding, or texture ownership.
- Source: execution
- Primary owning slice: CANVAS-140-CLIENT-ASSET-DISCOVERY
- Supporting slices: CANVAS-130-SPRITE-ASSET-BUNDLE, CANVAS-120-SPRITE-ASSET-PROVIDER
- Validation: validated
- Notes: Verified by `tests/python/test_client_asset_discovery.py`; discovery sanitizes configured names to basenames, prefers configured files, falls back to `Tibia.dat`/`Tibia.spr`, reports legacy-style missing-root/file warnings, and can be paired with an existing fixture sprite asset bundle provider.

### R052 - Sprite draw provider must support fixture asset bundles
- Class: core-capability
- Status: validated
- Description: Sprite draw assets must be groupable as an immutable fixture bundle of DAT-like records, SPR-like frame records, and atlas regions before real asset discovery exists.
- Why it matters: This gives future discovery and atlas lifecycle work a single record-owner seam while keeping binary parsing, pixel decoding, texture upload, and drawing out of the provider layer.
- Source: execution
- Primary owning slice: CANVAS-130-SPRITE-ASSET-BUNDLE
- Supporting slices: CANVAS-120-SPRITE-ASSET-PROVIDER, CANVAS-110-LIVE-SPRITE-DRAW-PLAN, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN
- Validation: validated
- Notes: Verified by `tests/python/test_sprite_asset_provider.py`; `SpriteDrawAssetBundle` builds provider inputs from existing DAT-like, SPR-like, and atlas-region records, and `build_sprite_draw_asset_bundle()` snapshots incoming iterables.

### R051 - Canvas host must consume sprite draw assets through a provider seam
- Class: core-capability
- Status: validated
- Description: Live sprite draw planning must accept a provider that supplies `SpriteCatalog` and `SpriteAtlas` together instead of requiring the canvas host to own only raw tuple wiring.
- Why it matters: This creates the ownership seam needed for future real DAT/SPR discovery and atlas lifecycle work while keeping frame planning independent from file loading and pixel painting.
- Source: execution
- Primary owning slice: CANVAS-120-SPRITE-ASSET-PROVIDER
- Supporting slices: CANVAS-110-LIVE-SPRITE-DRAW-PLAN, CANVAS-100-SPRITE-DRAW-DIAGNOSTICS, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN
- Validation: validated
- Notes: Verified by `tests/python/test_sprite_asset_provider.py` and `tests/python/test_canvas_sprite_draw_diagnostics.py`; canvas hosts accept `set_sprite_asset_provider(provider)`, refresh provider inputs during live frame synchronization, preserve direct fixture inputs, and keep explicit `set_sprite_draw_plan()` as an override.

### R050 - Canvas host must build sprite draw plans from live frame data
- Class: core-capability
- Status: validated
- Description: The canvas host must derive sprite draw diagnostics from the current `CanvasFrame` when fixture sprite catalog and atlas inputs are provided.
- Why it matters: This proves the shell can connect live map/frame state to sprite draw command planning before real asset loading or pixel painting exists.
- Source: execution
- Primary owning slice: CANVAS-110-LIVE-SPRITE-DRAW-PLAN
- Supporting slices: CANVAS-100-SPRITE-DRAW-DIAGNOSTICS, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN, CANVAS-80-SPR-FRAME-METADATA
- Validation: validated
- Notes: Verified by `tests/python/test_canvas_sprite_draw_diagnostics.py`; live inputs regenerate command diagnostics from visible frame tiles, refresh when frame data changes, and explicit `set_sprite_draw_plan()` remains a manual override.

### R049 - Renderer host must expose sprite draw plan diagnostics before painting
- Class: core-capability
- Status: validated
- Description: The canvas host must accept sprite draw plans and report draw command and unresolved sprite diagnostics without claiming pixel rendering.
- Why it matters: This verifies the shell seam that will later consume real sprite draw commands while preserving the honest no-pixels-yet renderer boundary.
- Source: execution
- Primary owning slice: CANVAS-100-SPRITE-DRAW-DIAGNOSTICS
- Supporting slices: CANVAS-60-SPRITE-CATALOG-SEAM, CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER, CANVAS-80-SPR-FRAME-METADATA, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN
- Validation: validated
- Notes: Verified by `tests/python/test_canvas_sprite_draw_diagnostics.py`; both placeholder and renderer-host canvas surfaces expose the sprite draw plan protocol, default to zero commands with no unresolved sprites, normalize unresolved sprite ids across repeated updates, and report command counts plus unresolved sprite ids after a plan is set.

### R048 - Sprite draw planning must produce atlas-backed command data
- Class: core-capability
- Status: validated
- Description: Resolved sprite-frame data must convert into deterministic draw commands with atlas source rectangles, screen destination rectangles, and missing atlas reporting before real painting begins.
- Why it matters: This creates the final pure data seam before renderer-host sprite diagnostics or GL painting, keeping atlas lookup separate from file parsing and widget drawing.
- Source: execution
- Primary owning slice: CANVAS-90-SPRITE-DRAW-COMMAND-PLAN
- Supporting slices: CANVAS-60-SPRITE-CATALOG-SEAM, CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER, CANVAS-80-SPR-FRAME-METADATA
- Validation: validated
- Notes: Verified by `tests/python/test_sprite_draw_commands.py`; `SpriteAtlas` maps sprite ids to source rectangles, `build_sprite_draw_plan` preserves ground-then-stack order, applies frame offsets to destination rectangles, and reports missing atlas or frame metadata sprite ids deterministically.

### R047 - Sprite catalog must carry SPR-like frame metadata
- Class: core-capability
- Status: validated
- Description: The renderer-facing sprite catalog must support deterministic SPR-like frame metadata by `sprite_id` before atlas placement or real drawing begins.
- Why it matters: Real sprite rendering needs frame dimensions and offsets, but renderer planning must keep file parsing, pixel decoding, and atlas placement separate from catalog metadata.
- Source: execution
- Primary owning slice: CANVAS-80-SPR-FRAME-METADATA
- Supporting slices: CANVAS-60-SPRITE-CATALOG-SEAM, CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER
- Validation: validated
- Notes: Verified by `tests/python/test_sprite_catalog_adapter.py`; `SprFrameRecord` attaches sorted `sprite_frames` metadata to matching `SpriteCatalogEntry` values while DAT-only records receive empty frame metadata.

### R046 - Sprite catalog must accept DAT-like adapter records
- Class: core-capability
- Status: validated
- Description: The renderer-facing sprite catalog must be constructible from DAT-like item sprite records without forcing renderer frame planning to import DAT adapter types.
- Why it matters: Real client asset integration needs a bridge from item metadata to sprite lookup, but renderer planning must stay testable and independent from file parsing.
- Source: execution
- Primary owning slice: CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER
- Supporting slices: CANVAS-60-SPRITE-CATALOG-SEAM
- Validation: validated
- Notes: Verified by `tests/python/test_sprite_catalog_adapter.py`; `DatSpriteRecord` feeds `SpriteCatalog` entries with deterministic adapter-owned metadata, and `build_sprite_frame` continues to report unresolved IDs through the catalog seam.

### R045 - Renderer host must consume frame plans as diagnostic draw primitives
- Class: core-capability
- Status: validated
- Description: The renderer host must project verified frame-plan tile commands into screen-space diagnostic primitives before adding sprite atlas rendering.
- Why it matters: This creates a tested draw-consumption seam between MapDrawer-style planning and later real sprite drawing, without pretending full renderer parity exists.
- Source: execution
- Primary owning slice: CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES
- Supporting slices: CANVAS-40-RENDER-FRAME-PLAN, CANVAS-30-MAP-VIEW-MATH
- Validation: validated
- Notes: Verified by `tests/python/test_diagnostic_tile_primitives.py` and `tests/python/test_renderer_frame_plan_integration.py`; primitive size follows viewport zoom and `RendererHostCanvasWidget` reports primitive count.

### R044 - Renderer path must expose an honest visible tile frame before sprite drawing
- Class: core-capability
- Status: validated
- Description: The renderer host must assemble all `MapModel` tiles within `EditorViewport.visible_rect()` for the active floor, with screen-rectangle position error below 1 pixel at 100% zoom, before any GL sprite draw pass is introduced.
- Why it matters: Legacy redux separates canvas input, viewport math, and MapDrawer orchestration. Python needs the same seam so later sprite rendering can consume a tested draw plan instead of reaching directly into shell state.
- Source: execution
- Primary owning slice: CANVAS-40-RENDER-FRAME-PLAN
- Supporting slices: CANVAS-10-RENDERER-HOST, CANVAS-20-VIEWPORT-MODEL, CANVAS-30-MAP-VIEW-MATH
- Validation: validated
- Notes: Verified by `tests/python/test_canvas_frame_model.py`, `tests/python/test_render_frame_plan.py`, and `tests/python/test_renderer_frame_plan_integration.py`; `CanvasFrame` includes visible same-floor tiles, stable `map_generation`, and `screen_rect` values derived from `EditorViewport.map_to_screen()` while the renderer host reports visible tile count without claiming real sprite drawing.

### R043 - Screen-to-map translation must adopt a legacy viewport model
- Class: primary-user-loop
- Status: validated
- Description: Real canvas input must translate widget points to map positions through a legacy-style scroll/zoom/floor model instead of the current minimal placeholder mapping.
- Why it matters: Honest interaction on a renderer-backed canvas depends on the same class of math that legacy redux keeps in `MainMapViewMath`.
- Source: execution
- Primary owning slice: CANVAS-30-MAP-VIEW-MATH
- Supporting slices: CANVAS-10-RENDERER-HOST, CANVAS-20-VIEWPORT-MODEL
- Validation: validated
- Notes: Verified by `tests/python/test_viewport_model.py` and `tests/python/test_canvas_seam_m4.py`; `EditorViewport` now exposes legacy-style `screen_to_map`, `map_to_screen`, and visible-rect math, and default canvas click handling applies tools through that viewport mapping.

### R042 - Viewport ownership must move out of MainWindow
- Class: core-capability
- Status: validated
- Description: The Python shell must introduce a viewport owner equivalent to the legacy redux `MapWindow`/`MainMapViewport` model so center position, scroll origin, and zoom stop living ad hoc inside `MainWindow`.
- Why it matters: The new renderer host is real, but correct camera behavior still requires a dedicated viewport state owner before coordinate math or rendering can become legacy-faithful.
- Source: execution
- Primary owning slice: CANVAS-20-VIEWPORT-MODEL
- Supporting slices: CANVAS-10-RENDERER-HOST
- Validation: validated
- Notes: Verified by `tests/python/test_viewport_model.py`, `tests/python/test_main_window_new_view.py`, `tests/python/test_main_window_viewport_model.py`, and `tests/python/test_canvas_seam_m4.py`; each editor view now owns an `EditorViewport` with center, scroll origin, floor, zoom, previous-position history, and snapshot/restore behavior while `MainWindow` keeps compatibility mirrors only.

### R014 - Legacy Selection parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell must complete the legacy `Selection` menu group with correct submenu placement, labels, shortcuts, and selection-mode exposure.
- Why it matters: `Selection` is still a core editing workflow surface and remains the next large uncovered legacy family after `Edit`.
- Source: execution
- Primary owning slice: LEGACY-60-SELECTION
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_selection_menu.py` and XML-backed `menu_path11..13`; selection-dependent actions now gate on real local selection presence, `Selection Mode` persists defaults through settings, and `Lower Floors`/`Visible Floors` are coupled honestly to `View -> Show all Floors`.

### R007 - Legacy File parity
- Class: launchability
- Status: validated
- Description: The Python shell must match the legacy `File` menu structure, including the correct grouping for import, export, and reload actions.
- Why it matters: File actions are part of the launchable editor shell and are user-visible entry points.
- Source: execution
- Primary owning slice: LEGACY-10-FILE
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_file_menu.py` and XML-backed `menu_path0..3`; `Import`, `Export`, `Reload`, and empty `Recent Files` now match legacy structure while file-system and preference backends remain explicit safe gaps.

### R008 - Legacy auxiliary menus parity
- Class: continuity
- Status: validated
- Description: The Python shell must close parity for `Experimental`, `Scripts`, and `About` without inventing a second product surface.
- Why it matters: The legacy menu tree is only complete when every top-level group is either implemented or explicitly limited.
- Source: execution
- Primary owning slice: LEGACY-110-EXPERIMENTAL
- Supporting slices: LEGACY-120-SCRIPTS, LEGACY-130-ABOUT, LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by slices `S12`, `S13`, and `S14`, plus the final milestone audit.

### R009 - Final legacy parity audit
- Class: quality-attribute
- Status: validated
- Description: The shell must pass a final parity audit against `menubar.xml` for every in-scope menu family before the epic can close.
- Why it matters: The milestone is about verified parity, not partial similarity.
- Source: execution
- Primary owning slice: LEGACY-140-FINAL-AUDIT
- Supporting slices: LEGACY-00-CONTRACT, LEGACY-90-NAVIGATE, LEGACY-100-WINDOW
- Validation: validated
- Notes: Verified by `tests/python/test_main_window_parity_phase2.py`, `tests/python/test_legacy_menu_contract.py`, and the covered local Python suite recorded in `S15`.

### R006 - Legacy Edit menu parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell matches the legacy `Edit` menu structure, submenu placement, labels, shortcuts, and the `Border Automagic` default, while keeping backend-heavy handlers as explicit safe gaps.
- Why it matters: `Edit` is a large, user-visible editor surface and needed to be closed independently before `Selection`.
- Source: execution
- Primary owning slice: LEGACY-20-EDIT
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_edit_menu.py` plus the XML-backed `menu_path4..6` parity checks; `Border Automagic` now restores from persisted settings and uses the legacy-style enable/disable status text, while Undo/Redo/pasteboard-backed behavior remains explicit backend work.

### R005 - Legacy Show menu parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell matches the legacy `Show` menu structure, labels, shortcuts, and checkable defaults, while keeping renderer/display semantics honest through local shell state plus the optional canvas show-flag seam.
- Why it matters: `Show` is part of the visual parity contract and should not be approximated ad hoc.
- Source: execution
- Primary owning slice: LEGACY-80-SHOW
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_show_menu.py`; all `Show` toggles are exposed as checkable actions with legacy defaults and are forwarded through `set_show_flag` when the active canvas exposes that seam.

### R004 - Legacy View menu parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell matches the legacy `View` menu structure, labels, shortcuts, checkable defaults, and reuses safe local canvas seams without claiming renderer-specific behavior.
- Why it matters: View controls are a direct extension of the existing shell-state foundation.
- Source: execution
- Primary owning slice: LEGACY-70-VIEW
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_view_menu.py`; `Show grid` and `Ghost higher floors` drive existing canvas seams, while remaining View flags are local state forwarded through `set_view_flag` when available and are now preserved per view/tab shell snapshot.

### R003 - Legacy Map menu surface parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell matches the legacy `Map` menu structure and keeps supported action labels faithful to the XML contract, while documenting backend gaps for town editing, cleanup handlers, and statistics explicitly.
- Why it matters: Map-level commands are core editor behavior and must not drift from the legacy product.
- Source: execution
- Primary owning slice: LEGACY-50-MAP
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_map_menu.py`; `Properties...` reuses `MapPropertiesDialog`, while `Edit Towns`, cleanup, and `Statistics` report safe backend gaps.

### R002 - Legacy Search menu parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell matches the legacy `Search` menu structure and keeps search actions aligned with legacy labels and shortcuts, while documenting map-search backend gaps explicitly.
- Why it matters: Search actions are part of the user-facing editor loop and already have partial local seams.
- Source: execution
- Primary owning slice: LEGACY-40-SEARCH
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_search_menu.py`, with `Find Item...` reusing `FindItemDialog` and map-wide searches reporting safe backend gaps.

### R001 - Legacy Editor menu parity
- Class: primary-user-loop
- Status: validated
- Description: The Python shell exposes the legacy `Editor` menu labels, ordering, and shortcuts, wires `New View`, fullscreen, and zoom to local shell seams, and documents `Take Screenshot` as a backend gap.
- Why it matters: `Editor` is the next high-value legacy surface after navigation and window parity.
- Source: execution
- Primary owning slice: LEGACY-30-EDITOR
- Supporting slices: LEGACY-140-FINAL-AUDIT
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_editor_contract.py`, `tests/python/test_legacy_editor_shell.py`, and `tests/python/test_main_window_new_view.py`.

### R010 - Legacy menu contract foundation exists in code
- Class: core-capability
- Status: validated
- Description: The Python shell now exposes the legacy top-level menu order and a declarative first-wave action contract rooted in `legacy_menu_contract.py`.
- Why it matters: Every later parity slice depends on a stable menu/action contract instead of hand-built drift.
- Source: execution
- Primary owning slice: LEGACY-00-CONTRACT
- Supporting slices: none
- Validation: validated
- Notes: Verified by `tests/python/test_legacy_menu_contract.py` and `tests/python/test_main_window_menu_contract_phase1.py`.

### R011 - Navigate menu matches the legacy contract for the covered actions
- Class: primary-user-loop
- Status: validated
- Description: `Navigate` exposes the legacy labels, shortcuts, and `Floor 0` through `Floor 15`, and reuses the shell-state navigation seams already present in the Python shell.
- Why it matters: Navigation is a high-frequency editor loop and a core legacy parity surface.
- Source: execution
- Primary owning slice: LEGACY-90-NAVIGATE
- Supporting slices: LEGACY-00-CONTRACT, M5-SHELL-NAVIGATION
- Validation: validated
- Notes: Verified by the XML-backed and shell-wiring tests added for the `Navigate` slice.

### R012 - Window menu matches the legacy contract for docks, palette, and toolbars
- Class: primary-user-loop
- Status: validated
- Description: `Window` now matches the legacy structure for primary items, the `Palette` submenu, and the `Toolbars` submenu, and it binds to existing dock and toolbar surfaces.
- Why it matters: Window visibility and palette selection are part of the visible shell contract and must stay stable.
- Source: execution
- Primary owning slice: LEGACY-100-WINDOW
- Supporting slices: LEGACY-00-CONTRACT, TIER2-DIALOGS-DOCKS
- Validation: validated
- Notes: Verified by the same XML-backed and shell-wiring tests that closed the `Navigate/Window` slice.

### R013 - Persistent shell state is reused rather than rewritten
- Class: continuity
- Status: validated
- Description: The legacy parity work reuses the verified `M5-SHELL-NAVIGATION` shell-state and `QSettings` persistence model instead of inventing a second state path.
- Why it matters: This keeps parity work honest and reduces regression risk in floor, position, and visibility behavior.
- Source: execution
- Primary owning slice: M5-SHELL-NAVIGATION
- Supporting slices: LEGACY-90-NAVIGATE, LEGACY-100-WINDOW
- Validation: validated
- Notes: Verified by the M5 shell tests plus the current `Navigate/Window` shell regression tests.

### R040 - Production default canvas uses a real renderer host
- Class: core-capability
- Status: validated
- Description: The production default canvas must be a real GL-backed host widget instead of a placeholder label, while preserving the existing shell-state and input seams.
- Why it matters: Legacy redux uses a true GL canvas, and future renderer slices should build on a stable production host rather than replacing the widget surface again.
- Source: execution
- Primary owning slice: CANVAS-10-RENDERER-HOST
- Supporting slices: none
- Validation: validated
- Notes: Verified by `tests/python/test_canvas_seam_m4.py`; `MainWindow` now defaults to `RendererHostCanvasWidget`.

### R041 - Canvas seam verification remains honest under offscreen CI
- Class: quality-attribute
- Status: validated
- Description: The canvas seam must remain testable when `QOpenGLWidget` cannot acquire a valid context under `QT_QPA_PLATFORM=offscreen`, without pretending rendering is available.
- Why it matters: Headless verification is still the primary proof path for this repository, and OpenGL availability cannot be silently assumed.
- Source: execution
- Primary owning slice: CANVAS-10-RENDERER-HOST
- Supporting slices: tests/python/test_canvas_seam_m4.py
- Validation: validated
- Notes: Verified by the new renderer-host diagnostics and explicit placeholder/fake canvas injection tests.

## Deferred

- None.

## Out of Scope

### R030 - Inventing a new top-level menu taxonomy
- Class: anti-feature
- Status: out-of-scope
- Description: The Python shell must not invent new top-level menu structure or regroup legacy actions differently when `menubar.xml` already defines the contract.
- Why it matters: This prevents parity work from turning into a new product design.
- Source: execution
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: The legacy XML remains authoritative unless an explicit divergence is documented.

### R031 - Hiding missing backends behind fake shell behavior
- Class: constraint
- Status: out-of-scope
- Description: Missing backend behavior must be documented per slice instead of being masked with placeholder behavior that looks complete.
- Why it matters: This keeps the milestone honest and makes follow-on slices reviewable.
- Source: execution
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Each slice must state real wiring versus remaining gaps.

### R032 - Expanding into canvas or rendering work outside shell parity
- Class: constraint
- Status: out-of-scope
- Description: Legacy menu parity slices must not reopen canvas, renderer, or unrelated backend work unless a slice explicitly scopes that dependency.
- Why it matters: This keeps the milestone narrow enough to verify and prevents menu parity from absorbing unrelated platform work.
- Source: execution
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Existing shell seams should be reused; new backend work belongs in separate milestones or explicitly scoped slices.

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R001 | primary-user-loop | validated | LEGACY-30-EDITOR | LEGACY-140-FINAL-AUDIT | validated |
| R002 | primary-user-loop | validated | LEGACY-40-SEARCH | LEGACY-140-FINAL-AUDIT | validated |
| R003 | primary-user-loop | validated | LEGACY-50-MAP | LEGACY-140-FINAL-AUDIT | validated |
| R004 | primary-user-loop | validated | LEGACY-70-VIEW | LEGACY-140-FINAL-AUDIT | validated |
| R005 | primary-user-loop | validated | LEGACY-80-SHOW | LEGACY-140-FINAL-AUDIT | validated |
| R006 | primary-user-loop | validated | LEGACY-20-EDIT | LEGACY-140-FINAL-AUDIT | validated |
| R007 | launchability | validated | LEGACY-10-FILE | LEGACY-140-FINAL-AUDIT | validated |
| R008 | continuity | validated | LEGACY-110-EXPERIMENTAL | LEGACY-120-SCRIPTS, LEGACY-130-ABOUT, LEGACY-140-FINAL-AUDIT | validated |
| R009 | quality-attribute | validated | LEGACY-140-FINAL-AUDIT | LEGACY-00-CONTRACT, LEGACY-90-NAVIGATE, LEGACY-100-WINDOW | validated |
| R010 | core-capability | validated | LEGACY-00-CONTRACT | none | validated |
| R011 | primary-user-loop | validated | LEGACY-90-NAVIGATE | LEGACY-00-CONTRACT, M5-SHELL-NAVIGATION | validated |
| R012 | primary-user-loop | validated | LEGACY-100-WINDOW | LEGACY-00-CONTRACT, TIER2-DIALOGS-DOCKS | validated |
| R013 | continuity | validated | M5-SHELL-NAVIGATION | LEGACY-90-NAVIGATE, LEGACY-100-WINDOW | validated |
| R014 | primary-user-loop | validated | LEGACY-60-SELECTION | LEGACY-140-FINAL-AUDIT | validated |
| R040 | core-capability | validated | CANVAS-10-RENDERER-HOST | none | validated |
| R041 | quality-attribute | validated | CANVAS-10-RENDERER-HOST | tests/python/test_canvas_seam_m4.py | validated |
| R042 | core-capability | validated | CANVAS-20-VIEWPORT-MODEL | CANVAS-10-RENDERER-HOST | validated |
| R043 | primary-user-loop | validated | CANVAS-30-MAP-VIEW-MATH | CANVAS-10-RENDERER-HOST, CANVAS-20-VIEWPORT-MODEL | validated |
| R044 | core-capability | validated | CANVAS-40-RENDER-FRAME-PLAN | CANVAS-10-RENDERER-HOST, CANVAS-20-VIEWPORT-MODEL, CANVAS-30-MAP-VIEW-MATH | validated |
| R045 | core-capability | validated | CANVAS-50-DIAGNOSTIC-TILE-PRIMITIVES | CANVAS-40-RENDER-FRAME-PLAN, CANVAS-30-MAP-VIEW-MATH | validated |
| R046 | core-capability | validated | CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER | CANVAS-60-SPRITE-CATALOG-SEAM | validated |
| R047 | core-capability | validated | CANVAS-80-SPR-FRAME-METADATA | CANVAS-60-SPRITE-CATALOG-SEAM, CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER | validated |
| R048 | core-capability | validated | CANVAS-90-SPRITE-DRAW-COMMAND-PLAN | CANVAS-60-SPRITE-CATALOG-SEAM, CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER, CANVAS-80-SPR-FRAME-METADATA | validated |
| R049 | core-capability | validated | CANVAS-100-SPRITE-DRAW-DIAGNOSTICS | CANVAS-60-SPRITE-CATALOG-SEAM, CANVAS-70-SPRITE-CATALOG-DAT-ADAPTER, CANVAS-80-SPR-FRAME-METADATA, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN | validated |
| R050 | core-capability | validated | CANVAS-110-LIVE-SPRITE-DRAW-PLAN | CANVAS-100-SPRITE-DRAW-DIAGNOSTICS, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN, CANVAS-80-SPR-FRAME-METADATA | validated |
| R051 | core-capability | validated | CANVAS-120-SPRITE-ASSET-PROVIDER | CANVAS-110-LIVE-SPRITE-DRAW-PLAN, CANVAS-100-SPRITE-DRAW-DIAGNOSTICS, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN | validated |
| R052 | core-capability | validated | CANVAS-130-SPRITE-ASSET-BUNDLE | CANVAS-120-SPRITE-ASSET-PROVIDER, CANVAS-110-LIVE-SPRITE-DRAW-PLAN, CANVAS-90-SPRITE-DRAW-COMMAND-PLAN | validated |
| R053 | core-capability | validated | CANVAS-140-CLIENT-ASSET-DISCOVERY | CANVAS-130-SPRITE-ASSET-BUNDLE, CANVAS-120-SPRITE-ASSET-PROVIDER | validated |
| R054 | core-capability | validated | CANVAS-150-CLIENT-ASSET-SIGNATURES | CANVAS-140-CLIENT-ASSET-DISCOVERY, CANVAS-130-SPRITE-ASSET-BUNDLE, CANVAS-120-SPRITE-ASSET-PROVIDER | validated |
| R030 | anti-feature | out-of-scope | none | none | n/a |
| R031 | constraint | out-of-scope | none | none | n/a |
| R032 | constraint | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 0
- Mapped to slices: 29
- Validated: 29
- Unmapped active requirements: 0
