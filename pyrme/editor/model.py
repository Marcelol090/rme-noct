from __future__ import annotations

from dataclasses import dataclass, field, replace

DEFAULT_MAP_VERSION = "OTServ 0.6.1"
DEFAULT_CLIENT_VERSION = "10.98"
DEFAULT_MAP_WIDTH = 256
DEFAULT_MAP_HEIGHT = 256
MAX_MAP_COORDINATE = 65535
FLOOR_COUNT = 16


@dataclass(slots=True)
class MapPropertiesState:
    """Metadata persisted on the active map document."""

    description: str = ""
    map_version: str = DEFAULT_MAP_VERSION
    client_version: str = DEFAULT_CLIENT_VERSION
    width: int = DEFAULT_MAP_WIDTH
    height: int = DEFAULT_MAP_HEIGHT
    house_file: str = ""
    spawn_file: str = ""
    waypoint_file: str = ""


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
    """Sparse map model matching the shared map owned by legacy Editor."""

    name: str = "Untitled"
    filename: str = ""
    properties: MapPropertiesState = field(default_factory=MapPropertiesState)
    is_dirty: bool = False
    generation: int = 0
    _tiles: dict[MapPosition, TileState] = field(default_factory=dict, repr=False)

    def tile_count(self) -> int:
        return len(self._tiles)

    def get_tile(self, position: MapPosition) -> TileState | None:
        return self._tiles.get(position)

    def set_tile(self, tile: TileState) -> None:
        self._tiles[tile.position] = tile
        self.mark_changed()

    def remove_tile(self, position: MapPosition) -> None:
        if position in self._tiles:
            del self._tiles[position]
            self.mark_changed()

    def update_properties(self, properties: MapPropertiesState) -> bool:
        previous_dimensions = (self.properties.width, self.properties.height)
        self.properties = replace(properties)
        return previous_dimensions != (self.properties.width, self.properties.height)

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

    def has_selection(self) -> bool:
        return bool(self.selection_positions)

    def select_position(self, position: MapPosition) -> None:
        self.selection_positions.add(position)

    def clear_selection(self) -> None:
        self.selection_positions.clear()
