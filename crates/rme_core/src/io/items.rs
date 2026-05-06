//! Parser for Tibia `items.xml` definitions.

use std::collections::BTreeMap;
use std::fmt;

use quick_xml::events::{BytesStart, Event};
use quick_xml::Reader;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ItemType {
    pub id: u16,
    pub name: String,
    pub attributes: BTreeMap<String, String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ItemsXmlError {
    Parse(String),
}

impl fmt::Display for ItemsXmlError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Parse(error) => write!(f, "{error}"),
        }
    }
}

impl std::error::Error for ItemsXmlError {}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ItemTemplate {
    ids: Vec<u16>,
    name: String,
    attributes: BTreeMap<String, String>,
}

pub fn parse_items(xml: &str) -> Result<Vec<ItemType>, ItemsXmlError> {
    let mut reader = Reader::from_str(xml);
    reader.config_mut().trim_text(true);

    let mut buf = Vec::new();
    let mut items = Vec::new();
    let mut current_item: Option<ItemTemplate> = None;
    let mut stack = Vec::new();

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Empty(event)) if event.name().as_ref() == b"item" => {
                if let Some(item) = parse_item_start(&reader, &event)? {
                    items.extend(expand_item_template(&item));
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"item" => {
                push_start(&mut stack, &event);
                current_item = parse_item_start(&reader, &event)?;
            }
            Ok(Event::Empty(event)) if event.name().as_ref() == b"attribute" => {
                if let Some(item) = current_item.as_mut() {
                    insert_item_attribute(&reader, &event, item)?;
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"attribute" => {
                push_start(&mut stack, &event);
                if let Some(item) = current_item.as_mut() {
                    insert_item_attribute(&reader, &event, item)?;
                }
            }
            Ok(Event::End(event)) if event.name().as_ref() == b"item" => {
                pop_end(&mut stack, event.name().as_ref())?;
                if let Some(item) = current_item.take() {
                    items.extend(expand_item_template(&item));
                }
            }
            Ok(Event::Start(event)) => push_start(&mut stack, &event),
            Ok(Event::End(event)) => pop_end(&mut stack, event.name().as_ref())?,
            Ok(Event::Eof) => {
                if let Some(open) = stack.last() {
                    return Err(ItemsXmlError::Parse(format!(
                        "unclosed XML tag <{}>",
                        element_name(open)
                    )));
                }
                if current_item.is_some() {
                    return Err(ItemsXmlError::Parse("unclosed item".to_string()));
                }
                break;
            }
            Ok(_) => {}
            Err(error) => {
                return Err(ItemsXmlError::Parse(format!(
                    "items.xml parse error at byte {}: {error}",
                    reader.error_position()
                )));
            }
        }
        buf.clear();
    }

    Ok(items)
}

fn parse_item_start(
    reader: &Reader<&[u8]>,
    event: &BytesStart<'_>,
) -> Result<Option<ItemTemplate>, ItemsXmlError> {
    let attrs = read_attrs(reader, event)?;
    let Some(ids) = item_ids(&attrs)? else {
        return Ok(None);
    };
    let name = attrs.get("name").cloned().unwrap_or_default();

    Ok(Some(ItemTemplate {
        ids,
        name,
        attributes: BTreeMap::new(),
    }))
}

fn insert_item_attribute(
    reader: &Reader<&[u8]>,
    event: &BytesStart<'_>,
    item: &mut ItemTemplate,
) -> Result<(), ItemsXmlError> {
    let attrs = read_attrs(reader, event)?;
    let Some(key) = attrs.get("key").filter(|key| !key.trim().is_empty()) else {
        return Ok(());
    };
    let value = attrs.get("value").cloned().unwrap_or_default();
    item.attributes.insert(key.trim().to_string(), value);
    Ok(())
}

fn read_attrs(
    reader: &Reader<&[u8]>,
    event: &BytesStart<'_>,
) -> Result<BTreeMap<String, String>, ItemsXmlError> {
    let mut attrs = BTreeMap::new();
    for attr in event.attributes() {
        let attr = attr.map_err(|error| ItemsXmlError::Parse(error.to_string()))?;
        let key = std::str::from_utf8(attr.key.as_ref())
            .map_err(|error| ItemsXmlError::Parse(error.to_string()))?
            .to_string();
        let value = attr
            .decode_and_unescape_value(reader.decoder())
            .map_err(|error| ItemsXmlError::Parse(error.to_string()))?
            .into_owned();
        attrs.insert(key, value);
    }
    Ok(attrs)
}

fn item_ids(attrs: &BTreeMap<String, String>) -> Result<Option<Vec<u16>>, ItemsXmlError> {
    if let Some(id) = attr_u16(attrs, "id")? {
        return Ok(Some(vec![id]));
    }

    let Some(from_id) = attr_u16(attrs, "fromid")? else {
        return Ok(None);
    };
    let to_id = attr_u16(attrs, "toid")?.unwrap_or(from_id);
    if from_id > to_id {
        return Err(ItemsXmlError::Parse(format!(
            "invalid item range: fromid {from_id} is greater than toid {to_id}"
        )));
    }

    Ok(Some((from_id..=to_id).collect()))
}

fn attr_u16(attrs: &BTreeMap<String, String>, key: &str) -> Result<Option<u16>, ItemsXmlError> {
    let Some(value) = attrs.get(key) else {
        return Ok(None);
    };
    value
        .trim()
        .parse()
        .map(Some)
        .map_err(|error| ItemsXmlError::Parse(format!("invalid item {key}: {error}")))
}

fn expand_item_template(template: &ItemTemplate) -> Vec<ItemType> {
    template
        .ids
        .iter()
        .map(|id| ItemType {
            id: *id,
            name: template.name.clone(),
            attributes: template.attributes.clone(),
        })
        .collect()
}

fn push_start(stack: &mut Vec<Vec<u8>>, event: &BytesStart<'_>) {
    stack.push(event.name().as_ref().to_vec());
}

fn pop_end(stack: &mut Vec<Vec<u8>>, end: &[u8]) -> Result<(), ItemsXmlError> {
    let Some(start) = stack.pop() else {
        return Err(ItemsXmlError::Parse("unexpected XML end tag".to_string()));
    };
    if start.as_slice() != end {
        return Err(ItemsXmlError::Parse(format!(
            "mismatched XML end tag: expected </{}>, got </{}>",
            element_name(&start),
            element_name(end),
        )));
    }
    Ok(())
}

fn element_name(name: &[u8]) -> String {
    String::from_utf8_lossy(name).into_owned()
}

#[cfg(test)]
mod tests {
    use super::parse_items;

    #[test]
    fn parse_empty_items_root_returns_no_items() {
        let items = parse_items("<items></items>").expect("empty items.xml should parse");

        assert!(items.is_empty());
    }

    #[test]
    fn parse_item_with_nested_attribute() {
        let items = parse_items(
            r#"
            <items>
                <item id="100" name="Gold Coin">
                    <attribute key="weight" value="1200" />
                </item>
            </items>
            "#,
        )
        .expect("item with nested attribute should parse");

        assert_eq!(items.len(), 1);
        assert_eq!(items[0].id, 100);
        assert_eq!(items[0].name, "Gold Coin");
        assert_eq!(items[0].attributes.get("weight"), Some(&"1200".to_string()));
    }

    #[test]
    fn parse_range_item_expands_ids_with_attributes() {
        let items = parse_items(
            r#"
            <items>
                <item fromid="100" toid="102" name="Range">
                    <attribute key="weight" value="1" />
                </item>
            </items>
            "#,
        )
        .expect("range item should parse");

        assert_eq!(items.len(), 3);
        assert_eq!(items[0].id, 100);
        assert_eq!(items[1].id, 101);
        assert_eq!(items[2].id, 102);
        for item in items {
            assert_eq!(item.name, "Range");
            assert_eq!(item.attributes.get("weight"), Some(&"1".to_string()));
        }
    }

    #[test]
    fn parse_unclosed_item_returns_error() {
        let error = parse_items(r#"<items><item id="100" name="Broken">"#)
            .expect_err("unclosed item should fail");

        assert!(error.to_string().contains("unclosed"));
    }
}
