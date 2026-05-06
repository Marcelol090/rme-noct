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

pub fn parse_items(xml: &str) -> Result<Vec<ItemType>, ItemsXmlError> {
    let mut reader = Reader::from_str(xml);
    reader.config_mut().trim_text(true);

    let mut buf = Vec::new();
    let mut items = Vec::new();
    let mut current_item: Option<ItemType> = None;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Empty(event)) if event.name().as_ref() == b"item" => {
                if let Some(item) = parse_item_start(&reader, &event)? {
                    items.push(item);
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"item" => {
                current_item = parse_item_start(&reader, &event)?;
            }
            Ok(Event::Empty(event)) if event.name().as_ref() == b"attribute" => {
                if let Some(item) = current_item.as_mut() {
                    insert_item_attribute(&reader, &event, item)?;
                }
            }
            Ok(Event::Start(event)) if event.name().as_ref() == b"attribute" => {
                if let Some(item) = current_item.as_mut() {
                    insert_item_attribute(&reader, &event, item)?;
                }
            }
            Ok(Event::End(event)) if event.name().as_ref() == b"item" => {
                if let Some(item) = current_item.take() {
                    items.push(item);
                }
            }
            Ok(Event::Eof) => break,
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
) -> Result<Option<ItemType>, ItemsXmlError> {
    let attrs = read_attrs(reader, event)?;
    let Some(id) = attr_u16(&attrs, "id")? else {
        return Ok(None);
    };
    let name = attrs.get("name").cloned().unwrap_or_default();

    Ok(Some(ItemType {
        id,
        name,
        attributes: BTreeMap::new(),
    }))
}

fn insert_item_attribute(
    reader: &Reader<&[u8]>,
    event: &BytesStart<'_>,
    item: &mut ItemType,
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
}
