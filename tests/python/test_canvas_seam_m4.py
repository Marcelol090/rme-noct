from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from PyQt6.QtCore import QPoint, QSettings, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QWidget

from pyrme import __app_name__, __version__
from pyrme.editor import MapPosition, TileState
from pyrme.ui.canvas_host import (
    EditorToolApplyResult,
    PlaceholderCanvasWidget,
    RendererHostCanvasWidget,
    implements_canvas_widget_protocol,
    implements_editor_activation_canvas_protocol,
    implements_editor_point_mapping_canvas_protocol,
    implements_editor_show_flag_canvas_protocol,
    implements_editor_tool_callback_canvas_protocol,
    implements_editor_tool_canvas_protocol,
    implements_editor_view_flag_canvas_protocol,
)
from pyrme.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[2]


def _make_workspace(name: str) -> Path:
    workspace = ROOT / ".tmp-tests" / f"{name}-{uuid.uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def _build_settings(root: Path, name: str) -> QSettings:
    return QSettings(str(root / name), QSettings.Format.IniFormat)


class _FakeCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor_context = None
        self.position: tuple[int, int, int] | None = None
        self.floor: int | None = None
        self.zoom_percent: int | None = None
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.show_lower: bool | None = None
        self.view_flags: dict[str, bool] = {}
        self.show_flags: dict[str, bool] = {}
        self.editor_mode: str | None = None
        self.active_brush_name: str | None = None
        self.active_brush_id: str | None = None
        self.active_item_id: int | None = None
        self.apply_count = 0

    def bind_editor_context(self, context) -> None:
        self.editor_context = context

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)

    def set_floor(self, z: int) -> None:
        self.floor = z

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled

    def set_view_flag(self, name: str, enabled: bool) -> None:
        self.view_flags[name] = enabled

    def set_show_flag(self, name: str, enabled: bool) -> None:
        self.show_flags[name] = enabled

    def set_editor_mode(self, mode: str) -> None:
        self.editor_mode = mode

    def set_active_brush(
        self,
        brush_name: str,
        brush_id: str | None,
        item_id: int | None,
    ) -> None:
        self.active_brush_name = brush_name
        self.active_brush_id = brush_id
        self.active_item_id = item_id

    def apply_active_tool(self) -> EditorToolApplyResult:
        self.apply_count += 1
        assert self.editor_context is not None
        assert self.position is not None
        position = MapPosition(*self.position)
        return EditorToolApplyResult(
            changed=self.editor_context.session.editor.apply_active_tool_at(position),
            position=position,
        )


class _BaseOnlyCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor_context = None
        self.position: tuple[int, int, int] | None = None
        self.floor: int | None = None
        self.zoom_percent: int | None = None
        self.show_grid: bool | None = None
        self.ghost_higher: bool | None = None
        self.show_lower: bool | None = None

    def bind_editor_context(self, context) -> None:
        self.editor_context = context

    def set_position(self, x: int, y: int, z: int) -> None:
        self.position = (x, y, z)

    def set_floor(self, z: int) -> None:
        self.floor = z

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent

    def set_show_grid(self, enabled: bool) -> None:
        self.show_grid = enabled

    def set_ghost_higher(self, enabled: bool) -> None:
        self.ghost_higher = enabled

    def set_show_lower(self, enabled: bool) -> None:
        self.show_lower = enabled


def test_canvas_capability_helpers_detect_placeholder_and_custom_canvas(qtbot) -> None:
    placeholder = PlaceholderCanvasWidget()
    custom = _FakeCanvasWidget()
    qtbot.addWidget(placeholder)
    qtbot.addWidget(custom)

    assert implements_canvas_widget_protocol(placeholder)
    assert implements_editor_view_flag_canvas_protocol(placeholder)
    assert implements_editor_show_flag_canvas_protocol(placeholder)
    assert implements_editor_activation_canvas_protocol(placeholder)
    assert implements_editor_tool_canvas_protocol(placeholder)
    assert implements_editor_tool_callback_canvas_protocol(placeholder)
    assert implements_editor_point_mapping_canvas_protocol(placeholder)

    assert implements_canvas_widget_protocol(custom)
    assert implements_editor_view_flag_canvas_protocol(custom)
    assert implements_editor_show_flag_canvas_protocol(custom)
    assert implements_editor_activation_canvas_protocol(custom)
    assert implements_editor_tool_canvas_protocol(custom)
    assert not implements_editor_tool_callback_canvas_protocol(custom)
    assert not implements_editor_point_mapping_canvas_protocol(custom)


