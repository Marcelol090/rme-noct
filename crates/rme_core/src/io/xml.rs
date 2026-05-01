//! XML sidecar serialization for OTBM maps.

use std::collections::BTreeMap;
use std::fmt::{self, Write as _};
use std::io::ErrorKind;
use std::path::{Path, PathBuf};

use quick_xml::events::{BytesStart, Event};
use quick_xml::Reader;

use crate::map::{Creature, House, MapModel, Spawn, Waypoint};

#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct SidecarLoadReport {
    pub waypoints: usize,
    pub spawns: usize,
    pub creatures: usize,
    pub houses: usize,
    pub missing_files: usize,
}

impl SidecarLoadReport {
    fn merge(&mut self, other: Self) {
        self.waypoints += other.waypoints;
        self.spawns += other.spawns;
        self.creatures += other.creatures;
        self.houses += other.houses;
        self.missing_files += other.missing_files;
    }
}

#[derive(Debug)]
pub enum XmlLoadError {
    Io(std::io::Error),
    Parse(String),
}

impl fmt::Display for XmlLoadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(error) => write!(f, "{error}"),
            Self::Parse(error) => write!(f, "{error}"),
        }
    }
}

impl std::error::Error for XmlLoadError {}

impl From<std::io::Error> for XmlLoadError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}

pub fn save_waypoints(map: &MapModel) -> String {
    let mut waypoints: Vec<&Waypoint> = map.waypoints().iter().collect();
    waypoints.sort_by_key(|waypoint| waypoint.name().to_lowercase());

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

pub fn load_sidecar_xml(
    map: &mut MapModel,
    otbm_path: impl AsRef<Path>,
) -> Result<SidecarLoadReport, XmlLoadError> {
    let otbm_path = otbm_path.as_ref();
    let mut report = SidecarLoadReport::default();

    match read_optional_xml(&resolve_sidecar_path(
        otbm_path,
        map.waypointfile(),
        "waypoint",
    ))? {
        Some(xml) => report.waypoints += load_waypoints_xml(map, &xml)?,
        None => report.missing_files += 1,
    }

    match read_optional_xml(&resolve_sidecar_path(otbm_path, map.spawnfile(), "spawn"))? {
        Some(xml) => report.merge(load_spawns_xml(map, &xml)?),
        None => report.missing_files += 1,
    }

    match read_optional_xml(&resolve_sidecar_path(otbm_path, map.housefile(), "house"))? {
        Some(xml) => report.houses += load_houses_xml(map, &xml)?,
        None => report.missing_files += 1,
    }

    Ok(report)
}

pub fn load_waypoints_xml(map: &mut MapModel, xml: &str) -> Result<usize, XmlLoadError> {
    let mut reader = Reader::from_str(xml);
    reader.config_mut().trim_text(true);
    let mut buf = Vec::new();
    let mut stack = Vec::new();
    let mut loaded = 0usize;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Empty(event)) if event.name().as_ref() == b"waypoint" => {
                let attrs = read_attrs(&reader, &event)?;
                if let Some(waypoint) = parse_waypoint(&attrs) {
                    map.add_waypoint(waypoint);
                    loaded += 1;
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"waypoint" => {
                push_start(&mut stack, &event);
                let attrs = read_attrs(&reader, &event)?;
                if let Some(waypoint) = parse_waypoint(&attrs) {
                    map.add_waypoint(waypoint);
                    loaded += 1;
                }
            }
            Ok(Event::Start(event)) => push_start(&mut stack, &event),
            Ok(Event::End(event)) => pop_end(&mut stack, event.name().as_ref())?,
            Ok(Event::Eof) => {
                ensure_balanced_eof(&stack, "XML")?;
                break;
            }
            Ok(_) => {}
            Err(error) => return Err(XmlLoadError::Parse(error.to_string())),
        }
        buf.clear();
    }

    Ok(loaded)
}

