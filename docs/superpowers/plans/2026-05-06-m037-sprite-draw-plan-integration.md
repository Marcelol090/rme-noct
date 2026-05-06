# M037 Sprite Draw Plan Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconnect sprite draw plan diagnostics from live canvas frames to canvas hosts.

**Architecture:** Keep drawing pixel-free. Export existing rendering contracts, then restore canvas-host state for explicit plans, injected catalog/atlas inputs, and asset-provider inputs. `_sync_canvas_frame()` remains the single refresh point for frame, resource, and draw-plan diagnostics.

**Tech Stack:** Python 3, PyQt6, pytest-qt, ruff, rtk, WSL.

---

## Context

Design source: `docs/superpowers/specs/2026-05-06-m037-sprite-draw-plan-integration-design.md`

Baseline RED:

```bash
QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py -q --tb=short
```

Current failure:

```text
ImportError: cannot import name 'SpriteDrawAssetInputs' from 'pyrme.rendering'
```

## Files

- Modify: `pyrme/rendering/__init__.py`
- Modify: `pyrme/ui/canvas_host.py`
- Test: `tests/python/test_canvas_sprite_draw_diagnostics.py`
- Verify: `tests/python/test_sprite_draw_commands.py`
- Verify: `tests/python/test_sprite_asset_provider.py`
- Verify: `tests/python/test_renderer_frame_plan_integration.py`
- Verify: `tests/python/test_frame_sprite_resources.py`
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M037-sprite-draw-plan/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M037-sprite-draw-plan/slices/S01/S01-SUMMARY.md`

## Task 1: Restore Rendering Exports

**Files:**
- Modify: `pyrme/rendering/__init__.py`
- Test: `tests/python/test_canvas_sprite_draw_diagnostics.py`

- [ ] **Step 1: Run RED**

```bash
QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py -q --tb=short
```

Expected: collection fails importing `SpriteDrawAssetInputs`.

- [ ] **Step 2: Export draw-plan contracts**

Add imports:

```python
from pyrme.rendering.sprite_asset_provider import (
    SpriteDrawAssetInputs,
    SpriteDrawAssetProvider,
    StaticSpriteDrawAssetProvider,
    build_sprite_draw_asset_bundle,
)
from pyrme.rendering.sprite_draw_commands import (
    SpriteAtlas,
    SpriteAtlasRegion,
    SpriteDrawCommand,
    SpriteDrawPlan,
    build_sprite_draw_plan,
)
from pyrme.rendering.sprite_frame import (
    SpriteCatalog,
    SpriteCatalogEntry,
    build_sprite_frame,
)
```

Add these names to `__all__`.

- [ ] **Step 3: Run collection GREEN to next failure**

```bash
QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py -q --tb=short
```

Expected: import error gone; tests now fail on missing canvas-host methods/diagnostics.

## Task 2: Restore Explicit Sprite Draw Plan Diagnostics

**Files:**
- Modify: `pyrme/ui/canvas_host.py`
- Test: `tests/python/test_canvas_sprite_draw_diagnostics.py`

- [ ] **Step 1: Add protocol names**

In `canvas_host.py`, import `SpriteDrawPlan` and add method tuple:

```python
_EDITOR_SPRITE_DRAW_PLAN_METHOD_NAMES = (
    "set_sprite_draw_plan",
    "sprite_draw_command_count",
    "unresolved_sprite_ids",
)
```

Add `EditorSpriteDrawPlanCanvasProtocol` and helper:

```python
class EditorSpriteDrawPlanCanvasProtocol(Protocol):
    def set_sprite_draw_plan(self, plan: SpriteDrawPlan) -> None: ...
    def sprite_draw_command_count(self) -> int: ...
    def unresolved_sprite_ids(self) -> tuple[int, ...]: ...


