import re
from pathlib import Path

path = Path("crates/rme_core/src/io/dat.rs")
content = path.read_text()
content = content.replace("            let mut it = DatItem::default();", "            #[allow(clippy::field_reassign_with_default)]\n            let mut it = DatItem::default();")
path.write_text(content)

path = Path("crates/rme_core/src/io/otb.rs")
content = path.read_text()
content = content.replace("            let mut fr = OtbItem::default();", "            #[allow(clippy::field_reassign_with_default)]\n            let mut fr = OtbItem::default();")
path.write_text(content)

print("Fixed clippy 2")