pub fn load_spawns_xml(map: &mut MapModel, xml: &str) -> Result<SidecarLoadReport, XmlLoadError> {
    let mut reader = Reader::from_str(xml);
    reader.config_mut().trim_text(true);
    let mut buf = Vec::new();
    let mut stack = Vec::new();
    let mut report = SidecarLoadReport::default();

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Empty(event)) if event.name().as_ref() == b"spawn" => {
                let attrs = read_attrs(&reader, &event)?;
                if let Some(spawn) = parse_spawn(&attrs) {
                    map.add_spawn(spawn);
                    report.spawns += 1;
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"spawn" => {
                let attrs = read_attrs(&reader, &event)?;
                if let Some(mut spawn) = parse_spawn(&attrs) {
                    let creatures = read_spawn_children(&mut reader, &mut spawn)?;
                    map.add_spawn(spawn);
                    report.spawns += 1;
                    report.creatures += creatures;
                } else {
                    skip_element(&mut reader, b"spawn")?;
                }
            }
            Ok(Event::Start(event)) => push_start(&mut stack, &event),
            Ok(Event::End(event)) => pop_end(&mut stack, event.name().as_ref())?,
            Ok(Event::Eof) => {
                ensure_balanced_eof(&stack, "XML")?;
                break;
            }
            Ok(_) => {}
            Err(error) => return Err(XmlLoadError::Parse(error.to_string())),
        }
        buf.clear();
    }

    Ok(report)
}

pub fn load_houses_xml(map: &mut MapModel, xml: &str) -> Result<usize, XmlLoadError> {
    let mut reader = Reader::from_str(xml);
    reader.config_mut().trim_text(true);
    let mut buf = Vec::new();
    let mut stack = Vec::new();
    let mut loaded = 0usize;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Empty(event)) if event.name().as_ref() == b"house" => {
                let attrs = read_attrs(&reader, &event)?;
                if let Some(house) = parse_house(&attrs) {
                    map.add_house(house);
                    loaded += 1;
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"house" => {
                push_start(&mut stack, &event);
                let attrs = read_attrs(&reader, &event)?;
                if let Some(house) = parse_house(&attrs) {
                    map.add_house(house);
                    loaded += 1;
                }
            }
            Ok(Event::Start(event)) => push_start(&mut stack, &event),
            Ok(Event::End(event)) => pop_end(&mut stack, event.name().as_ref())?,
            Ok(Event::Eof) => {
                ensure_balanced_eof(&stack, "XML")?;
                break;
            }
            Ok(_) => {}
            Err(error) => return Err(XmlLoadError::Parse(error.to_string())),
        }
        buf.clear();
    }

    Ok(loaded)
}

fn sidecar_path(otbm_path: &Path, suffix: &str) -> PathBuf {
    let stem = otbm_path
        .file_stem()
        .and_then(|value| value.to_str())
        .filter(|value| !value.is_empty())
        .unwrap_or("map");
    otbm_path.with_file_name(format!("{stem}-{suffix}.xml"))
}

fn resolve_sidecar_path(otbm_path: &Path, explicit: &str, suffix: &str) -> PathBuf {
    let explicit = explicit.trim();
    if explicit.is_empty() {
        return sidecar_path(otbm_path, suffix);
    }

    let explicit_path = PathBuf::from(explicit);
    if explicit_path.is_absolute() {
        return explicit_path;
    }

    otbm_path
        .parent()
        .map(|parent| parent.join(&explicit_path))
        .unwrap_or(explicit_path)
}

