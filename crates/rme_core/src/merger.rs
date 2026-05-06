use crate::map::{MapModel, MapPosition, Tile, MAX_XY, MAX_Z};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CollisionPolicy {
    Replace,
    Skip,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MapMergeOptions {
    pub offset_x: i32,
    pub offset_y: i32,
    pub offset_z: i32,
    pub collision_policy: CollisionPolicy,
}

impl Default for MapMergeOptions {
    fn default() -> Self {
        Self {
            offset_x: 0,
            offset_y: 0,
            offset_z: 0,
            collision_policy: CollisionPolicy::Replace,
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct MergeReport {
    pub copied_tiles: u64,
    pub replaced_tiles: u64,
    pub skipped_existing_tiles: u64,
    pub discarded_tiles: u64,
}

pub fn merge_map_tiles(
    target: &mut MapModel,
    source: &MapModel,
    options: MapMergeOptions,
) -> MergeReport {
    let mut report = MergeReport::default();

    for source_tile in source.iter_tiles() {
        let Some(destination) = translate_position(source_tile.position(), options) else {
            report.discarded_tiles += 1;
            continue;
        };

        if target.get_tile(&destination).is_some() {
            match options.collision_policy {
                CollisionPolicy::Skip => {
                    report.skipped_existing_tiles += 1;
                    continue;
                }
                CollisionPolicy::Replace => {
                    report.replaced_tiles += 1;
                }
            }
        }

        target.set_tile(copy_tile_at(source_tile, destination));
        report.copied_tiles += 1;
    }

    report
}

fn translate_position(position: MapPosition, options: MapMergeOptions) -> Option<MapPosition> {
    let x = i32::from(position.x()) + options.offset_x;
    let y = i32::from(position.y()) + options.offset_y;
    let z = i32::from(position.z()) + options.offset_z;

    if x < 0
        || y < 0
        || z < 0
        || x > i32::from(MAX_XY)
        || y > i32::from(MAX_XY)
        || z > i32::from(MAX_Z)
    {
        return None;
    }

    Some(MapPosition::new(x, y, z))
}

fn copy_tile_at(source: &Tile, destination: MapPosition) -> Tile {
    // Exhaustive tile payload copy for merge; update when Tile gains persisted fields.
    let mut tile = Tile::new(destination);
    tile.set_ground(source.ground().cloned());
    for item in source.items() {
        tile.add_item(item.clone());
    }
    tile.set_house_id(source.house_id());
    tile.set_mapflags(source.mapflags());
    tile.set_statflags(source.statflags());
    tile
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        item::Item,
        map::{MapPosition, Tile},
    };

    fn tile_with_contents(position: MapPosition, ground_id: u16) -> Tile {
        let mut tile = Tile::new(position);
        tile.set_ground(Some(Item::new(ground_id)));
        let mut stack_item = Item::new(2148);
        stack_item.set_count(10);
        tile.add_item(stack_item);
        tile.set_house_id(42);
        tile.set_mapflags(7);
        tile.set_statflags(4);
        tile
    }

    #[test]
    fn merge_offsets_tile_and_preserves_contents() {
        let mut target = MapModel::new();
        let mut source = MapModel::new();
        source.set_tile(tile_with_contents(MapPosition::new(10, 20, 7), 100));

        let report = merge_map_tiles(
            &mut target,
            &source,
            MapMergeOptions {
                offset_x: 5,
                offset_y: -2,
                offset_z: 1,
                collision_policy: CollisionPolicy::Replace,
            },
        );

        assert_eq!(report.copied_tiles, 1);
        assert_eq!(report.replaced_tiles, 0);
        assert_eq!(report.skipped_existing_tiles, 0);
        assert_eq!(report.discarded_tiles, 0);

        let merged = target
            .get_tile(&MapPosition::new(15, 18, 8))
            .expect("translated tile should exist");
        assert_eq!(merged.ground().unwrap().id(), 100);
        assert_eq!(merged.item_count(), 1);
        assert_eq!(merged.items()[0].id(), 2148);
        assert_eq!(merged.items()[0].count(), 10);
        assert_eq!(merged.house_id(), 42);
        assert_eq!(merged.mapflags(), 7);
        assert_eq!(merged.statflags(), 4);
    }

    #[test]
    fn replace_policy_overwrites_existing_destination_tile() {
        let mut target = MapModel::new();
        target.set_tile(tile_with_contents(MapPosition::new(15, 18, 8), 500));

        let mut source = MapModel::new();
        source.set_tile(tile_with_contents(MapPosition::new(10, 20, 7), 100));

        let report = merge_map_tiles(
            &mut target,
            &source,
            MapMergeOptions {
                offset_x: 5,
                offset_y: -2,
                offset_z: 1,
                collision_policy: CollisionPolicy::Replace,
            },
        );

        assert_eq!(report.copied_tiles, 1);
        assert_eq!(report.replaced_tiles, 1);
        assert_eq!(report.skipped_existing_tiles, 0);
        assert_eq!(report.discarded_tiles, 0);
        assert_eq!(
            target
                .get_tile(&MapPosition::new(15, 18, 8))
                .unwrap()
                .ground()
                .unwrap()
                .id(),
            100
        );
    }

    #[test]
    fn skip_policy_keeps_existing_destination_tile() {
        let mut target = MapModel::new();
        target.set_tile(tile_with_contents(MapPosition::new(15, 18, 8), 500));

        let mut source = MapModel::new();
        source.set_tile(tile_with_contents(MapPosition::new(10, 20, 7), 100));

        let report = merge_map_tiles(
            &mut target,
            &source,
            MapMergeOptions {
                offset_x: 5,
                offset_y: -2,
                offset_z: 1,
                collision_policy: CollisionPolicy::Skip,
            },
        );

        assert_eq!(report.copied_tiles, 0);
        assert_eq!(report.replaced_tiles, 0);
        assert_eq!(report.skipped_existing_tiles, 1);
        assert_eq!(report.discarded_tiles, 0);
        assert_eq!(
            target
                .get_tile(&MapPosition::new(15, 18, 8))
                .unwrap()
                .ground()
                .unwrap()
                .id(),
            500
        );
    }

    #[test]
    fn invalid_translated_positions_are_discarded() {
        let mut target = MapModel::new();
        let mut source = MapModel::new();
        source.set_tile(tile_with_contents(MapPosition::new(0, 0, 0), 100));
        source.set_tile(tile_with_contents(MapPosition::new(10, 10, 15), 200));

        let report = merge_map_tiles(
            &mut target,
            &source,
            MapMergeOptions {
                offset_x: -1,
                offset_y: 0,
                offset_z: 1,
                collision_policy: CollisionPolicy::Replace,
            },
        );

        assert_eq!(report.copied_tiles, 0);
        assert_eq!(report.discarded_tiles, 2);
        assert!(target.is_empty());
    }
}
