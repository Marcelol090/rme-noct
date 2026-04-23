"""Shell-facing canvas host abstractions.

The legacy editor shell needs a stable widget seam while the renderer is
materialized slice by slice. Tests can inject custom canvas widgets while
the default shell uses a real OpenGL host with an honest diagnostic overlay.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeGuard, cast

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QFont, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPen
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QLabel, QWidget

from pyrme import __app_name__
from pyrme.core_bridge import create_editor_shell_state
from pyrme.editor import MapPosition
from pyrme.rendering import (
    DiagnosticTilePrimitive,
    RenderFramePlan,
    RenderTileCommand,
    SpriteAtlas,
    SpriteCatalog,
    SpriteDrawPlan,
    build_sprite_draw_plan,
    build_sprite_frame,
)
from pyrme.ui.canvas_frame import CanvasFrame, build_canvas_frame
from pyrme.ui.styles import qss_color
from pyrme.ui.theme import THEME, TYPOGRAPHY
from pyrme.ui.viewport import EditorViewport, ViewportSnapshot

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyrme.ui.editor_context import EditorContext


class CanvasWidgetProtocol(Protocol):
    def bind_editor_context(self, context: EditorContext) -> None: ...
    def set_position(self, x: int, y: int, z: int) -> None: ...
    def set_floor(self, z: int) -> None: ...
    def set_zoom(self, percent: int) -> None: ...
    def set_show_grid(self, enabled: bool) -> None: ...
    def set_ghost_higher(self, enabled: bool) -> None: ...
    def set_show_lower(self, enabled: bool) -> None: ...


class EditorViewFlagCanvasProtocol(Protocol):
    def set_view_flag(self, name: str, enabled: bool) -> None: ...


class EditorShowFlagCanvasProtocol(Protocol):
    def set_show_flag(self, name: str, enabled: bool) -> None: ...


class EditorFrameSummaryCanvasProtocol(Protocol):
    def set_frame_summary(self, summary: str) -> None: ...


class EditorFramePrimitivesCanvasProtocol(Protocol):
    def set_frame_primitives(
        self,
        primitives: tuple[DiagnosticTilePrimitive, ...],
    ) -> None: ...


class EditorSpriteDrawPlanCanvasProtocol(Protocol):
    def set_sprite_draw_plan(self, plan: SpriteDrawPlan) -> None: ...


_CANVAS_WIDGET_METHOD_NAMES = (
    "bind_editor_context",
    "set_position",
    "set_floor",
    "set_zoom",
    "set_show_grid",
    "set_ghost_higher",
    "set_show_lower",
)
_EDITOR_VIEW_FLAG_METHOD_NAMES = ("set_view_flag",)
_EDITOR_SHOW_FLAG_METHOD_NAMES = ("set_show_flag",)
_EDITOR_ACTIVATION_METHOD_NAMES = ("set_editor_mode", "set_active_brush")
_EDITOR_TOOL_METHOD_NAMES = ("apply_active_tool",)
_EDITOR_TOOL_CALLBACK_METHOD_NAMES = ("set_tool_applied_callback",)
_EDITOR_POINT_MAPPING_METHOD_NAMES = ("map_position_for_point",)
_EDITOR_FRAME_SUMMARY_METHOD_NAMES = ("set_frame_summary",)
_EDITOR_FRAME_PRIMITIVES_METHOD_NAMES = ("set_frame_primitives",)
_EDITOR_SPRITE_DRAW_PLAN_METHOD_NAMES = ("set_sprite_draw_plan",)
_EDITOR_VIEWPORT_METHOD_NAMES = ("set_viewport_snapshot",)


def _implements_widget_methods(widget: object, method_names: tuple[str, ...]) -> bool:
    return isinstance(widget, QWidget) and all(
        callable(getattr(widget, name, None)) for name in method_names
    )


def implements_canvas_widget_protocol(widget: object) -> TypeGuard[CanvasWidgetProtocol]:
    return _implements_widget_methods(widget, _CANVAS_WIDGET_METHOD_NAMES)


def implements_editor_view_flag_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorViewFlagCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_VIEW_FLAG_METHOD_NAMES)


def implements_editor_show_flag_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorShowFlagCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_SHOW_FLAG_METHOD_NAMES)


def implements_editor_activation_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorActivationCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_ACTIVATION_METHOD_NAMES)


def implements_editor_tool_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorToolCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_TOOL_METHOD_NAMES)


def implements_editor_tool_callback_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorToolCallbackCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_TOOL_CALLBACK_METHOD_NAMES)


def implements_editor_point_mapping_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorPointMappingCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_POINT_MAPPING_METHOD_NAMES)


def implements_editor_frame_summary_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorFrameSummaryCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_FRAME_SUMMARY_METHOD_NAMES)


def implements_editor_frame_primitives_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorFramePrimitivesCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_FRAME_PRIMITIVES_METHOD_NAMES)


def implements_editor_sprite_draw_plan_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorSpriteDrawPlanCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_SPRITE_DRAW_PLAN_METHOD_NAMES)


def implements_editor_viewport_canvas_protocol(
    widget: object,
) -> TypeGuard[EditorViewportCanvasProtocol]:
    return _implements_widget_methods(widget, _EDITOR_VIEWPORT_METHOD_NAMES)


class EditorActivationCanvasProtocol(Protocol):
    def set_editor_mode(self, mode: str) -> None: ...
    def set_active_brush(
        self,
        brush_name: str,
        brush_id: str | None,
        item_id: int | None,
    ) -> None: ...


class EditorToolCanvasProtocol(Protocol):
    def apply_active_tool(self) -> EditorToolApplyResult: ...


class EditorToolCallbackCanvasProtocol(Protocol):
    def set_tool_applied_callback(self, callback) -> None: ...


class EditorPointMappingCanvasProtocol(Protocol):
    def map_position_for_point(self, point: QPoint) -> MapPosition: ...


class EditorViewportCanvasProtocol(Protocol):
    def set_viewport_snapshot(self, snapshot: ViewportSnapshot) -> None: ...


@dataclass(frozen=True, slots=True)
class EditorToolApplyResult:
    changed: bool
    position: MapPosition


class _CanvasShellStateMixin:
    """Shared shell-state and input behavior for canvas host widgets."""

    def _init_canvas_shell_state(self) -> None:
        self.editor_context: EditorContext | None = None
        self._shell_core = create_editor_shell_state()
        self._position = (32000, 32000, 7)
        self._floor = 7
        self._zoom_percent = 100
        self._viewport = EditorViewport()
        self._show_grid = False
        self._ghost_higher = False
        self._show_lower = True
        self._view_flags: dict[str, bool] = {}
        self._show_flags: dict[str, bool] = {}
        self._render_summary = "tool idle"
        self._canvas_frame = build_canvas_frame(None, self._viewport)
        self._frame_summary = self._canvas_frame.summary()
        self._frame_primitives: tuple[DiagnosticTilePrimitive, ...] = ()
        self._sprite_draw_plan = SpriteDrawPlan((), ())
        self._sprite_draw_inputs: tuple[SpriteCatalog, SpriteAtlas] | None = None
        self._core_mode = "native" if self._shell_core.is_native() else "python-fallback"
        self._editor_mode = "drawing"
        self._active_brush_name = "Select"
        self._active_brush_id: str | None = None
        self._active_item_id: int | None = None
        self._tool_applied_callback: Callable[[EditorToolApplyResult], None] | None = None
        cast("QWidget", self).setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._state_changed()

    def bind_editor_context(self, context: EditorContext) -> None:
        self.editor_context = context
        self._state_changed()

    def set_position(self, x: int, y: int, z: int) -> None:
        self._position = self._shell_core.set_position(x, y, z)
        self._floor = self._position[2]
        self._viewport.set_center(*self._position)
        self._state_changed()

    def set_floor(self, z: int) -> None:
        self._floor = self._shell_core.set_floor(z)
        self._position = self._shell_core.position()
        self._viewport.set_floor(self._floor)
        self._state_changed()

    def set_zoom(self, percent: int) -> None:
        self._zoom_percent = self._shell_core.set_zoom_percent(percent)
        self._viewport.set_zoom_percent(self._zoom_percent)
        self._state_changed()

    def set_viewport_snapshot(self, snapshot: ViewportSnapshot) -> None:
        self._viewport.restore(snapshot)
        self._position = self._viewport.center
        self._floor = self._viewport.floor
        self._zoom_percent = self._viewport.zoom_percent
        self._state_changed()

    def set_show_grid(self, enabled: bool) -> None:
        self._show_grid = self._shell_core.set_show_grid(enabled)
        self._state_changed()

    def set_ghost_higher(self, enabled: bool) -> None:
        self._ghost_higher = self._shell_core.set_ghost_higher(enabled)
        self._state_changed()

    def set_show_lower(self, enabled: bool) -> None:
        self._show_lower = self._shell_core.set_show_lower(enabled)
        self._state_changed()

    def set_view_flag(self, name: str, enabled: bool) -> None:
        self._view_flags[name] = enabled
        with suppress(ValueError):
            self._shell_core.set_view_flag(name, enabled)
        self._state_changed()

    def set_show_flag(self, name: str, enabled: bool) -> None:
        self._show_flags[name] = enabled
        core_name = "show_animation" if name == "show_preview" else name
        with suppress(ValueError):
            self._shell_core.set_show_flag(core_name, enabled)
        self._state_changed()

    def set_editor_mode(self, mode: str) -> None:
        self._editor_mode = mode
        self._state_changed()

    def set_active_brush(
        self,
        brush_name: str,
        brush_id: str | None,
        item_id: int | None,
    ) -> None:
        self._active_brush_name = brush_name
        self._active_brush_id = brush_id
        self._active_item_id = item_id
        self._state_changed()

    def set_tool_applied_callback(
        self, callback: Callable[[EditorToolApplyResult], None]
    ) -> None:
        self._tool_applied_callback = callback

    def apply_active_tool(self) -> EditorToolApplyResult:
        return self.apply_active_tool_at_position(MapPosition(*self._position))

    def map_position_for_point(self, point: QPoint) -> MapPosition:
        x, y, z = self._viewport.screen_to_map(point.x(), point.y())
        return MapPosition(x, y, z)

    def apply_active_tool_at_position(
        self,
        position: MapPosition,
    ) -> EditorToolApplyResult:
        if self.editor_context is None:
            self._render_summary = "tool apply unavailable: no editor context"
            self._state_changed()
            return EditorToolApplyResult(
                changed=False,
                position=position,
            )
        changed = self.editor_context.session.editor.apply_active_tool_at(position)
        mode = self.editor_context.session.mode
        summary = f"{mode} @ {position.x},{position.y},{position.z:02d}"
        if changed:
            self._render_summary = f"tool applied: {summary}"
        else:
            self._render_summary = f"tool no-op: {summary}"
        self._state_changed()
        return EditorToolApplyResult(changed=changed, position=position)

    def _notify_tool_applied(
        self,
        result: EditorToolApplyResult | None = None,
    ) -> None:
        if result is None:
            result = self.apply_active_tool()
        if self._tool_applied_callback is not None:
            self._tool_applied_callback(result)

    def _mouse_target_position(self, event: QMouseEvent) -> MapPosition:
        return self.map_position_for_point(event.pos())

    def mousePressEvent(self, event: QMouseEvent | None) -> None:  # noqa: N802
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            self._notify_tool_applied(
                self.apply_active_tool_at_position(self._mouse_target_position(event))
            )
            cast("QWidget", self).setFocus(Qt.FocusReason.MouseFocusReason)
            event.accept()
            return
        QWidget.mousePressEvent(cast("QWidget", self), event)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:  # noqa: N802
        if event is not None and event.key() in {
            Qt.Key.Key_Space,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        }:
            self._notify_tool_applied()
            event.accept()
            return
        QWidget.keyPressEvent(cast("QWidget", self), event)

    def set_render_summary(self, summary: str) -> None:
        self._render_summary = summary
        self._state_changed()

    def set_frame_summary(self, summary: str) -> None:
        self._frame_summary = summary
        self._state_changed()

    def set_frame_primitives(
        self,
        primitives: tuple[DiagnosticTilePrimitive, ...],
    ) -> None:
        self._frame_primitives = tuple(primitives)
        self._state_changed()

    def frame_primitive_count(self) -> int:
        return len(self._frame_primitives)

    def set_sprite_draw_plan(self, plan: SpriteDrawPlan) -> None:
        self._sprite_draw_inputs = None
        self._sprite_draw_plan = SpriteDrawPlan(
            commands=tuple(plan.commands),
            unresolved_sprite_ids=tuple(sorted(set(plan.unresolved_sprite_ids))),
        )
        self._state_changed()

    def set_sprite_draw_inputs(
        self,
        catalog: SpriteCatalog,
        atlas: SpriteAtlas,
    ) -> None:
        self._sprite_draw_inputs = (catalog, atlas)
        self._state_changed()

    def sprite_draw_command_count(self) -> int:
        return len(self._sprite_draw_plan.commands)

    def unresolved_sprite_ids(self) -> tuple[int, ...]:
        return self._sprite_draw_plan.unresolved_sprite_ids

    def canvas_frame(self) -> CanvasFrame:
        return self._canvas_frame

    def set_core_mode(self, core_mode: str) -> None:
        self._core_mode = core_mode
        self._state_changed()

    def diagnostic_text(self) -> str:
        x, y, z = self._position
        active_view = ", ".join(
            name for name, enabled in sorted(self._view_flags.items()) if enabled
        ) or "none"
        active_show = ", ".join(
            name for name, enabled in sorted(self._show_flags.items()) if enabled
        ) or "none"
        active_item = (
            str(self._active_item_id) if self._active_item_id is not None else "none"
        )
        active_brush_id = self._active_brush_id or "none"
        return (
            f"{__app_name__} Canvas\n\n"
            f"{self._diagnostic_intro()}\n"
            f"Document: {self._document_name()}\n"
            f"Core Mode: {self._core_mode}\n"
            f"Shell State: {self._shell_core.render_summary()}\n"
            f"Editor Mode: {self._editor_mode}\n"
            f"Active Brush: {self._active_brush_name} ({active_brush_id})\n"
            f"Active Item: {active_item}\n"
            f"Position: {x}, {y}, {z:02d}\n"
            f"Floor: {self._floor:02d} | Zoom: {self._zoom_percent}%\n"
            f"Grid: {'ON' if self._show_grid else 'OFF'} | "
            f"Ghost Higher: {'ON' if self._ghost_higher else 'OFF'} | "
            f"Show Lower: {'ON' if self._show_lower else 'OFF'}\n"
            f"View Flags: {active_view}\n"
            f"Show Flags: {active_show}\n"
            f"{self._render_summary}\n"
            f"{self._frame_summary}\n"
            f"Visible Tiles: {self._canvas_frame.tile_count}\n"
            f"Map Generation: {self._canvas_frame.map_generation}\n"
            f"Visible Rect: {_format_visible_rect(self._canvas_frame.visible_rect)}\n"
            f"Tile Primitives: {self.frame_primitive_count()}\n"
            f"Sprite Draw Commands: {self.sprite_draw_command_count()}\n"
            f"Unresolved Sprites: {_format_unresolved_sprite_ids(self.unresolved_sprite_ids())}"
        )

    def _diagnostic_intro(self) -> str:
        return "Rust-backed wgpu renderer will be integrated in a later slice."

    def _document_name(self) -> str:
        if self.editor_context is None:
            return "Untitled"
        return str(self.editor_context.session.document.name)

    def _state_changed(self) -> None:
        raise NotImplementedError

    def _sync_canvas_frame(self) -> None:
        try:
            self._canvas_frame = build_canvas_frame(self.editor_context, self._viewport)
            self._frame_summary = self._canvas_frame.summary()
            self._frame_primitives = tuple(
                DiagnosticTilePrimitive(
                    position=tile.position,
                    screen_rect=tile.screen_rect,
                    label=_tile_label(tile.ground_item_id, tile.item_ids),
                )
                for tile in self._canvas_frame.tiles
            )
            self._sync_live_sprite_draw_plan()
        except Exception as exc:
            self._canvas_frame = build_canvas_frame(None, self._viewport)
            self._frame_summary = f"frame plan unavailable: {exc}"
            self._frame_primitives = ()

    def _sync_live_sprite_draw_plan(self) -> None:
        if self._sprite_draw_inputs is None:
            return
        try:
            catalog, atlas = self._sprite_draw_inputs
            frame_plan = _render_frame_plan_from_canvas_frame(self._canvas_frame)
            sprite_frame = build_sprite_frame(frame_plan, catalog)
            self._sprite_draw_plan = build_sprite_draw_plan(
                sprite_frame,
                atlas,
                EditorViewport(self._canvas_frame.viewport_snapshot),
            )
        except Exception as exc:
            self._sprite_draw_plan = SpriteDrawPlan((), ())
            self._render_summary = f"sprite draw plan unavailable: {exc}"


class PlaceholderCanvasWidget(_CanvasShellStateMixin, QLabel):
    """Fallback label-based canvas for explicit tests and local fallback paths."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "QLabel {"
            f"  color: {qss_color(THEME.ash_lavender)};"
            "  font-size: 18px;"
            "  font-weight: 300;"
            f"  background-color: {qss_color(THEME.void_black)};"
            f"  border: 1px solid {qss_color(THEME.ghost_border)};"
            "  border-radius: 8px;"
            "  padding: 40px;"
            "}"
        )
        self._init_canvas_shell_state()

    def _state_changed(self) -> None:
        self._sync_canvas_frame()
        self.setText(self.diagnostic_text())

    def resizeEvent(self, event) -> None:  # noqa: N802
        size = event.size()
        self._viewport.set_view_size(size.width(), size.height())
        super().resizeEvent(event)


