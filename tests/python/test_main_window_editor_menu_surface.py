from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from pyrme.ui.legacy_menu_contract import (
    EDITOR_ACTION_ORDER,
    EDITOR_ACTIONS,
    EDITOR_ZOOM_ACTION_ORDER,
    EDITOR_ZOOM_MENU_TITLE,
)
from pyrme.ui.main_window import MainWindow


class _FakeCanvasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.zoom_percent: int | None = None

    def set_position(self, x: int, y: int, z: int) -> None:
        pass

    def set_floor(self, z: int) -> None:
        pass

    def set_zoom(self, percent: int) -> None:
        self.zoom_percent = percent

    def set_show_grid(self, enabled: bool) -> None:
        pass

    def set_ghost_higher(self, enabled: bool) -> None:
        pass

    def set_show_lower(self, enabled: bool) -> None:
        pass


def _menus_by_title(window: MainWindow):
    menu_bar = window.menuBar()
    assert menu_bar is not None
    menus = {}
    for action in menu_bar.actions():
        menu = action.menu()
        if menu is not None:
            menus[action.text().replace("&", "")] = menu
    return menus


def test_main_window_exposes_editor_menu_surface_from_contract(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    menus = _menus_by_title(window)
    editor_menu = menus["Editor"]

    top_level_items = [action.text() for action in editor_menu.actions() if action.text()]
    assert top_level_items[:3] == [
        EDITOR_ACTIONS[action_key].text for action_key in EDITOR_ACTION_ORDER
    ]

    zoom_menu_action = next(
        action for action in editor_menu.actions() if action.menu() is not None
    )
    assert zoom_menu_action.text() == EDITOR_ZOOM_MENU_TITLE
    zoom_menu = zoom_menu_action.menu()
    assert zoom_menu is not None
    assert [action.text() for action in zoom_menu.actions()] == [
        EDITOR_ACTIONS[action_key].text for action_key in EDITOR_ZOOM_ACTION_ORDER
    ]

    for action_key in (*EDITOR_ACTION_ORDER, *EDITOR_ZOOM_ACTION_ORDER):
        spec = EDITOR_ACTIONS[action_key]
        menu = editor_menu if len(spec.menu_path) == 1 else zoom_menu
        action = next(action for action in menu.actions() if action.text() == spec.text)
        assert action.objectName() == f"action_{spec.action_id}"
        assert action.shortcut().toString() == (spec.shortcut or "")
        assert action.statusTip() == (spec.status_tip or "")


def test_main_window_editor_remaining_stub_is_safe(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    status_bar = window.statusBar()
    assert status_bar is not None

    assert not window.isFullScreen()
    assert window._zoom_percent == 100
    assert window._view_tabs.count() == 1
    assert not hasattr(window, "_last_screenshot")

    window.take_screenshot_action.trigger()
    assert status_bar.currentMessage() == "Take Screenshot is not available yet."
    assert not hasattr(window, "_last_screenshot")


def test_main_window_editor_zoom_actions_drive_shell_zoom_state(qtbot) -> None:
    holder: dict[str, _FakeCanvasWidget] = {}

    def _canvas_factory(parent: QWidget | None = None) -> _FakeCanvasWidget:
        canvas = _FakeCanvasWidget(parent)
        holder["canvas"] = canvas
        return canvas

    window = MainWindow(canvas_factory=_canvas_factory)
    qtbot.addWidget(window)
    status_bar = window.statusBar()
    assert status_bar is not None

    canvas = holder["canvas"]
    assert window._zoom_percent == 100
    assert window._zoom_label.text() == "100%"
    assert canvas.zoom_percent == 100

    window.zoom_in_action.trigger()
    assert window._zoom_percent == 110
    assert window._zoom_label.text() == "110%"
    assert canvas.zoom_percent == 110
    assert status_bar.currentMessage() == "Zoom set to 110%"

    window.zoom_out_action.trigger()
    assert window._zoom_percent == 100
    assert window._zoom_label.text() == "100%"
    assert canvas.zoom_percent == 100
    assert status_bar.currentMessage() == "Zoom set to 100%"

    window.zoom_normal_action.trigger()
    assert window._zoom_percent == 100
    assert window._zoom_label.text() == "100%"
    assert canvas.zoom_percent == 100
    assert status_bar.currentMessage() == "Zoom reset to 100%"


def test_main_window_editor_fullscreen_action_toggles_window_mode(qtbot) -> None:
    window = MainWindow(enable_docks=False)
    qtbot.addWidget(window)
    status_bar = window.statusBar()
    assert status_bar is not None

    window.show()
    qtbot.waitExposed(window)
    assert not window.isFullScreen()

    window.toggle_fullscreen_action.trigger()
    qtbot.waitUntil(window.isFullScreen)
    assert status_bar.currentMessage() == "Entered fullscreen mode."

    window.toggle_fullscreen_action.trigger()
    qtbot.waitUntil(lambda: not window.isFullScreen())
    assert status_bar.currentMessage() == "Exited fullscreen mode."
