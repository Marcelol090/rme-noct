from __future__ import annotations

from types import SimpleNamespace

from PyQt6.QtWidgets import QWidget

from pyrme.ui.dialogs.house_manager import HouseManagerDialog


class _EditorWithoutHouseBackend:
    def get_towns(self) -> list[tuple[int, str, int, int, int]]:
        return []


class _EditorWithHouseBackend:
    def __init__(self) -> None:
        self.houses: list[tuple[int, str, int, int, bool, int, int, int]] = [
            (1, "Temple", 0, 0, False, 100, 200, 7)
        ]

    def get_towns(self) -> list[tuple[int, str, int, int, int]]:
        return [(3, "Thais", 32369, 32241, 7)]

    def get_houses(self) -> list[tuple[int, str, int, int, bool, int, int, int]]:
        return list(self.houses)

    def add_house(self, house_id: int, name: str, town_id: int) -> bool:
        self.houses.append((house_id, name, town_id, 0, False, 32000, 32000, 7))
        return True

    def update_house(
        self,
        house_id: int,
        name: str,
        town_id: int,
        rent: int,
        is_guildhall: bool,
        x: int,
        y: int,
        z: int,
    ) -> bool:
        for index, house in enumerate(self.houses):
            if house[0] == house_id:
                self.houses[index] = (house_id, name, town_id, rent, is_guildhall, x, y, z)
                return True
        return False

    def remove_house(self, house_id: int) -> bool:
        for index, house in enumerate(self.houses):
            if house[0] == house_id:
                self.houses.pop(index)
                return True
        return False


class _HouseManagerParent(QWidget):
    def __init__(self, editor: object | None = None) -> None:
        super().__init__()
        self._editor_context = SimpleNamespace(
            session=SimpleNamespace(editor=editor or _EditorWithoutHouseBackend())
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


def test_house_manager_uses_house_backend(qtbot) -> None:
    editor = _EditorWithHouseBackend()
    parent = _HouseManagerParent(editor)
    qtbot.addWidget(parent)

    dialog = HouseManagerDialog(parent)
    qtbot.addWidget(dialog)

    assert dialog.house_list.count() == 1
    assert dialog.add_btn.isEnabled() is True

    first_item = dialog.house_list.item(0)
    assert first_item is not None
    dialog.house_list.setCurrentItem(first_item)
    assert dialog.name_edit.text() == "Temple"
    assert dialog.remove_btn.isEnabled() is True

    dialog.name_edit.setText("Temple Updated")
    assert editor.houses[0][1] == "Temple Updated"

    dialog._on_add_house()
    assert editor.houses[-1][0] == 2

    dialog._on_remove_house()
    assert [house[0] for house in editor.houses] == [1]
