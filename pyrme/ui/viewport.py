"""Viewport state owner for editor canvas views."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

TILE_SIZE = 32
GROUND_LAYER = 7
MIN_MAP_COORD = 0
MAX_MAP_COORD = 65000
MIN_FLOOR = 0
MAX_FLOOR = 15
MIN_ZOOM_PERCENT = 10
MAX_ZOOM_PERCENT = 800


@dataclass(frozen=True, slots=True)
class ViewportSnapshot:
    center_x: int = 32000
    center_y: int = 32000
    floor: int = GROUND_LAYER
    zoom_percent: int = 100
    previous_position: tuple[int, int, int] | None = None
    logical_width: int = 0
    logical_height: int = 0
    scale_factor: float = 1.0
    scroll_x: int = 0
    scroll_y: int = 0


class EditorViewport:
    """Owns map camera state independently from `MainWindow` widgets."""

    def __init__(self, snapshot: ViewportSnapshot | None = None) -> None:
        self._center_x = 32000
        self._center_y = 32000
        self._floor = GROUND_LAYER
        self._zoom_percent = 100
        self._previous_position: tuple[int, int, int] | None = None
        self._logical_width = 0
        self._logical_height = 0
        self._scale_factor = 1.0
        self._scroll_x = 0
        self._scroll_y = 0
        if snapshot is not None:
            self.restore(snapshot)

    @property
    def center_x(self) -> int:
        return self._center_x

    @property
    def center_y(self) -> int:
        return self._center_y

    @property
    def floor(self) -> int:
        return self._floor

    @property
    def center(self) -> tuple[int, int, int]:
        return (self._center_x, self._center_y, self._floor)

    @property
    def zoom_percent(self) -> int:
        return self._zoom_percent

    @property
    def previous_position(self) -> tuple[int, int, int] | None:
        return self._previous_position

    @property
    def logical_size(self) -> tuple[int, int]:
        return (self._logical_width, self._logical_height)

    @property
    def scale_factor(self) -> float:
        return self._scale_factor

    @property
    def pixel_size(self) -> tuple[int, int]:
        return (
            int(self._logical_width * self._scale_factor),
            int(self._logical_height * self._scale_factor),
        )

    @property
    def scroll_origin(self) -> tuple[int, int]:
        return (self._scroll_x, self._scroll_y)

    @property
    def legacy_zoom_scale(self) -> float:
        return 100.0 / max(MIN_ZOOM_PERCENT, self._zoom_percent)

    def set_center(
        self,
        x: int,
        y: int,
        floor: int,
        *,
        track_history: bool = False,
    ) -> None:
        next_position = (
            _clamp_int(x, MIN_MAP_COORD, MAX_MAP_COORD),
            _clamp_int(y, MIN_MAP_COORD, MAX_MAP_COORD),
            _clamp_int(floor, MIN_FLOOR, MAX_FLOOR),
        )
        current = self.center
        if track_history and next_position != current:
            self._previous_position = current
        self._center_x, self._center_y, self._floor = next_position
        self._sync_scroll_from_center()

    def set_previous_position(self, position: tuple[int, int, int] | None) -> None:
        self._previous_position = _clamp_position(position)

    def set_floor(self, floor: int) -> None:
        self._floor = _clamp_int(floor, MIN_FLOOR, MAX_FLOOR)
        self._sync_scroll_from_center()

    def set_zoom_percent(self, percent: int) -> None:
        self._zoom_percent = _clamp_int(
            percent,
            MIN_ZOOM_PERCENT,
            MAX_ZOOM_PERCENT,
        )
        self._sync_scroll_from_center()

    def set_view_size(
        self,
        logical_width: int,
        logical_height: int,
        *,
        scale_factor: float = 1.0,
    ) -> None:
        self._logical_width = max(0, int(logical_width))
        self._logical_height = max(0, int(logical_height))
        self._scale_factor = max(0.0001, float(scale_factor))
        self._sync_scroll_from_center()

    def scroll_to(self, x: int, y: int, *, centered: bool = False) -> None:
        if centered:
            self.set_center(x, y, self._floor)
            return
        self._scroll_x = max(0, int(x))
        self._scroll_y = max(0, int(y))
        self._sync_center_from_scroll()

    def scroll_relative(self, dx: int, dy: int) -> None:
        self.scroll_to(self._scroll_x + int(dx), self._scroll_y + int(dy))

    def screen_to_map(self, screen_x: int, screen_y: int) -> tuple[int, int, int]:
        scaled_x = int(int(screen_x) * self._scale_factor)
        scaled_y = int(int(screen_y) * self._scale_factor)

        if scaled_x < 0:
            map_x = _trunc_div(self._scroll_x + scaled_x, TILE_SIZE)
        else:
            map_x = int(self._scroll_x + (scaled_x * self.legacy_zoom_scale)) // TILE_SIZE

        if scaled_y < 0:
            map_y = _trunc_div(self._scroll_y + scaled_y, TILE_SIZE)
        else:
            map_y = int(self._scroll_y + (scaled_y * self.legacy_zoom_scale)) // TILE_SIZE

        offset = _floor_tile_offset(self._floor)
        return (
            _clamp_int(map_x + offset, MIN_MAP_COORD, MAX_MAP_COORD),
            _clamp_int(map_y + offset, MIN_MAP_COORD, MAX_MAP_COORD),
            self._floor,
        )

    def map_to_screen(self, map_x: int, map_y: int, map_z: int) -> tuple[int, int]:
        adjusted_x = int(map_x) - _floor_tile_offset(int(map_z))
        adjusted_y = int(map_y) - _floor_tile_offset(int(map_z))
        raw_x = float(adjusted_x * TILE_SIZE - self._scroll_x)
        raw_y = float(adjusted_y * TILE_SIZE - self._scroll_y)

        if raw_x < 0.0:
            screen_x = int(ceil(raw_x / self._scale_factor))
        else:
            screen_x = int(ceil(raw_x / (self.legacy_zoom_scale * self._scale_factor)))

        if raw_y < 0.0:
            screen_y = int(ceil(raw_y / self._scale_factor))
        else:
            screen_y = int(ceil(raw_y / (self.legacy_zoom_scale * self._scale_factor)))

        return (screen_x, screen_y)

    def visible_rect(self) -> tuple[float, float, float, float]:
        pixel_width, pixel_height = self.pixel_size
        tile_size = float(TILE_SIZE) / max(0.0001, self.legacy_zoom_scale)
        offset = _floor_tile_offset(self._floor)
        return (
            float(self._scroll_x) / TILE_SIZE + offset,
            float(self._scroll_y) / TILE_SIZE + offset,
            pixel_width / tile_size + 1.0,
            pixel_height / tile_size + 1.0,
        )

    def snapshot(self) -> ViewportSnapshot:
        return ViewportSnapshot(
            center_x=self._center_x,
            center_y=self._center_y,
            floor=self._floor,
            zoom_percent=self._zoom_percent,
            previous_position=self._previous_position,
            logical_width=self._logical_width,
            logical_height=self._logical_height,
            scale_factor=self._scale_factor,
            scroll_x=self._scroll_x,
            scroll_y=self._scroll_y,
        )

    def restore(self, snapshot: ViewportSnapshot) -> None:
        self._center_x = _clamp_int(snapshot.center_x, MIN_MAP_COORD, MAX_MAP_COORD)
        self._center_y = _clamp_int(snapshot.center_y, MIN_MAP_COORD, MAX_MAP_COORD)
        self._floor = _clamp_int(snapshot.floor, MIN_FLOOR, MAX_FLOOR)
        self._zoom_percent = _clamp_int(
            snapshot.zoom_percent,
            MIN_ZOOM_PERCENT,
            MAX_ZOOM_PERCENT,
        )
        self._previous_position = _clamp_position(snapshot.previous_position)
        self._logical_width = max(0, int(snapshot.logical_width))
        self._logical_height = max(0, int(snapshot.logical_height))
        self._scale_factor = max(0.0001, float(snapshot.scale_factor))
        self._scroll_x = max(0, int(snapshot.scroll_x))
        self._scroll_y = max(0, int(snapshot.scroll_y))

    def _sync_scroll_from_center(self) -> None:
        half_width = int(
            (self._logical_width * self._scale_factor * self.legacy_zoom_scale) / 2.0
        )
        half_height = int(
            (self._logical_height * self._scale_factor * self.legacy_zoom_scale) / 2.0
        )
        self._scroll_x = max(
            0,
            _world_tile_to_scroll_pixel(self._center_x, self._floor) - half_width,
        )
        self._scroll_y = max(
            0,
            _world_tile_to_scroll_pixel(self._center_y, self._floor) - half_height,
        )

    def _sync_center_from_scroll(self) -> None:
        half_width = int(
            (self._logical_width * self._scale_factor * self.legacy_zoom_scale) / 2.0
        )
        half_height = int(
            (self._logical_height * self._scale_factor * self.legacy_zoom_scale) / 2.0
        )
        floor_offset = _floor_tile_offset(self._floor)
        self._center_x = _clamp_int(
            int((self._scroll_x + half_width) / TILE_SIZE) + floor_offset,
            MIN_MAP_COORD,
            MAX_MAP_COORD,
        )
        self._center_y = _clamp_int(
            int((self._scroll_y + half_height) / TILE_SIZE) + floor_offset,
            MIN_MAP_COORD,
            MAX_MAP_COORD,
        )


def _floor_tile_offset(floor: int) -> int:
    if floor <= GROUND_LAYER:
        return GROUND_LAYER - floor
    return 0


def _world_tile_to_scroll_pixel(tile: int, floor: int) -> int:
    return (tile - _floor_tile_offset(floor)) * TILE_SIZE


def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, int(value)))


def _clamp_position(position: tuple[int, int, int] | None) -> tuple[int, int, int] | None:
    if position is None:
        return None
    x, y, floor = position
    return (
        _clamp_int(x, MIN_MAP_COORD, MAX_MAP_COORD),
        _clamp_int(y, MIN_MAP_COORD, MAX_MAP_COORD),
        _clamp_int(floor, MIN_FLOOR, MAX_FLOOR),
    )


def _trunc_div(value: int, divisor: int) -> int:
    return int(value / divisor)
