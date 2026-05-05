from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

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


@dataclass(frozen=True, slots=True)
class TileEditChange:
    position: MapPosition
    before: TileState | None
    after: TileState | None


@dataclass(frozen=True, slots=True)
class MapStatisticsSnapshot:
    tile_count: int
    item_count: int
    blocking_tile_count: int = 0
    walkable_tile_count: int = 0
    spawn_count: int = 0
    creature_count: int = 0
    waypoint_count: int = 0
    house_count: int = 0
    total_house_sqm: int = 0
    town_count: int = 0


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
    _undo_stack: list[tuple[TileEditChange, ...]] = field(
        default_factory=list,
        repr=False,
    )
    _redo_stack: list[tuple[TileEditChange, ...]] = field(
        default_factory=list,
        repr=False,
    )
    _clipboard: tuple[tuple[int, int, int, TileState], ...] = field(
        default=(),
        repr=False,
    )

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
            self._apply_changes(
                (TileEditChange(position=position, before=existing, after=next_tile),)
            )
            return True

        if self.mode == "erasing":
            existing = self.map_model.get_tile(position)
            if existing is None:
                return False
            self._apply_changes(
                (TileEditChange(position=position, before=existing, after=None),)
            )
            return True

        return False

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def has_clipboard(self) -> bool:
        return bool(self._clipboard)

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        changes = self._undo_stack.pop()
        self._apply_changes(
            tuple(
                TileEditChange(
                    position=change.position,
                    before=change.after,
                    after=change.before,
                )
                for change in changes
            ),
            record=False,
        )
        self._redo_stack.append(changes)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        changes = self._redo_stack.pop()
        self._apply_changes(changes, record=False)
        self._undo_stack.append(changes)
        return True

    def copy_selection(self) -> bool:
        selected_tiles = [
            tile
            for position in sorted(self.selection_positions)
            if (tile := self.map_model.get_tile(position)) is not None
        ]
        if not selected_tiles:
            return False
        anchor_x = min(tile.position.x for tile in selected_tiles)
        anchor_y = min(tile.position.y for tile in selected_tiles)
        anchor_z = min(tile.position.z for tile in selected_tiles)
        self._clipboard = tuple(
            (
                tile.position.x - anchor_x,
                tile.position.y - anchor_y,
                tile.position.z - anchor_z,
                tile,
            )
            for tile in selected_tiles
        )
        return True

    def cut_selection(self) -> bool:
        if not self.copy_selection():
            return False
        changes = tuple(
            TileEditChange(position=tile.position, before=tile, after=None)
            for _dx, _dy, _dz, tile in self._clipboard
        )
        changed = self._apply_changes(changes)
        if changed:
            self.clear_selection()
        return changed

    def paste_clipboard_at(self, anchor: MapPosition) -> bool:
        changes: list[TileEditChange] = []
        for dx, dy, dz, tile in self._clipboard:
            position = MapPosition(anchor.x + dx, anchor.y + dy, anchor.z + dz)
            after = TileState(
                position=position,
                ground_item_id=tile.ground_item_id,
                item_ids=tile.item_ids,
            )
            before = self.map_model.get_tile(position)
            if before != after:
                changes.append(
                    TileEditChange(position=position, before=before, after=after)
                )
        return self._apply_changes(tuple(changes))

    def clipboard_tile_count(self) -> int:
        return len(self._clipboard)

    def replace_item_id(
        self,
        old_item_id: int,
        new_item_id: int,
        positions: Iterable[MapPosition] | None = None,
    ) -> int:
        changes: list[TileEditChange] = []
        occurrence_count = 0
        for tile in self._iter_target_tiles(positions):
            next_ground = (
                new_item_id if tile.ground_item_id == old_item_id else tile.ground_item_id
            )
            next_items = tuple(
                new_item_id if item_id == old_item_id else item_id
                for item_id in tile.item_ids
            )
            occurrence_count += int(tile.ground_item_id == old_item_id)
            occurrence_count += sum(1 for item_id in tile.item_ids if item_id == old_item_id)
            next_tile = TileState(
                position=tile.position,
                ground_item_id=next_ground,
                item_ids=next_items,
            )
            if tile != next_tile:
                changes.append(
                    TileEditChange(
                        position=tile.position,
                        before=tile,
                        after=next_tile,
                    )
                )
        if not self._apply_changes(tuple(changes)):
            return 0
        return occurrence_count

    def remove_item_id(
        self,
        item_id: int,
        positions: Iterable[MapPosition] | None = None,
    ) -> int:
        changes: list[TileEditChange] = []
        occurrence_count = 0
        for tile in self._iter_target_tiles(positions):
            next_ground = None if tile.ground_item_id == item_id else tile.ground_item_id
            next_items = tuple(
                stacked_item_id
                for stacked_item_id in tile.item_ids
                if stacked_item_id != item_id
            )
            occurrence_count += int(tile.ground_item_id == item_id)
            occurrence_count += sum(
                1 for stacked_item_id in tile.item_ids if stacked_item_id == item_id
            )
            if next_ground is None and not next_items:
                after = None
            else:
                after = TileState(
                    position=tile.position,
                    ground_item_id=next_ground,
                    item_ids=next_items,
                )
            if tile != after:
                changes.append(
                    TileEditChange(
                        position=tile.position,
                        before=tile,
                        after=after,
                    )
                )
        if not self._apply_changes(tuple(changes)):
            return 0
        return occurrence_count

    def clear_modified_state(self) -> bool:
        was_dirty = self.map_model.is_dirty
        self.map_model.clear_changed()
        return was_dirty

    def collect_statistics(self) -> MapStatisticsSnapshot:
        tiles = self.map_model.tiles()
        return MapStatisticsSnapshot(
            tile_count=len(tiles),
            item_count=sum(
                int(tile.ground_item_id is not None) + len(tile.item_ids)
                for tile in tiles
            ),
            walkable_tile_count=len(tiles),
        )

    def selection_item_counts(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for tile in self._iter_target_tiles(self.selection_positions):
            if tile.ground_item_id is not None:
                counts[tile.ground_item_id] = counts.get(tile.ground_item_id, 0) + 1
            for item_id in tile.item_ids:
                counts[item_id] = counts.get(item_id, 0) + 1
        return counts

    def _iter_target_tiles(
        self,
        positions: Iterable[MapPosition] | None,
    ) -> tuple[TileState, ...]:
        if positions is None:
            return self.map_model.tiles()
        return tuple(
            tile
            for position in sorted(set(positions))
            if (tile := self.map_model.get_tile(position)) is not None
        )

    def _apply_changes(
        self,
        changes: tuple[TileEditChange, ...],
        *,
        record: bool = True,
    ) -> bool:
        effective_changes = tuple(
            change for change in changes if change.before != change.after
        )
        if not effective_changes:
            return False
        for change in effective_changes:
            if change.after is None:
                self.map_model.remove_tile(change.position)
            else:
                self.map_model.set_tile(change.after)
        if record:
            self._undo_stack.append(effective_changes)
            self._redo_stack.clear()
        return True

    def has_selection(self) -> bool:
        return bool(self.selection_positions)

    def select_position(self, position: MapPosition) -> None:
        self.selection_positions.add(position)

    def clear_selection(self) -> None:
        self.selection_positions.clear()
