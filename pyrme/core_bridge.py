"""Bridge between the Python shell and the optional native Rust core."""

from __future__ import annotations

from dataclasses import dataclass, field
from os import cpu_count
from typing import Any

VIEW_FLAG_DEFAULTS: dict[str, bool] = {
    "show_all_floors": False,
    "show_as_minimap": False,
    "show_only_colors": False,
    "show_only_modified": False,
    "always_show_zones": False,
    "extended_house_shader": False,
    "show_tooltips": False,
    "show_client_box": False,
    "ghost_loose_items": False,
    "show_shade": False,
}

SHOW_FLAG_DEFAULTS: dict[str, bool] = {
    "show_animation": False,
    "show_light": False,
    "show_light_strength": False,
    "show_technical_items": False,
    "show_invalid_tiles": False,
    "show_invalid_zones": False,
    "show_creatures": False,
    "show_spawns": False,
    "show_special": False,
    "show_houses": False,
    "show_pathing": False,
    "show_towns": False,
    "show_waypoints": False,
    "highlight_items": False,
    "highlight_locked_doors": False,
    "show_wall_hooks": False,
}


def _recommended_worker_threads() -> int:
    detected = cpu_count() or 1
    return max(1, min(16, detected))


@dataclass
class _FallbackEditorShellState:
    _position: tuple[int, int, int] = (32000, 32000, 7)
    _zoom_percent: int = 100
    _show_grid: bool = False
    _ghost_higher: bool = False
    _show_lower: bool = True
    _view_flags: dict[str, bool] = field(
        default_factory=lambda: dict(VIEW_FLAG_DEFAULTS)
    )
    _show_flags: dict[str, bool] = field(
        default_factory=lambda: dict(SHOW_FLAG_DEFAULTS)
    )
    _waypoints: list[tuple[str, int, int, int]] = field(default_factory=list)
    _houses: list[tuple[int, str, int, int, bool, int, int, int]] = field(
        default_factory=list
    )

    def position(self) -> tuple[int, int, int]:
        return self._position

    def set_position(self, x: int, y: int, z: int) -> tuple[int, int, int]:
        self._position = (
            max(0, min(65000, int(x))),
            max(0, min(65000, int(y))),
            max(0, min(15, int(z))),
        )
        return self._position

    def floor(self) -> int:
        return self._position[2]

    def set_floor(self, z: int) -> int:
        self._position = (self._position[0], self._position[1], max(0, min(15, int(z))))
        return self._position[2]

    def zoom_percent(self) -> int:
        return self._zoom_percent

    def set_zoom_percent(self, percent: int) -> int:
        self._zoom_percent = max(10, min(800, int(percent)))
        return self._zoom_percent

    def show_grid(self) -> bool:
        return self._show_grid

    def set_show_grid(self, enabled: bool) -> bool:
        self._show_grid = bool(enabled)
        return self._show_grid

    def ghost_higher(self) -> bool:
        return self._ghost_higher

    def set_ghost_higher(self, enabled: bool) -> bool:
        self._ghost_higher = bool(enabled)
        return self._ghost_higher

    def show_lower(self) -> bool:
        return self._show_lower

    def set_show_lower(self, enabled: bool) -> bool:
        self._show_lower = bool(enabled)
        return self._show_lower

    def set_view_flag(self, name: str, enabled: bool) -> bool:
        if name not in self._view_flags:
            raise ValueError(f"unknown view flag: {name}")
        self._view_flags[name] = bool(enabled)
        return self._view_flags[name]

    def view_flag(self, name: str) -> bool:
        if name not in self._view_flags:
            raise ValueError(f"unknown view flag: {name}")
        return self._view_flags[name]

    def view_flags(self) -> dict[str, bool]:
        return dict(self._view_flags)

    def set_show_flag(self, name: str, enabled: bool) -> bool:
        if name not in self._show_flags:
            raise ValueError(f"unknown show flag: {name}")
        self._show_flags[name] = bool(enabled)
        return self._show_flags[name]

    def show_flag(self, name: str) -> bool:
        if name not in self._show_flags:
            raise ValueError(f"unknown show flag: {name}")
        return self._show_flags[name]

    def show_flags(self) -> dict[str, bool]:
        return dict(self._show_flags)

    def recommended_worker_threads(self) -> int:
        return _recommended_worker_threads()

    def render_summary(self) -> str:
        return (
            f"zoom={self._zoom_percent}%"
            f" grid={'on' if self._show_grid else 'off'}"
            f" ghost_higher={'on' if self._ghost_higher else 'off'}"
            f" show_lower={'on' if self._show_lower else 'off'}"
            f" worker_threads={self.recommended_worker_threads()}"
        )

    def collect_statistics(self) -> Any:
        return None

    def towns(self) -> list[tuple[int, str, int, int, int]]:
        return []

    def add_town(self, id: int, name: str, x: int, y: int, z: int) -> None:
        pass

    def remove_town(self, id: int) -> bool:
        return False

    def get_waypoints(self) -> list[tuple[str, int, int, int]]:
        return list(self._waypoints)

    def add_waypoint(self, name: str, x: int, y: int, z: int) -> bool:
        self._waypoints.append((name, *self._clamp_position(x, y, z)))
        return True

    def update_waypoint(self, index: int, name: str, x: int, y: int, z: int) -> bool:
        if index < 0 or index >= len(self._waypoints):
            return False
        self._waypoints[index] = (name, *self._clamp_position(x, y, z))
        return True

    def remove_waypoint(self, index: int) -> bool:
        if index < 0 or index >= len(self._waypoints):
            return False
        self._waypoints.pop(index)
        return True

    def get_houses(self) -> list[tuple[int, str, int, int, bool, int, int, int]]:
        return list(self._houses)

    def add_house(
        self,
        houseid: int,
        name: str,
        entryx: int,
        entryy: int,
        entryz: int,
        rent: int,
        townid: int,
        guildhall: bool,
        size: int,
    ) -> bool:
        del size
        if any(existing[0] == houseid for existing in self._houses):
            return False
        x, y, z = self._clamp_position(entryx, entryy, entryz)
        self._houses.append((houseid, name, townid, rent, guildhall, x, y, z))
        return True

    def update_house(
        self,
        houseid: int,
        name: str,
        townid: int,
        rent: int,
        guildhall: bool,
        entryx: int,
        entryy: int,
        entryz: int,
    ) -> bool:
        for index, existing in enumerate(self._houses):
            if existing[0] == houseid:
                x, y, z = self._clamp_position(entryx, entryy, entryz)
                self._houses[index] = (houseid, name, townid, rent, guildhall, x, y, z)
                return True
        return False

    def remove_house(self, houseid: int) -> bool:
        for index, existing in enumerate(self._houses):
            if existing[0] == houseid:
                self._houses.pop(index)
                return True
        return False

    @staticmethod
    def _clamp_position(x: int, y: int, z: int) -> tuple[int, int, int]:
        return (
            max(0, min(65000, int(x))),
            max(0, min(65000, int(y))),
            max(0, min(15, int(z))),
        )


