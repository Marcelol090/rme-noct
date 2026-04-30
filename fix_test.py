import re
from pathlib import Path

path = Path("crates/rme_core/src/map.rs")
content = path.read_text()

search = """        model.add_house(House::new(
            12,
            "House",
            MapPosition::new(12, 22, 7),
            500,
            3,
            true,
            14,
        ));"""

replace = """        model.add_house(House::new(
            12,
            "House",
            MapPosition::new(12, 22, 7),
            500,
            3,
            true,
            14,
        ));
        model.add_town(Town::new(1, "Thais", MapPosition::new(32369, 32241, 7)));"""

if search in content:
    content = content.replace(search, replace)
    path.write_text(content)
    print("Fixed map.rs")
else:
    print("Failed to find replacement point.")
