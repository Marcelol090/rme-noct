//! XML sidecar serialization for OTBM maps.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use crate::map::{Creature, House, MapModel, Spawn, Waypoint};

pub fn save_waypoints(map: &MapModel) -> String {
    let mut waypoints: Vec<&Waypoint> = map.waypoints().iter().collect();
    waypoints.sort_by_key(|left| left.name().to_lowercase());

    let mut xml = xml_header("waypoints", waypoints.is_empty());
    if waypoints.is_empty() {
        return xml;
    }
    for waypoint in waypoints {
        let position = waypoint.position();
        writeln!(
            xml,
            "\t<waypoint name=\"{}\" x=\"{}\" y=\"{}\" z=\"{}\" />",
            escape_attr(waypoint.name()),
            position.x(),
            position.y(),
            position.z(),
        )
        .expect("writing XML into String cannot fail");
    }
    xml.push_str("</waypoints>\n");
    xml
}

pub fn save_spawns(map: &MapModel) -> String {
    let mut spawns: Vec<&Spawn> = map.spawns().iter().collect();
    spawns.sort_by_key(|spawn| {
        let center = spawn.center();
        (center.x(), center.y(), center.z())
    });

    let mut xml = xml_header("spawns", spawns.is_empty());
    if spawns.is_empty() {
        return xml;
    }
    for spawn in spawns {
        let center = spawn.center();
        write!(
            xml,
            "\t<spawn centerx=\"{}\" centery=\"{}\" centerz=\"{}\" radius=\"{}\"",
            center.x(),
            center.y(),
            center.z(),
            spawn.radius(),
        )
        .expect("writing XML into String cannot fail");

        let mut creatures: Vec<&Creature> = spawn
            .creatures()
            .iter()
            .filter(|creature| creature_is_inside_spawn_radius(creature, spawn.radius()))
            .collect();
        creatures.sort_by_key(|creature| {
            (
                creature.offset_y(),
                creature.offset_x(),
                creature.name().to_lowercase(),
            )
        });
        if creatures.is_empty() {
            xml.push_str(" />\n");
            continue;
        }

        xml.push_str(">\n");
        for creature in creatures {
            let tag = if creature.is_npc() { "npc" } else { "monster" };
            write!(
                xml,
                "\t\t<{tag} name=\"{}\" x=\"{}\" y=\"{}\" spawntime=\"{}\"",
                escape_attr(creature.name()),
                creature.offset_x(),
                creature.offset_y(),
                creature.spawntime(),
            )
            .expect("writing XML into String cannot fail");
            if creature.direction() != 0 {
                write!(xml, " direction=\"{}\"", creature.direction())
                    .expect("writing XML into String cannot fail");
            }
            xml.push_str(" />\n");
        }
        xml.push_str("\t</spawn>\n");
    }
    xml.push_str("</spawns>\n");
    xml
}

pub fn save_houses(map: &MapModel) -> String {
    let mut houses: Vec<&House> = map.houses().iter().collect();
    houses.sort_by_key(|house| house.id());

    let mut xml = xml_header("houses", houses.is_empty());
    if houses.is_empty() {
        return xml;
    }
    for house in houses {
        let entry = house.entry();
        write!(
            xml,
            "\t<house name=\"{}\" houseid=\"{}\" entryx=\"{}\" entryy=\"{}\" \
             entryz=\"{}\" rent=\"{}\"",
            escape_attr(house.name()),
            house.id(),
            entry.x(),
            entry.y(),
            entry.z(),
            house.rent(),
        )
        .expect("writing XML into String cannot fail");
        if house.guildhall() {
            xml.push_str(" guildhall=\"true\"");
        }
        writeln!(
            xml,
            " townid=\"{}\" size=\"{}\" />",
            house.townid(),
            house.size()
        )
        .expect("writing XML into String cannot fail");
    }
    xml.push_str("</houses>\n");
    xml
}

pub fn save_sidecar_xml(map: &MapModel, otbm_path: impl AsRef<Path>) -> std::io::Result<()> {
    let otbm_path = otbm_path.as_ref();
    std::fs::write(sidecar_path(otbm_path, "waypoint"), save_waypoints(map))?;
    std::fs::write(sidecar_path(otbm_path, "spawn"), save_spawns(map))?;
    std::fs::write(sidecar_path(otbm_path, "house"), save_houses(map))?;
    Ok(())
}

