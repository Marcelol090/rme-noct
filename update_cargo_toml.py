import re
from pathlib import Path

path = Path("crates/rme_core/Cargo.toml")
content = path.read_text()

search = """[dependencies]
pyo3 = { version = "0.23", features = ["extension-module"] }"""

replace = """[dependencies]
pyo3 = { version = "0.23" }"""

search2 = """[features]
default = []"""

replace2 = """[features]
default = []
extension-module = ["pyo3/extension-module"]"""

if search in content and search2 in content:
    content = content.replace(search, replace).replace(search2, replace2)
    path.write_text(content)
    print("Updated Cargo.toml")
else:
    print("Failed to find replacement points.")