def test_main_window_defaults_to_renderer_host_canvas(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "renderer-host-default.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    canvas = window._canvas
    assert isinstance(canvas, RendererHostCanvasWidget)
    assert implements_canvas_widget_protocol(canvas)
    assert implements_editor_view_flag_canvas_protocol(canvas)
    assert implements_editor_show_flag_canvas_protocol(canvas)
    assert implements_editor_activation_canvas_protocol(canvas)
    assert implements_editor_tool_canvas_protocol(canvas)
    assert implements_editor_tool_callback_canvas_protocol(canvas)
    assert implements_editor_point_mapping_canvas_protocol(canvas)
    assert canvas.diagnostic_text().startswith(f"{__app_name__} Canvas")
    assert "OpenGL Context:" in canvas.diagnostic_text()


def test_renderer_host_canvas_reports_offscreen_context_honestly(qtbot) -> None:
    canvas = RendererHostCanvasWidget()
    qtbot.addWidget(canvas)

    text = canvas.diagnostic_text()
    assert "Core Mode:" in text
    assert "Shell State:" in text
    assert "OpenGL Context:" in text
    if not canvas.isValid():
        assert "unavailable" in text


def test_main_window_uses_injected_canvas_factory_and_forwards_shell_state(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-seam")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        canvas = holder["canvas"]
        assert window._view_tabs.currentWidget() is canvas
        assert canvas.position == (32000, 32000, 7)
        assert canvas.floor == 7
        assert canvas.zoom_percent == 100
        assert canvas.editor_mode == "drawing"
        assert canvas.active_brush_name == "Select"
        assert canvas.active_brush_id is None
        assert canvas.active_item_id is None

        window._set_current_position(32100, 32150, 5)
        window.editor_zoom_in_action.trigger()

        assert window._active_view().viewport.center == (32100, 32150, 5)
        assert window._active_view().viewport.zoom_percent == 110
        assert canvas.position == (32100, 32150, 5)
        assert canvas.floor == 5
        assert canvas.zoom_percent == 110
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_rejects_canvas_factory_without_canvas_protocol() -> None:
    class _InvalidCanvasWidget(QWidget):
        pass

    temp_root = _make_workspace("canvas-invalid-contract")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _InvalidCanvasWidget:
            return _InvalidCanvasWidget(parent)

        try:
            MainWindow(
                settings=_build_settings(temp_root, "canvas-invalid-contract.ini"),
                canvas_factory=_canvas_factory,
            )
        except TypeError as exc:
            assert "CanvasWidgetProtocol" in str(exc)
        else:
            raise AssertionError("invalid canvas factory should fail fast")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_rejects_canvas_factory_with_non_callable_protocol_attrs() -> None:
    class _MisleadingCanvasWidget(QWidget):
        bind_editor_context = 1
        set_position = 1
        set_floor = 1
        set_zoom = 1
        set_show_grid = 1
        set_ghost_higher = 1
        set_show_lower = 1
        set_view_flag = 1
        set_show_flag = 1

    temp_root = _make_workspace("canvas-misleading-contract")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _MisleadingCanvasWidget:
            return _MisleadingCanvasWidget(parent)

        try:
            MainWindow(
                settings=_build_settings(temp_root, "canvas-misleading-contract.ini"),
                canvas_factory=_canvas_factory,
            )
        except TypeError as exc:
            assert "CanvasWidgetProtocol" in str(exc)
        else:
            raise AssertionError("misleading canvas factory should fail fast")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_canvas_capability_helpers_reject_non_callable_optional_attrs(qtbot) -> None:
    class _BadViewFlagCanvasWidget(_BaseOnlyCanvasWidget):
        set_view_flag = 1

    class _BadShowFlagCanvasWidget(_BaseOnlyCanvasWidget):
        set_show_flag = 1

    class _BadActivationCanvasWidget(_BaseOnlyCanvasWidget):
        set_editor_mode = 1
        set_active_brush = 1

    class _BadToolCanvasWidget(_BaseOnlyCanvasWidget):
        apply_active_tool = 1

    class _BadCallbackCanvasWidget(_BaseOnlyCanvasWidget):
        set_tool_applied_callback = 1

    class _BadPointMappingCanvasWidget(_BaseOnlyCanvasWidget):
        map_position_for_point = 1

    widgets = [
        _BadViewFlagCanvasWidget(),
        _BadShowFlagCanvasWidget(),
        _BadActivationCanvasWidget(),
        _BadToolCanvasWidget(),
        _BadCallbackCanvasWidget(),
        _BadPointMappingCanvasWidget(),
    ]
    for widget in widgets:
        qtbot.addWidget(widget)

    assert not implements_editor_view_flag_canvas_protocol(widgets[0])
    assert not implements_editor_show_flag_canvas_protocol(widgets[1])
    assert not implements_editor_activation_canvas_protocol(widgets[2])
    assert not implements_editor_tool_canvas_protocol(widgets[3])
    assert not implements_editor_tool_callback_canvas_protocol(widgets[4])
    assert not implements_editor_point_mapping_canvas_protocol(widgets[5])


def test_main_window_allows_canvas_without_optional_view_show_flag_seams(
    qtbot,
    settings_workspace: Path,
) -> None:
    holder: dict[str, _BaseOnlyCanvasWidget] = {}

    def _canvas_factory(parent: QWidget | None = None) -> _BaseOnlyCanvasWidget:
        canvas = _BaseOnlyCanvasWidget(parent)
        holder["canvas"] = canvas
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "base-canvas-no-flag-seams.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window.view_menu_actions["view_show_as_minimap"].trigger()
    window.show_menu_actions["show_light"].trigger()

    canvas = holder["canvas"]
    assert implements_canvas_widget_protocol(canvas)
    assert not implements_editor_view_flag_canvas_protocol(canvas)
    assert not implements_editor_show_flag_canvas_protocol(canvas)
    assert window._views[0].shell_state.view_flags["view_show_as_minimap"] is True
    assert window._views[0].shell_state.show_flags["show_light"] is True


def test_main_window_forwards_editor_activation_state_to_canvas(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-activation")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-activation.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        window.brush_mode_actions["selection"].trigger()
        assert window.brush_palette_dock is not None
        palette = window.brush_palette_dock.item_palette
        assert palette is not None
        palette._on_result_clicked(palette._result_model.index(0))

        canvas = holder["canvas"]
        assert canvas.editor_mode == "selection"
        assert canvas.active_brush_name == "Stone"
        assert canvas.active_brush_id == "item:1"
        assert canvas.active_item_id == 1
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_extended_tool_modes_update_canvas_activation(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-extended-modes")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-extended-modes.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        for mode in ("erasing", "fill", "move"):
            window.brush_mode_actions[mode].trigger()
            assert window._editor_context.session.mode == mode
            assert holder["canvas"].editor_mode == mode
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_apply_active_tool_uses_canvas_seam_and_marks_view_dirty(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-apply")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-apply.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        window._set_active_item_selection("Stone", 1)
        changed = window._apply_active_tool_at_cursor()

        canvas = holder["canvas"]
        assert changed is True
        assert canvas.apply_count == 1
        assert window._editor_context.session.document.is_dirty is True
        assert window._editor_context.session.editor.map_model.get_tile(
            MapPosition(32000, 32000, 7)
        ) == TileState(position=MapPosition(32000, 32000, 7), ground_item_id=1)
        assert window._view_tabs.tabText(0) == "Untitled*"
        assert window.statusBar().currentMessage() == "Applied Draw tool at 32000, 32000, 07."
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_apply_selection_tool_refreshes_selection_actions(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}
    temp_root = _make_workspace("canvas-select")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
            canvas = _FakeCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-select.ini"),
            canvas_factory=_canvas_factory,
            enable_docks=False,
        )
        qtbot.addWidget(window)

        assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is False
        window.brush_mode_actions["selection"].trigger()

        changed = window._apply_active_tool_at_cursor()

        assert changed is True
        assert holder["canvas"].apply_count == 1
        assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is True
        assert window.statusBar().currentMessage() == "Applied Select tool at 32000, 32000, 07."
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_main_window_apply_active_tool_uses_canvas_reported_target_position(qtbot) -> None:
    class _TargetedCanvasWidget(_FakeCanvasWidget):
        def apply_active_tool(self) -> EditorToolApplyResult:
            self.apply_count += 1
            assert self.editor_context is not None
            target = MapPosition(32010, 32020, 5)
            return EditorToolApplyResult(
                changed=self.editor_context.session.editor.apply_active_tool_at(target),
                position=target,
            )

    holder: dict[str, _TargetedCanvasWidget] = {}
    temp_root = _make_workspace("canvas-targeted-apply")

    try:
        def _canvas_factory(parent: QWidget | None = None) -> _TargetedCanvasWidget:
            canvas = _TargetedCanvasWidget(parent)
            holder["canvas"] = canvas
            return canvas

        window = MainWindow(
            settings=_build_settings(temp_root, "canvas-targeted-apply.ini"),
            canvas_factory=_canvas_factory,
        )
        qtbot.addWidget(window)

        window._set_active_item_selection("Stone", 1)
        changed = window._apply_active_tool_at_cursor()

        assert changed is True
        assert holder["canvas"].apply_count == 1
        assert window._coord_label.text() == "Pos: (X: 32010, Y: 32020, Z: 05)"
        assert window._editor_context.session.editor.map_model.get_tile(
            MapPosition(32010, 32020, 5)
        ) == TileState(position=MapPosition(32010, 32020, 5), ground_item_id=1)
        assert window.statusBar().currentMessage() == "Applied Draw tool at 32010, 32020, 05."
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_renderer_host_canvas_left_click_applies_draw_tool_and_refreshes_shell(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-draw.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_active_item_selection("Stone", 1)
    point = QPoint(0, 0)

    QTest.mouseClick(window._canvas, Qt.MouseButton.LeftButton, pos=point)

    expected = MapPosition(window._current_x, window._current_y, window._current_z)
    assert window._editor_context.session.document.is_dirty is True
    assert window._editor_context.session.editor.map_model.get_tile(
        expected
    ) == TileState(position=expected, ground_item_id=1)
    assert window._view_tabs.tabText(0) == "Untitled*"
    assert window.windowTitle() == f"Untitled* - {__app_name__} v{__version__}"
    assert (
        window.statusBar().currentMessage()
        == f"Applied Draw tool at {expected.x}, {expected.y}, {expected.z:02d}."
    )
    assert (
        f"tool applied: drawing @ {expected.x},{expected.y},{expected.z:02d}"
        in window._canvas.diagnostic_text()
    )


def test_renderer_host_canvas_return_key_applies_selection_tool(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "renderer-host-canvas-select.ini"),
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is False
    window.brush_mode_actions["selection"].trigger()
    window._canvas.setFocus()

    QTest.keyClick(window._canvas, Qt.Key.Key_Return)

    assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is True
    assert window.statusBar().currentMessage() == "Applied Select tool at 32000, 32000, 07."
    assert "tool applied: selection @ 32000,32000,07" in window._canvas.diagnostic_text()


def test_placeholder_canvas_left_click_applies_draw_tool_and_refreshes_shell(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-draw.ini"),
        canvas_factory=PlaceholderCanvasWidget,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_active_item_selection("Stone", 1)
    point = QPoint(0, 0)

    QTest.mouseClick(window._canvas, Qt.MouseButton.LeftButton, pos=point)

    expected = MapPosition(window._current_x, window._current_y, window._current_z)
    assert window._editor_context.session.document.is_dirty is True
    assert window._editor_context.session.editor.map_model.get_tile(
        expected
    ) == TileState(position=expected, ground_item_id=1)
    assert window._view_tabs.tabText(0) == "Untitled*"
    assert window.windowTitle() == f"Untitled* - {__app_name__} v{__version__}"
    assert (
        window.statusBar().currentMessage()
        == f"Applied Draw tool at {expected.x}, {expected.y}, {expected.z:02d}."
    )
    assert f"tool applied: drawing @ {expected.x},{expected.y},{expected.z:02d}" in (
        window._canvas.text()
    )


def test_placeholder_canvas_left_click_applies_selection_tool(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-select.ini"),
        canvas_factory=PlaceholderCanvasWidget,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is False
    window.brush_mode_actions["selection"].trigger()
    point = QPoint(0, 0)

    QTest.mouseClick(window._canvas, Qt.MouseButton.LeftButton, pos=point)

    expected = MapPosition(window._current_x, window._current_y, window._current_z)
    assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is True
    assert (
        window.statusBar().currentMessage()
        == f"Applied Select tool at {expected.x}, {expected.y}, {expected.z:02d}."
    )
    assert f"tool applied: selection @ {expected.x},{expected.y},{expected.z:02d}" in (
        window._canvas.text()
    )


def test_placeholder_canvas_space_key_applies_draw_tool(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-space.ini"),
        canvas_factory=PlaceholderCanvasWidget,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._set_active_item_selection("Stone", 1)
    window._canvas.setFocus()

    QTest.keyClick(window._canvas, Qt.Key.Key_Space)

    assert window._editor_context.session.document.is_dirty is True
    assert window._editor_context.session.editor.map_model.get_tile(
        MapPosition(32000, 32000, 7)
    ) == TileState(position=MapPosition(32000, 32000, 7), ground_item_id=1)
    assert window.statusBar().currentMessage() == "Applied Draw tool at 32000, 32000, 07."
    assert "tool applied: drawing @ 32000,32000,07" in window._canvas.text()


def test_placeholder_canvas_return_key_applies_selection_tool(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-return.ini"),
        canvas_factory=PlaceholderCanvasWidget,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is False
    window.brush_mode_actions["selection"].trigger()
    window._canvas.setFocus()

    QTest.keyClick(window._canvas, Qt.Key.Key_Return)

    assert window.selection_menu_actions["replace_on_selection_items"].isEnabled() is True
    assert window.statusBar().currentMessage() == "Applied Select tool at 32000, 32000, 07."
    assert "tool applied: selection @ 32000,32000,07" in window._canvas.text()


def test_placeholder_canvas_click_can_translate_widget_point_to_map_position(
    qtbot,
    settings_workspace: Path,
) -> None:
    class _PointMappedPlaceholderCanvas(PlaceholderCanvasWidget):
        def map_position_for_point(self, point: QPoint) -> MapPosition:
            return MapPosition(32000 + point.x(), 32000 + point.y(), 6)

    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-point-map.ini"),
        canvas_factory=_PointMappedPlaceholderCanvas,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert implements_editor_tool_callback_canvas_protocol(window._canvas)
    assert implements_editor_point_mapping_canvas_protocol(window._canvas)
    window._set_active_item_selection("Stone", 1)

    QTest.mouseClick(window._canvas, Qt.MouseButton.LeftButton, pos=QPoint(10, 15))

    assert window._coord_label.text() == "Pos: (X: 32010, Y: 32015, Z: 06)"
    assert window._editor_context.session.editor.map_model.get_tile(
        MapPosition(32010, 32015, 6)
    ) == TileState(position=MapPosition(32010, 32015, 6), ground_item_id=1)
    assert window.statusBar().currentMessage() == "Applied Draw tool at 32010, 32015, 06."
    assert "tool applied: drawing @ 32010,32015,06" in window._canvas.text()


def test_placeholder_canvas_uses_viewport_math_for_default_point_mapping(
    qtbot,
    settings_workspace: Path,
) -> None:
    window = MainWindow(
        settings=_build_settings(settings_workspace, "placeholder-canvas-viewport-map.ini"),
        canvas_factory=PlaceholderCanvasWidget,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    window._canvas.resize(640, 480)
    window._set_current_position(32000, 32100, 7)
    window._set_active_item_selection("Stone", 1)
    qtbot.wait(1)

    QTest.mouseClick(window._canvas, Qt.MouseButton.LeftButton, pos=QPoint(0, 0))

    assert (window._current_x, window._current_y, window._current_z) != (32000, 32100, 7)
    assert window._editor_context.session.editor.map_model.get_tile(
        MapPosition(window._current_x, window._current_y, window._current_z)
    ) == TileState(
        position=MapPosition(window._current_x, window._current_y, window._current_z),
        ground_item_id=1,
    )
    assert window.statusBar().currentMessage().startswith("Applied Draw tool at ")


def test_non_placeholder_canvas_click_can_report_mapped_target_position(
    qtbot,
    settings_workspace: Path,
) -> None:
    class _InteractiveCanvasWidget(_FakeCanvasWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._tool_applied_callback = None

        def set_tool_applied_callback(self, callback) -> None:
            self._tool_applied_callback = callback

        def map_position_for_point(self, point: QPoint) -> MapPosition:
            return MapPosition(32000 + point.x(), 32000 + point.y(), 4)

        def mousePressEvent(self, event) -> None:  # noqa: N802
            if event.button() == Qt.MouseButton.LeftButton:
                assert self.editor_context is not None
                target = self.map_position_for_point(event.pos())
                self.apply_count += 1
                result = EditorToolApplyResult(
                    changed=self.editor_context.session.editor.apply_active_tool_at(target),
                    position=target,
                )
                if self._tool_applied_callback is not None:
                    self._tool_applied_callback(result)
                event.accept()
                return
            super().mousePressEvent(event)

    holder: dict[str, _InteractiveCanvasWidget] = {}

    def _canvas_factory(parent: QWidget | None = None) -> _InteractiveCanvasWidget:
        canvas = _InteractiveCanvasWidget(parent)
        holder["canvas"] = canvas
        return canvas

    window = MainWindow(
        settings=_build_settings(settings_workspace, "interactive-canvas-point-map.ini"),
        canvas_factory=_canvas_factory,
        enable_docks=False,
    )
    qtbot.addWidget(window)

    assert implements_editor_tool_callback_canvas_protocol(holder["canvas"])
    assert implements_editor_point_mapping_canvas_protocol(holder["canvas"])
    window._set_active_item_selection("Stone", 1)

    QTest.mouseClick(window._canvas, Qt.MouseButton.LeftButton, pos=QPoint(12, 18))

    assert holder["canvas"].apply_count == 1
    assert window._coord_label.text() == "Pos: (X: 32012, Y: 32018, Z: 04)"
    assert window._editor_context.session.editor.map_model.get_tile(
        MapPosition(32012, 32018, 4)
    ) == TileState(position=MapPosition(32012, 32018, 4), ground_item_id=1)
    assert window.statusBar().currentMessage() == "Applied Draw tool at 32012, 32018, 04."


def test_placeholder_canvas_uses_shell_core_bridge_for_state_summary(
    qtbot,
    monkeypatch,
) -> None:
    class _FakeShellCore:
        def __init__(self) -> None:
            self._position = (32000, 32000, 7)
            self._zoom = 100
            self._show_grid = False
            self._ghost_higher = False
            self._show_lower = True

        def is_native(self) -> bool:
            return True

        def set_position(self, x: int, y: int, z: int) -> tuple[int, int, int]:
            self._position = (x, y, z)
            return self._position

        def position(self) -> tuple[int, int, int]:
            return self._position

        def set_floor(self, z: int) -> int:
            self._position = (self._position[0], self._position[1], z)
            return z

        def set_zoom_percent(self, percent: int) -> int:
            self._zoom = percent
            return self._zoom

        def set_show_grid(self, enabled: bool) -> bool:
            self._show_grid = enabled
            return self._show_grid

        def set_ghost_higher(self, enabled: bool) -> bool:
            self._ghost_higher = enabled
            return self._ghost_higher

        def set_show_lower(self, enabled: bool) -> bool:
            self._show_lower = enabled
            return self._show_lower

        def set_view_flag(self, name: str, enabled: bool) -> bool:
            del name, enabled
            return True

        def set_show_flag(self, name: str, enabled: bool) -> bool:
            del name, enabled
            return True

        def render_summary(self) -> str:
            return (
                f"zoom={self._zoom}%"
                f" grid={'on' if self._show_grid else 'off'}"
                f" ghost_higher={'on' if self._ghost_higher else 'off'}"
                f" show_lower={'on' if self._show_lower else 'off'}"
            )

    monkeypatch.setattr("pyrme.ui.canvas_host.create_editor_shell_state", _FakeShellCore)

    canvas = PlaceholderCanvasWidget()
    qtbot.addWidget(canvas)

    canvas.set_position(32100, 32150, 5)
    canvas.set_zoom(125)
    canvas.set_show_grid(True)
    canvas.set_ghost_higher(True)
    canvas.set_show_lower(False)

    text = canvas.text()
    assert "Core Mode: native" in text
    assert "Position: 32100, 32150, 05" in text
    assert "Floor: 05 | Zoom: 125%" in text
    assert "Shell State: zoom=125% grid=on ghost_higher=on show_lower=off" in text