def implements_editor_sprite_draw_plan_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorSpriteDrawPlanCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_SPRITE_DRAW_PLAN_METHOD_NAMES)
```

- [ ] **Step 2: Add state and explicit setter**

In `_init_canvas_shell_state()`:

```python
self._sprite_draw_plan = SpriteDrawPlan(commands=(), unresolved_sprite_ids=())
self._sprite_draw_error: str | None = None
self._sprite_draw_inputs: tuple[SpriteCatalog, SpriteAtlas] | None = None
self._sprite_asset_provider: SpriteDrawAssetProvider | None = None
self._sprite_draw_override = False
```

Add methods:

```python
def set_sprite_draw_plan(self, plan: SpriteDrawPlan) -> None:
    self._sprite_draw_plan = plan
    self._sprite_draw_error = None
    self._sprite_draw_override = True
    self._state_changed()

def sprite_draw_command_count(self) -> int:
    return len(self._sprite_draw_plan.commands)

def unresolved_sprite_ids(self) -> tuple[int, ...]:
    return tuple(sorted(set(self._sprite_draw_plan.unresolved_sprite_ids)))
```

- [ ] **Step 3: Add diagnostics text**

In `diagnostic_text()`, append after sprite resource diagnostics:

```python
f"{self._sprite_resource_diagnostics.summary()}\n"
f"Sprite Draw Commands: {self.sprite_draw_command_count()}\n"
f"Unresolved Sprites: {_format_unresolved_sprite_ids(self.unresolved_sprite_ids())}"
```

Add helper:

```python
def _format_unresolved_sprite_ids(sprite_ids: tuple[int, ...]) -> str:
    if not sprite_ids:
        return "none"
    return ", ".join(str(sprite_id) for sprite_id in sprite_ids)
```

- [ ] **Step 4: Run explicit seam tests**

```bash
QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py::test_placeholder_canvas_reports_default_sprite_draw_diagnostics tests/python/test_canvas_sprite_draw_diagnostics.py::test_placeholder_canvas_accepts_sprite_draw_plan_and_reports_counts tests/python/test_canvas_sprite_draw_diagnostics.py::test_sprite_draw_plan_diagnostics_normalize_repeated_updates tests/python/test_canvas_sprite_draw_diagnostics.py::test_sprite_draw_plan_protocol_helper_detects_canvas_hosts -q --tb=short
```

Expected: four tests pass.

## Task 3: Restore Live Frame Draw Plan Refresh

**Files:**
- Modify: `pyrme/ui/canvas_host.py`
- Test: `tests/python/test_canvas_sprite_draw_diagnostics.py`

- [ ] **Step 1: Add input/provider setters**

Add imports:

```python
from pyrme.rendering import (
    SpriteAtlas,
    SpriteCatalog,
    SpriteDrawAssetProvider,
    build_sprite_draw_plan,
    build_sprite_frame,
)
```

Add methods:

```python
def set_sprite_draw_inputs(self, catalog: SpriteCatalog, atlas: SpriteAtlas) -> None:
    self._sprite_draw_inputs = (catalog, atlas)
    self._sprite_asset_provider = None
    self._sprite_draw_override = False
    self._state_changed()

def set_sprite_asset_provider(self, provider: SpriteDrawAssetProvider) -> None:
    self._sprite_asset_provider = provider
    self._sprite_draw_inputs = None
    self._sprite_draw_override = False
    self._state_changed()
```

- [ ] **Step 2: Build live draw plan inside `_sync_canvas_frame()`**

After `frame_plan = build_render_frame_plan(...)`, call a helper:

```python
self._sync_sprite_draw_plan(frame_plan)
```

Add helper:

```python
def _sync_sprite_draw_plan(self, frame_plan: RenderFramePlan | None) -> None:
    if self._sprite_draw_override:
        return
    self._sprite_draw_error = None
    if frame_plan is None:
        self._sprite_draw_plan = SpriteDrawPlan(commands=(), unresolved_sprite_ids=())
        return
    try:
        inputs = self._sprite_draw_inputs
        if self._sprite_asset_provider is not None:
            provider_inputs = self._sprite_asset_provider.sprite_draw_inputs()
            inputs = (provider_inputs.catalog, provider_inputs.atlas)
        if inputs is None:
            self._sprite_draw_plan = SpriteDrawPlan(commands=(), unresolved_sprite_ids=())
            return
        catalog, atlas = inputs
        sprite_frame = build_sprite_frame(frame_plan, catalog)
        self._sprite_draw_plan = build_sprite_draw_plan(
            sprite_frame,
            atlas,
            self._viewport,
        )
    except Exception as exc:
        self._sprite_draw_plan = SpriteDrawPlan(commands=(), unresolved_sprite_ids=())
        self._sprite_draw_error = f"sprite draw plan unavailable: {exc}"
