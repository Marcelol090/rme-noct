---
description: Build the Rust core and install Python package in development mode
---

1. Ensure you are in the project root directory
// turbo
2. Run `maturin develop` to build the Rust core and install it
3. Verify the build: `python -c "from pyrme import rme_core; print(rme_core.version())"`
// turbo
4. Run `cargo test --manifest-path crates/rme_core/Cargo.toml` to verify Rust tests pass
