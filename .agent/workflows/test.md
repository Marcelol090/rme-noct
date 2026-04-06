---
description: Run the full test suite (Python + Rust)
---

// turbo-all

1. Run Rust tests: `cargo test --manifest-path crates/rme_core/Cargo.toml`
2. Run Python tests: `pytest tests/python/ -v --tb=short`
3. Run ruff linter: `ruff check pyrme/`
4. Run mypy type checks: `mypy pyrme/ --ignore-missing-imports`