```

In `diagnostic_text()`, include `_sprite_draw_error` only when set.

- [ ] **Step 3: Run live/provider tests**

```bash
QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py::test_placeholder_canvas_builds_sprite_draw_plan_from_live_frame tests/python/test_canvas_sprite_draw_diagnostics.py::test_placeholder_canvas_builds_sprite_draw_plan_from_asset_provider tests/python/test_canvas_sprite_draw_diagnostics.py::test_live_sprite_draw_plan_updates_when_frame_changes tests/python/test_canvas_sprite_draw_diagnostics.py::test_live_sprite_draw_plan_refreshes_provider_inputs_when_frame_changes tests/python/test_canvas_sprite_draw_diagnostics.py::test_explicit_sprite_draw_plan_overrides_live_fixture_inputs tests/python/test_canvas_sprite_draw_diagnostics.py::test_explicit_sprite_draw_plan_overrides_asset_provider tests/python/test_canvas_sprite_draw_diagnostics.py::test_failed_asset_provider_clears_stale_commands_and_preserves_frame tests/python/test_canvas_sprite_draw_diagnostics.py::test_invalid_live_sprite_metadata_clears_stale_commands -q --tb=short
```

Expected: listed tests pass.

## Task 4: Focused Regression and Closeout

**Files:**
- Modify: `.gsd/STATE.md`
- Modify: `.gsd/milestones/M037-sprite-draw-plan/slices/S01/S01-PLAN.md`
- Create: `.gsd/milestones/M037-sprite-draw-plan/slices/S01/S01-SUMMARY.md`

- [ ] **Step 1: Run focused regression**

```bash
QT_QPA_PLATFORM=offscreen PATH="$HOME/.local/bin:$PATH" rtk python3 -m pytest tests/python/test_canvas_sprite_draw_diagnostics.py tests/python/test_sprite_draw_commands.py tests/python/test_sprite_asset_provider.py tests/python/test_renderer_frame_plan_integration.py tests/python/test_frame_sprite_resources.py -q --tb=short
```

Expected: all pass.

- [ ] **Step 2: Run quality gates**

```bash
PATH="$HOME/.local/bin:$PATH" rtk python3 -m ruff check pyrme/rendering/__init__.py pyrme/ui/canvas_host.py tests/python/test_canvas_sprite_draw_diagnostics.py
git diff --check
PATH="$HOME/.local/bin:$PATH" rtk npm run preflight --silent
```

Expected: ruff says `All checks passed!`; diff check exits 0; preflight ends `Validation: ok`.

- [ ] **Step 3: Update GSD docs**

Mark `.gsd/milestones/M037-sprite-draw-plan/slices/S01/S01-PLAN.md` tasks complete and write `S01-SUMMARY.md` with exact verification commands/results.

Update `.gsd/STATE.md`:

```markdown
**Active Milestone:** M037-sprite-draw-plan
**Active Slice:** S01-SPRITE-DRAW-PLAN-INTEGRATION
**Active Task:** none
**Phase:** review
**Next Action:** Run caveman-review on M037/S01 diff, then commit and PR after clean review.
```

- [ ] **Step 4: caveman-review before commit**

Review diff. Required clean result:

- exports only existing rendering contracts
- canvas host diagnostics only
- no pixel drawing claim
- no atlas loading
- no minimap/Search menu/Rust/PyO3 changes

Commit only after clean review:

```bash
git add -- pyrme/rendering/__init__.py pyrme/ui/canvas_host.py .gsd/STATE.md .gsd/milestones/M037-sprite-draw-plan docs/superpowers/specs/2026-05-06-m037-sprite-draw-plan-integration-design.md docs/superpowers/plans/2026-05-06-m037-sprite-draw-plan-integration.md
git commit -m "feat(M037/S01): restore sprite draw plan diagnostics"
```

