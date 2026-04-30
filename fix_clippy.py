import re
from pathlib import Path

path = Path("crates/rme_core/src/editor.rs")
content = path.read_text()
content = content.replace("fn add_spawn_creature(", "#[allow(clippy::too_many_arguments)]\n    fn add_spawn_creature(")
content = content.replace("fn add_house(", "#[allow(clippy::too_many_arguments)]\n    fn add_house(")
path.write_text(content)

path = Path("crates/rme_core/src/io/dat.rs")
content = path.read_text()
content = content.replace("pub fn parse(payload: &[u8]) -> Result<DatFile, DatParseError> {", "#[allow(clippy::field_reassign_with_default)]\npub fn parse(payload: &[u8]) -> Result<DatFile, DatParseError> {")
path.write_text(content)

path = Path("crates/rme_core/src/io/otb.rs")
content = path.read_text()
content = content.replace("pub fn load(path: &str) -> Result<OtbFile, OtbError> {", "#[allow(clippy::field_reassign_with_default)]\npub fn load(path: &str) -> Result<OtbFile, OtbError> {")
path.write_text(content)

path = Path("crates/rme_core/src/map.rs")
content = path.read_text()
content = content.replace("pub fn collect_statistics(&self) -> MapStatistics {", "#[allow(clippy::field_reassign_with_default)]\n    pub fn collect_statistics(&self) -> MapStatistics {")
path.write_text(content)

print("Fixed clippy")
