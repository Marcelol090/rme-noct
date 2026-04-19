from __future__ import annotations

from dataclasses import dataclass, field

MAX_MAP_COORDINATE = 65535
FLOOR_COUNT = 16
VALID_EDITOR_MODES = ("selection", "drawing", "erasing", "fill", "move")


@dataclass(frozen=True, order=True, slots=True)
class MapPosition:
    x: int
    y: int
    z: int

    def __post_init__(self) -> None:
        if not 0 <= self.x <= MAX_MAP_COORDINATE:
            raise ValueError(f"x must be between 0 and {MAX_MAP_COORDINATE}")
        if not 0 <= self.y <= MAX_MAP_COORDINATE:
            raise ValueError(f"y must be between 0 and {MAX_MAP_COORDINATE}")
        if not 0 <= self.z < FLOOR_COUNT:
            raise ValueError(f"z must be between 0 and {FLOOR_COUNT - 1}")


@dataclass(frozen=True, slots=True)
class TileState:
    position: MapPosition
    ground_item_id: int | None = None
    item_ids: tuple[int, ...] = ()


@dataclass(slots=True)
class MapModel:
    """Sparse shared map model owned by the editor session."""

    name: str = "Untitled"
    is_dirty: bool = False
    generation: int = 0
    _tiles: dict[MapPosition, TileState] = field(default_factory=dict, repr=False)

    def tile_count(self) -> int:
        return len(self._tiles)

    def get_tile(self, position: MapPosition) -> TileState | None:
        return self._tiles.get(position)

    def tiles(self) -> tuple[TileState, ...]:
        return tuple(self._tiles[position] for position in sorted(self._tiles))

    def set_tile(self, tile: TileState) -> None:
        self._tiles[tile.position] = tile
        self.mark_changed()

    def remove_tile(self, position: MapPosition) -> None:
        if position in self._tiles:
            del self._tiles[position]
            self.mark_changed()

    def mark_changed(self) -> None:
        self.is_dirty = True
        self.generation += 1

    def clear_changed(self) -> None:
        self.is_dirty = False


@dataclass(slots=True)
class EditorModel:
    """Minimal editor backend owner for shared map and selection state."""

    map_model: MapModel = field(default_factory=MapModel)
    selection_positions: set[MapPosition] = field(default_factory=set)
    secondary_map: MapModel | None = None
    _mode: str = "drawing"
    _active_brush_id: str | None = None
    _active_item_id: int | None = None

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        self._mode = value if value in VALID_EDITOR_MODES else "drawing"

    @property
    def active_brush_id(self) -> str | None:
        return self._active_brush_id

    @active_brush_id.setter
    def active_brush_id(self, value: str | None) -> None:
        self._active_brush_id = value

    @property
    def active_item_id(self) -> int | None:
        return self._active_item_id

    @active_item_id.setter
    def active_item_id(self, value: int | None) -> None:
        self._active_item_id = value

    def set_mode(self, value: str) -> None:
        self.mode = value

    def activate_palette_brush(self, palette_name: str) -> None:
        self._active_brush_id = f"palette:{palette_name.casefold()}"
        self._active_item_id = None

    def activate_item_brush(self, item_id: int) -> None:
        self._active_brush_id = f"item:{item_id}"
        self._active_item_id = item_id

    def clear_active_brush(self) -> None:
        self._active_brush_id = None
        self._active_item_id = None

    def apply_active_tool_at(self, position: MapPosition) -> bool:
        if self.mode == "selection":
            size_before = len(self.selection_positions)
            self.select_position(position)
            return len(self.selection_positions) != size_before

        if self.mode == "drawing":
            if self.active_item_id is None:
                return False
            existing = self.map_model.get_tile(position)
            next_tile = TileState(
                position=position,
                ground_item_id=self.active_item_id,
                item_ids=existing.item_ids if existing is not None else (),
            )
            if existing == next_tile:
                return False
            self.map_model.set_tile(next_tile)
            return True

        if self.mode == "erasing":
            if self.map_model.get_tile(position) is None:
                return False
            self.map_model.remove_tile(position)
            return True

        return False

    def has_selection(self) -> bool:
        return bool(self.selection_positions)

    def select_position(self, position: MapPosition) -> None:
        self.selection_positions.add(position)

    def clear_selection(self) -> None:
        self.selection_positions.clear()