class RendererHostCanvasWidget(_CanvasShellStateMixin, QOpenGLWidget):
    """Real OpenGL-backed canvas host with a diagnostic overlay.

    This is intentionally not a map renderer yet. It is the Qt equivalent of the
    legacy GL canvas surface, while viewport ownership and real draw passes remain
    separate follow-on slices.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._gl_initialized = False
        self._drawable_size = (0, 0)
        self.setMouseTracking(True)
        self._init_canvas_shell_state()

    def initializeGL(self) -> None:  # noqa: N802
        self._gl_initialized = True
        self.update()

    def resizeGL(self, width: int, height: int) -> None:  # noqa: N802
        self._drawable_size = (width, height)
        self._viewport.set_view_size(width, height)
        self.update()

    def paintGL(self) -> None:  # noqa: N802
        painter = QPainter(self)
        self._paint_diagnostics(painter)

    def paintEvent(self, event: QPaintEvent | None) -> None:  # noqa: N802
        if self.isValid():
            super().paintEvent(event)
            return
        painter = QPainter(self)
        self._paint_diagnostics(painter)
        if event is not None:
            event.accept()

    def _state_changed(self) -> None:
        self._sync_canvas_frame()
        self.update()

    def _diagnostic_intro(self) -> str:
        return (
            "OpenGL renderer host is active; map rendering, screenshots, and "
            "viewport math remain pending in later slices."
        )

    def diagnostic_text(self) -> str:
        base = super().diagnostic_text()
        width, height = self._drawable_size
        return (
            f"{base}\n"
            f"OpenGL Context: {self._context_status()}\n"
            f"Drawable Size: {width}x{height}"
        )

    def _context_status(self) -> str:
        if not self.isValid():
            return "unavailable"
        context = self.context()
        if context is None:
            return "pending"
        return "ready" if self._gl_initialized else "created"

    def _paint_diagnostics(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), THEME.void_black)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self._paint_tile_primitives(painter)
        content_rect = self.rect().adjusted(20, 20, -20, -20)
        painter.setPen(QPen(THEME.ghost_border))
        painter.drawRoundedRect(content_rect, 12.0, 12.0)
        text_rect = content_rect.adjusted(20, 20, -20, -20)
        painter.setPen(THEME.moonstone_white)
        font = QFont(TYPOGRAPHY.code_label(11))
        font.setStyleHint(QFont.StyleHint.Monospace)
        painter.setFont(font)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self.diagnostic_text(),
        )
        painter.end()

    def _paint_tile_primitives(self, painter: QPainter) -> None:
        if not self._frame_primitives:
            return
        painter.save()
        painter.setPen(QPen(THEME.moonstone_white))
        painter.setBrush(QColor(80, 144, 112, 96))
        for primitive in self._frame_primitives:
            x, y, width, height = primitive.screen_rect
            painter.drawRect(QRect(x, y, width, height))
        painter.restore()


def _format_visible_rect(rect: tuple[float, float, float, float]) -> str:
    x, y, width, height = rect
    return f"{x:.2f},{y:.2f},{width:.2f},{height:.2f}"


def _format_unresolved_sprite_ids(sprite_ids: tuple[int, ...]) -> str:
    if not sprite_ids:
        return "none"
    return ", ".join(str(sprite_id) for sprite_id in sprite_ids)


def _render_frame_plan_from_canvas_frame(frame: CanvasFrame) -> RenderFramePlan:
    return RenderFramePlan(
        viewport=frame.viewport_snapshot,
        visible_rect=frame.visible_rect,
        tile_commands=tuple(
            RenderTileCommand(
                position=tile.position,
                ground_item_id=tile.ground_item_id,
                item_ids=tile.item_ids,
            )
            for tile in frame.tiles
        ),
    )


def _tile_label(ground_item_id: int | None, item_ids: tuple[int, ...]) -> str:
    base = str(ground_item_id) if ground_item_id is not None else "empty"
    return f"{base} +{len(item_ids)}" if item_ids else base