fn sidecar_path(otbm_path: &Path, suffix: &str) -> PathBuf {
    let stem = otbm_path
        .file_stem()
        .and_then(|value| value.to_str())
        .filter(|value| !value.is_empty())
        .unwrap_or("map");
    otbm_path.with_file_name(format!("{stem}-{suffix}.xml"))
}

fn xml_header(root: &str, empty: bool) -> String {
    if empty {
        format!("<?xml version=\"1.0\"?>\n<{root} />\n")
    } else {
        format!("<?xml version=\"1.0\"?>\n<{root}>\n")
    }
}

fn escape_attr(raw: &str) -> String {
    let mut escaped = String::with_capacity(raw.len());
    for ch in raw.chars() {
        match ch {
            '&' => escaped.push_str("&amp;"),
            '"' => escaped.push_str("&quot;"),
            '<' => escaped.push_str("&lt;"),
            '>' => escaped.push_str("&gt;"),
            '\'' => escaped.push_str("&apos;"),
            _ => escaped.push(ch),
        }
    }
    escaped
}

fn creature_is_inside_spawn_radius(creature: &Creature, radius: u32) -> bool {
    creature.offset_x().unsigned_abs() <= radius && creature.offset_y().unsigned_abs() <= radius
}

#[cfg(test)]
mod tests {
    use crate::map::{Creature, House, MapModel, MapPosition, Spawn, Waypoint};

    use super::{save_houses, save_spawns, save_waypoints};

    #[test]
    fn xml_sidecars_match_legacy_roots_and_attributes() {
        let mut map = MapModel::new();
        map.add_waypoint(Waypoint::new(
            "Temple & Shop",
            MapPosition::new(100, 200, 7),
        ));
        let spawn_index = map.add_spawn(Spawn::new(MapPosition::new(101, 201, 7), 5));
        map.add_spawn_creature(
            spawn_index,
            Creature::new("Rat \"Scout\"", 1, -1, 60, false, 2),
        )
        .unwrap();
        map.add_house(House::new(
            12,
            "Depot \"North\"",
            MapPosition::new(102, 202, 7),
            500,
            3,
            true,
            14,
        ));

        assert_eq!(
            save_waypoints(&map),
            "<?xml version=\"1.0\"?>\n<waypoints>\n\t<waypoint name=\"Temple &amp; Shop\" x=\"100\" y=\"200\" z=\"7\" />\n</waypoints>\n"
        );
        assert_eq!(
            save_spawns(&map),
            "<?xml version=\"1.0\"?>\n<spawns>\n\t<spawn centerx=\"101\" centery=\"201\" centerz=\"7\" radius=\"5\">\n\t\t<monster name=\"Rat &quot;Scout&quot;\" x=\"1\" y=\"-1\" spawntime=\"60\" direction=\"2\" />\n\t</spawn>\n</spawns>\n"
        );
        assert_eq!(
            save_houses(&map),
            "<?xml version=\"1.0\"?>\n<houses>\n\t<house name=\"Depot &quot;North&quot;\" houseid=\"12\" entryx=\"102\" entryy=\"202\" entryz=\"7\" rent=\"500\" guildhall=\"true\" townid=\"3\" size=\"14\" />\n</houses>\n"
        );
    }

    #[test]
    fn xml_spawns_use_legacy_radius_scan_window() {
        let mut map = MapModel::new();
        let spawn_index = map.add_spawn(Spawn::new(MapPosition::new(101, 201, 7), 0));
        map.add_spawn_creature(spawn_index, Creature::new("Guide", 0, 0, 30, true, 0))
            .unwrap();
        map.add_spawn_creature(spawn_index, Creature::new("Outside", 1, 0, 30, false, 0))
            .unwrap();

        assert_eq!(
            save_spawns(&map),
            "<?xml version=\"1.0\"?>\n<spawns>\n\t<spawn centerx=\"101\" centery=\"201\" centerz=\"7\" radius=\"0\">\n\t\t<npc name=\"Guide\" x=\"0\" y=\"0\" spawntime=\"30\" />\n\t</spawn>\n</spawns>\n"
        );
    }
}