fn read_optional_xml(path: &Path) -> Result<Option<String>, XmlLoadError> {
    match std::fs::read_to_string(path) {
        Ok(xml) => Ok(Some(xml)),
        Err(error) if error.kind() == ErrorKind::NotFound => Ok(None),
        Err(error) => Err(XmlLoadError::Io(error)),
    }
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

fn read_attrs(
    reader: &Reader<&[u8]>,
    event: &BytesStart<'_>,
) -> Result<BTreeMap<String, String>, XmlLoadError> {
    let mut attrs = BTreeMap::new();
    for attr in event.attributes() {
        let attr = attr.map_err(|error| XmlLoadError::Parse(error.to_string()))?;
        let key = std::str::from_utf8(attr.key.as_ref())
            .map_err(|error| XmlLoadError::Parse(error.to_string()))?
            .to_string();
        let value = attr
            .decode_and_unescape_value(reader.decoder())
            .map_err(|error| XmlLoadError::Parse(error.to_string()))?
            .into_owned();
        attrs.insert(key, value);
    }
    Ok(attrs)
}

fn push_start(stack: &mut Vec<Vec<u8>>, event: &BytesStart<'_>) {
    stack.push(event.name().as_ref().to_vec());
}

fn pop_end(stack: &mut Vec<Vec<u8>>, end: &[u8]) -> Result<(), XmlLoadError> {
    let Some(start) = stack.pop() else {
        return Err(XmlLoadError::Parse("unexpected XML end tag".to_string()));
    };
    if start.as_slice() != end {
        return Err(XmlLoadError::Parse(format!(
            "mismatched XML end tag: expected </{}>, got </{}>",
            element_name(&start),
            element_name(end),
        )));
    }
    Ok(())
}

fn ensure_balanced_eof(stack: &[Vec<u8>], context: &str) -> Result<(), XmlLoadError> {
    if stack.is_empty() {
        return Ok(());
    }
    Err(XmlLoadError::Parse(format!(
        "unexpected EOF while reading {context}"
    )))
}

fn element_name(name: &[u8]) -> String {
    String::from_utf8_lossy(name).into_owned()
}

fn parse_waypoint(attrs: &BTreeMap<String, String>) -> Option<Waypoint> {
    let name = attr_str(attrs, "name")?;
    let x = attr_i32(attrs, "x")?;
    let y = attr_i32(attrs, "y")?;
    let z = attr_i32(attrs, "z")?;
    if name.is_empty() || x == 0 || y == 0 {
        return None;
    }
    Some(Waypoint::new(
        name.to_string(),
        crate::map::MapPosition::new(x, y, z),
    ))
}

fn parse_spawn(attrs: &BTreeMap<String, String>) -> Option<Spawn> {
    let centerx = attr_i32(attrs, "centerx")?;
    let centery = attr_i32(attrs, "centery")?;
    let centerz = attr_i32(attrs, "centerz")?;
    let radius = attr_i32(attrs, "radius")?;
    if centerx == 0 || centery == 0 || radius < 1 {
        return None;
    }
    Some(Spawn::new(
        crate::map::MapPosition::new(centerx, centery, centerz),
        radius,
    ))
}

fn read_spawn_children(
    reader: &mut Reader<&[u8]>,
    spawn: &mut Spawn,
) -> Result<usize, XmlLoadError> {
    let mut buf = Vec::new();
    let mut child_stack = Vec::new();
    let mut loaded = 0usize;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Empty(event))
                if event.name().as_ref() == b"monster" || event.name().as_ref() == b"npc" =>
            {
                let attrs = read_attrs(reader, &event)?;
                if let Some(creature) = parse_creature(&attrs, event.name().as_ref() == b"npc") {
                    spawn.add_creature(creature);
                    loaded += 1;
                }
            }
            Ok(Event::Start(event))
                if event.name().as_ref() == b"monster" || event.name().as_ref() == b"npc" =>
            {
                push_start(&mut child_stack, &event);
                let attrs = read_attrs(reader, &event)?;
                if let Some(creature) = parse_creature(&attrs, event.name().as_ref() == b"npc") {
                    spawn.add_creature(creature);
                    loaded += 1;
                }
            }
            Ok(Event::Start(event)) => push_start(&mut child_stack, &event),
            Ok(Event::End(event)) if event.name().as_ref() == b"spawn" => {
                if child_stack.is_empty() {
                    break;
                }
                return Err(XmlLoadError::Parse(
                    "unexpected spawn end while child XML is open".to_string(),
                ));
            }
            Ok(Event::End(event)) => pop_end(&mut child_stack, event.name().as_ref())?,
            Ok(Event::Eof) => {
                return Err(XmlLoadError::Parse(
                    "unexpected EOF while reading spawn".to_string(),
                ))
            }
            Ok(_) => {}
            Err(error) => return Err(XmlLoadError::Parse(error.to_string())),
        }
        buf.clear();
    }

    Ok(loaded)
}

fn skip_element(reader: &mut Reader<&[u8]>, element: &[u8]) -> Result<(), XmlLoadError> {
    let mut buf = Vec::new();
    let mut nested = 0usize;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(event)) if event.name().as_ref() == element => nested += 1,
            Ok(Event::End(event)) if event.name().as_ref() == element => {
                if nested == 0 {
                    break;
                }
                nested -= 1;
            }
            Ok(Event::Eof) => {
                return Err(XmlLoadError::Parse(
                    "unexpected EOF while skipping XML element".to_string(),
                ))
            }
            Ok(_) => {}
            Err(error) => return Err(XmlLoadError::Parse(error.to_string())),
        }
        buf.clear();
    }

    Ok(())
}

