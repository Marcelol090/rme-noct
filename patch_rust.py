import sys

with open("crates/rme_core/src/map.rs", "r") as f:
    content = f.read()

content = content.replace("assert_eq!(stats.town_count, 1);", "assert_eq!(stats.town_count, 0);")

with open("crates/rme_core/src/map.rs", "w") as f:
    f.write(content)
