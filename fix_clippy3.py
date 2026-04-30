import re
from pathlib import Path

path = Path("crates/rme_core/src/io/dat.rs")
content = path.read_text()
content = content.replace("            #[allow(clippy::field_reassign_with_default)]\n            let mut it = DatItem::default();\n            it.client_id = client_id;", "            let mut it = DatItem { client_id, ..Default::default() };")
path.write_text(content)

path = Path("crates/rme_core/src/io/otb.rs")
content = path.read_text()
content = content.replace("            #[allow(clippy::field_reassign_with_default)]\n            let mut fr = OtbItem::default();\n            fr.group = child.node_type;", "            let mut fr = OtbItem { group: child.node_type, ..Default::default() };")
path.write_text(content)

print("Fixed clippy 3")
