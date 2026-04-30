import sys

with open("crates/rme_core/Cargo.toml", "r") as f:
    content = f.read()

content = content.replace(
    'pyo3 = { version = "0.23", features = ["extension-module"] }',
    'pyo3 = { version = "0.23" }'
)

if "extension-module = " not in content:
    content = content.replace(
        '[features]\ndefault = []',
        '[features]\nextension-module = ["pyo3/extension-module"]\ndefault = []'
    )

with open("crates/rme_core/Cargo.toml", "w") as f:
    f.write(content)