fn parse_creature(attrs: &BTreeMap<String, String>, is_npc: bool) -> Option<Creature> {
    let name = attr_str(attrs, "name")?;
    let offset_x = attr_i32(attrs, "x")?;
    let offset_y = attr_i32(attrs, "y")?;
    if name.is_empty() {
        return None;
    }
    Some(Creature::new(
        name.to_string(),
        offset_x,
        offset_y,
        attr_u32(attrs, "spawntime").unwrap_or(0),
        is_npc,
        attr_u32(attrs, "direction")
            .unwrap_or(0)
            .min(u32::from(u8::MAX)) as u8,
    ))
}

fn parse_house(attrs: &BTreeMap<String, String>) -> Option<House> {
    let houseid = attr_u32(attrs, "houseid")?;
    let townid = attr_u32(attrs, "townid")?;
    Some(House::new(
        houseid,
        attr_str(attrs, "name").unwrap_or("").to_string(),
        crate::map::MapPosition::new(
            attr_i32(attrs, "entryx").unwrap_or(0),
            attr_i32(attrs, "entryy").unwrap_or(0),
            attr_i32(attrs, "entryz").unwrap_or(0),
        ),
        attr_u32(attrs, "rent").unwrap_or(0),
        townid,
        attr_bool(attrs, "guildhall").unwrap_or(false),
        attr_u32(attrs, "size").unwrap_or(0),
    ))
}

fn attr_str<'a>(attrs: &'a BTreeMap<String, String>, key: &str) -> Option<&'a str> {
    attrs.get(key).map(|value| value.trim())
}

fn attr_i32(attrs: &BTreeMap<String, String>, key: &str) -> Option<i32> {
    attr_str(attrs, key)?.parse().ok()
}

fn attr_u32(attrs: &BTreeMap<String, String>, key: &str) -> Option<u32> {
    attr_str(attrs, key)?.parse().ok()
}