class EditorShellCoreBridge:
    """Stable Python-facing adapter over the optional native extension."""

    def __init__(self, inner: Any, *, native: bool) -> None:
        self._inner = inner
        self._native = native

    def is_native(self) -> bool:
        return self._native

    def position(self) -> tuple[int, int, int]:
        return tuple(self._inner.position())

    def set_position(self, x: int, y: int, z: int) -> tuple[int, int, int]:
        return tuple(self._inner.set_position(x, y, z))

    def floor(self) -> int:
        return int(self._inner.floor())

    def set_floor(self, z: int) -> int:
        return int(self._inner.set_floor(z))

    def zoom_percent(self) -> int:
        return int(self._inner.zoom_percent())

    def set_zoom_percent(self, percent: int) -> int:
        return int(self._inner.set_zoom_percent(percent))

    def show_grid(self) -> bool:
        return bool(self._inner.show_grid())

    def set_show_grid(self, enabled: bool) -> bool:
        return bool(self._inner.set_show_grid(enabled))

    def ghost_higher(self) -> bool:
        return bool(self._inner.ghost_higher())

    def set_ghost_higher(self, enabled: bool) -> bool:
        return bool(self._inner.set_ghost_higher(enabled))

    def show_lower(self) -> bool:
        return bool(self._inner.show_lower())

    def set_show_lower(self, enabled: bool) -> bool:
        return bool(self._inner.set_show_lower(enabled))

    def set_view_flag(self, name: str, enabled: bool) -> bool:
        return bool(self._inner.set_view_flag(name, enabled))

    def view_flag(self, name: str) -> bool:
        return bool(self._inner.view_flag(name))

    def view_flags(self) -> dict[str, bool]:
        return dict(self._inner.view_flags())

    def set_show_flag(self, name: str, enabled: bool) -> bool:
        return bool(self._inner.set_show_flag(name, enabled))

    def show_flag(self, name: str) -> bool:
        return bool(self._inner.show_flag(name))

    def show_flags(self) -> dict[str, bool]:
        return dict(self._inner.show_flags())

    def recommended_worker_threads(self) -> int:
        return int(self._inner.recommended_worker_threads())

    def render_summary(self) -> str:
        return str(self._inner.render_summary())

    def collect_statistics(self) -> Any:
        if hasattr(self._inner, "collect_statistics"):
            return self._inner.collect_statistics()
        return None

    def towns(self) -> list[tuple[int, str, int, int, int]]:
        if hasattr(self._inner, "towns"):
            return list(self._inner.towns())
        return []

    def add_town(self, id: int, name: str, x: int, y: int, z: int) -> None:
        if hasattr(self._inner, "add_town"):
            self._inner.add_town(id, name, x, y, z)

    def remove_town(self, id: int) -> bool:
        if hasattr(self._inner, "remove_town"):
            return bool(self._inner.remove_town(id))
        return False

    def get_towns(self) -> list[tuple[int, str, int, int, int]]:
        return self.towns()

    def get_waypoints(self) -> list[tuple[str, int, int, int]]:
        if hasattr(self._inner, "get_waypoints"):
            return [
                (str(name), int(x), int(y), int(z))
                for name, x, y, z in self._inner.get_waypoints()
            ]
        return []

    def add_waypoint(self, name: str, x: int, y: int, z: int) -> bool:
        if hasattr(self._inner, "add_waypoint"):
            return bool(self._inner.add_waypoint(name, x, y, z))
        return False

    def update_waypoint(self, index: int, name: str, x: int, y: int, z: int) -> bool:
        if hasattr(self._inner, "update_waypoint"):
            return bool(self._inner.update_waypoint(index, name, x, y, z))
        return False

    def remove_waypoint(self, index: int) -> bool:
        if hasattr(self._inner, "remove_waypoint"):
            return bool(self._inner.remove_waypoint(index))
        return False

    def get_houses(self) -> list[tuple[int, str, int, int, bool, int, int, int]]:
        if hasattr(self._inner, "get_houses"):
            return [
                (
                    int(houseid),
                    str(name),
                    int(townid),
                    int(rent),
                    bool(guildhall),
                    int(entryx),
                    int(entryy),
                    int(entryz),
                )
                for (
                    houseid,
                    name,
                    townid,
                    rent,
                    guildhall,
                    entryx,
                    entryy,
                    entryz,
                ) in self._inner.get_houses()
            ]
        return []

    def add_house(
        self,
        houseid: int,
        name: str,
        townid: int,
        entryx: int = 32000,
        entryy: int = 32000,
        entryz: int = 7,
        rent: int = 0,
        guildhall: bool = False,
        size: int = 0,
    ) -> bool:
        if hasattr(self._inner, "add_house"):
            return bool(
                self._inner.add_house(
                    houseid, name, entryx, entryy, entryz, rent, townid, guildhall, size
                )
            )
        return False

    def update_house(
        self,
        houseid: int,
        name: str,
        townid: int,
        rent: int,
        guildhall: bool,
        entryx: int,
        entryy: int,
        entryz: int,
    ) -> bool:
        if hasattr(self._inner, "update_house"):
            return bool(
                self._inner.update_house(
                    houseid, name, townid, rent, guildhall, entryx, entryy, entryz
                )
            )
        return False

    def remove_house(self, houseid: int) -> bool:
        if hasattr(self._inner, "remove_house"):
            return bool(self._inner.remove_house(houseid))
        return False


def create_editor_shell_state() -> EditorShellCoreBridge:
    """Create a native-backed shell state when available, else use Python fallback."""

    try:
        from pyrme import rme_core  # type: ignore[attr-defined]
    except ImportError:
        return EditorShellCoreBridge(_FallbackEditorShellState(), native=False)

    if hasattr(rme_core, "EditorShellState"):
        return EditorShellCoreBridge(rme_core.EditorShellState(), native=True)

    return EditorShellCoreBridge(_FallbackEditorShellState(), native=False)
