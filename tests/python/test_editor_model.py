from __future__ import annotations

import pytest

from pyrme.editor import EditorModel, MapModel, MapPosition, MapPropertiesState, TileState


def test_map_model_stores_sparse_tiles_and_tracks_generation() -> None:
    model = MapModel()
    position = MapPosition(32000, 32000, 7)
    tile = TileState(position=position, ground_item_id=100, item_ids=(200, 201))

    assert model.tile_count() == 0
    assert model.get_tile(position) is None
    assert model.is_dirty is False
    assert model.generation == 0

    model.set_tile(tile)

    assert model.tile_count() == 1
    assert model.get_tile(position) == tile
    assert model.is_dirty is True
    assert model.generation == 1

    model.clear_changed()
    model.remove_tile(position)

    assert model.tile_count() == 0
    assert model.get_tile(position) is None
    assert model.is_dirty is True
    assert model.generation == 2


def test_map_position_rejects_coordinates_outside_legacy_bounds() -> None:
    with pytest.raises(ValueError, match="x must be"):
        MapPosition(-1, 32000, 7)

    with pytest.raises(ValueError, match="y must be"):
        MapPosition(32000, 65536, 7)

    with pytest.raises(ValueError, match="z must be"):
        MapPosition(32000, 32000, 16)


def test_editor_model_owns_shared_map_selection_and_secondary_map() -> None:
    editor = EditorModel()
    position = MapPosition(32000, 32000, 7)
    secondary_map = MapModel(name="Preview")

    editor.select_position(position)
    editor.secondary_map = secondary_map

    assert editor.has_selection() is True
    assert editor.selection_positions == {position}
    assert editor.secondary_map is secondary_map

    editor.clear_selection()
    assert editor.has_selection() is False


def test_map_model_metadata_updates_without_marking_map_dirty() -> None:
    model = MapModel()
    updated = MapPropertiesState(
        description="Test map",
        width=512,
        height=768,
        house_file="houses.xml",
        spawn_file="spawns.xml",
        waypoint_file="waypoints.xml",
    )

    dimensions_changed = model.update_properties(updated)

    assert dimensions_changed is True
    assert model.properties == updated
    assert model.is_dirty is False
    assert model.generation == 0