fn attr_bool(attrs: &BTreeMap<String, String>, key: &str) -> Option<bool> {
    match attr_str(attrs, key)?.to_ascii_lowercase().as_str() {
        "1" | "true" | "yes" => Some(true),
        "0" | "false" | "no" => Some(false),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use crate::map::{Creature, House, MapModel, MapPosition, Spawn, Waypoint};

    use super::{
        load_houses_xml, load_sidecar_xml, load_spawns_xml, load_waypoints_xml, save_houses,
        save_spawns, save_waypoints,
    };

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

    #[test]
    fn xml_loads_waypoints_and_skips_invalid_nodes() {
        let mut map = MapModel::new();
        let loaded = load_waypoints_xml(
            &mut map,
            r#"<?xml version="1.0"?>
<waypoints>
    <waypoint name="Temple" x="100" y="200" z="7" />
    <waypoint name="" x="101" y="201" z="7" />
    <waypoint name="Bad X" x="0" y="201" z="7" />
</waypoints>
"#,
        )
        .unwrap();

        assert_eq!(loaded, 1);
        assert_eq!(map.waypoints().len(), 1);
        assert_eq!(map.waypoints()[0].name(), "Temple");
        assert_eq!(map.waypoints()[0].position().as_tuple(), (100, 200, 7));
    }

    #[test]
    fn xml_load_reports_malformed_document() {
        let mut map = MapModel::new();
        let err = load_waypoints_xml(
            &mut map,
            r#"<waypoints><waypoint name="Temple" x="100" y="200" z="7">"#,
        )
        .unwrap_err();

        assert!(err.to_string().contains("unexpected EOF"));
    }

    #[test]
    fn xml_load_reports_mismatched_end_tag() {
        let mut map = MapModel::new();
        let err = load_waypoints_xml(&mut map, r#"<waypoints></house>"#).unwrap_err();
        let message = err.to_string();

        assert!(
            message.contains("end") || message.contains("End") || message.contains("expected"),
            "{message}"
        );
    }

    #[test]
    fn xml_loads_spawns_and_creatures_with_legacy_validation() {
        let mut map = MapModel::new();
        let report = load_spawns_xml(
            &mut map,
            r#"<?xml version="1.0"?>
<spawns>
    <spawn centerx="101" centery="201" centerz="7" radius="5">
        <monster name="Rat" x="1" y="-1" spawntime="60" direction="2" />
        <npc name="Guide" x="0" y="0" spawntime="30" />
        <monster name="" x="2" y="2" spawntime="15" />
    </spawn>
    <spawn centerx="0" centery="201" centerz="7" radius="5" />
    <spawn centerx="102" centery="202" centerz="7" radius="0" />
</spawns>
"#,
        )
        .unwrap();

        assert_eq!(report.spawns, 1);
        assert_eq!(report.creatures, 2);
        assert_eq!(map.spawns().len(), 1);
        assert_eq!(map.spawns()[0].center().as_tuple(), (101, 201, 7));
        assert_eq!(map.spawns()[0].radius(), 5);
        assert_eq!(map.spawns()[0].creatures().len(), 2);
        assert!(map.spawns()[0].creatures()[1].is_npc());
    }

    #[test]
    fn xml_loads_houses_and_skips_missing_townid() {
        let mut map = MapModel::new();
        let loaded = load_houses_xml(
            &mut map,
            r#"<?xml version="1.0"?>
<houses>
    <house name="Depot" houseid="12" entryx="102" entryy="202" entryz="7" rent="500" guildhall="true" townid="3" size="14" />
    <house name="No Town" houseid="13" entryx="103" entryy="203" entryz="7" rent="0" />
</houses>
"#,
        )
        .unwrap();

        assert_eq!(loaded, 1);
        assert_eq!(map.houses().len(), 1);
        assert_eq!(map.houses()[0].id(), 12);
        assert_eq!(map.houses()[0].name(), "Depot");
        assert_eq!(map.houses()[0].entry().as_tuple(), (102, 202, 7));
        assert_eq!(map.houses()[0].townid(), 3);
        assert!(map.houses()[0].guildhall());
    }

    #[test]
    fn xml_sidecar_loader_uses_explicit_paths_and_stem_fallback() {
        let dir = tempfile::tempdir().unwrap();
        let otbm_path = dir.path().join("world.otbm");
        std::fs::write(&otbm_path, b"").unwrap();
        std::fs::write(
            dir.path().join("custom-spawn.xml"),
            r#"<?xml version="1.0"?><spawns><spawn centerx="101" centery="201" centerz="7" radius="5" /></spawns>"#,
        )
        .unwrap();
        std::fs::write(
            dir.path().join("world-house.xml"),
            r#"<?xml version="1.0"?><houses><house name="Depot" houseid="12" entryx="102" entryy="202" entryz="7" rent="500" townid="3" size="14" /></houses>"#,
        )
        .unwrap();
        std::fs::write(
            dir.path().join("world-waypoint.xml"),
            r#"<?xml version="1.0"?><waypoints><waypoint name="Temple" x="100" y="200" z="7" /></waypoints>"#,
        )
        .unwrap();

        let mut map = MapModel::new();
        map.set_spawnfile("custom-spawn.xml");

        let report = load_sidecar_xml(&mut map, &otbm_path).unwrap();

        assert_eq!(report.spawns, 1);
        assert_eq!(report.houses, 1);
        assert_eq!(report.waypoints, 1);
        assert_eq!(report.missing_files, 0);
    }

    #[test]
    fn external_canary_tfs_sidecar_xml_parse_when_configured() {
        let Some(root) = std::env::var_os("RME_NOCT_EXTERNAL_TIBIA_FIXTURES") else {
            return;
        };
        let root = std::path::PathBuf::from(root);
        let cases = [
            "holybaiak-server/data-canary/world/custom/events.otbm",
            "korvusot/data-canary/world/canary.otbm",
            "korvusot/data-otservbr-global/world/korvusot.otbm",
            "KingOT/MAPAS/ATUALIZADO/otservbr.otbm",
        ];

        let mut parsed_cases = 0usize;
        for relative in cases {
            let otbm_path = root.join(relative);
            if !otbm_path.exists() {
                continue;
            }
            let mut map = MapModel::new();
            let report = load_sidecar_xml(&mut map, &otbm_path).unwrap();
            if report.waypoints + report.spawns + report.houses > 0 {
                parsed_cases += 1;
            }
        }

        assert!(
            parsed_cases > 0,
            "no configured Canary/TFS sidecar fixtures parsed"
        );
    }
}
