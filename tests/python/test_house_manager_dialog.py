from __future__ import annotations

from types import SimpleNamespace

from PyQt6.QtWidgets import QWidget

from pyrme.ui.dialogs.house_manager import HouseManagerDialog


class _EditorWithoutHouseBackend:
    def get_towns(self) -> list[tuple[int, str, int, int, int]]:
        return []


class _HouseManagerParent(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._editor_context = SimpleNamespace(
            session=SimpleNamespace(editor=_EditorWithoutHouseBackend())
        )
        self.jumped_to: tuple[int, int, int] | None = None

    def _set_current_position(self, x: int, y: int, z: int) -> None:
        self.jumped_to = (x, y, z)


def test_house_manager_opens_without_house_backend(qtbot) -> None:
    parent = _HouseManagerParent()
    qtbot.addWidget(parent)

    dialog = HouseManagerDialog(parent)
    qtbot.addWidget(dialog)

    assert dialog.house_list.count() == 0
    assert dialog.add_btn.isEnabled() is False
    assert dialog.remove_btn.isEnabled() is False
    assert dialog.name_edit.isEnabled() is False
