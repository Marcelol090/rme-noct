---
name: pyrme-context
description: Use at the start of EVERY task or session to load project context, architecture decisions, and coding conventions for the PyRME project.
---

# PyRME Project Context

## Architecture Overview

**PyRME** is a ground-up rewrite of [Remere's Map Editor](https://github.com/karolak6612/remeres-map-editor-redux) targeting full feature parity with RME Extended Edition 3.8.

```
┌─────────────────────────────────┐
│   Python UI Layer (PyQt6)       │
│   Menus, Dialogs, Palettes,     │
│   Docks, Preferences, DevTools  │
├─────────────────────────────────┤
│   PyO3 Bridge (zero-copy)       │
├─────────────────────────────────┤
│   Rust Core (rme_core)          │
│   Canvas, Map, Tiles, Brushes,  │
│   I/O (OTBM/OTB/DAT/SPR),      │
│   Undo/Redo, Selection          │
└─────────────────────────────────┘
```

## Stack

- **Python 3.12+** / **PyQt6** (latest) – UI layer
- **Rust** via **PyO3** + **maturin** – Performance core
- **wgpu** – GPU canvas renderer (Milestone 4)
- **fnv** – FNV-1a hashing (sprite hash matching)
- **rayon** – Parallel processing
- **serde** – Serialization (clipboard, config)

## Conventions

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Python: ruff + mypy strict
- Rust: clippy + cargo fmt
- Tests: pytest (Python), cargo test + proptest (Rust)
- UI: Obsidian Cartographer dark theme (purple #6e5ae6 accent)

## Mandatory Checklist

Before ANY implementation:
1. ☑ Check Context7 MCP for library docs
2. ☑ Reference legacy C++ at `remeres-map-editor-redux/source/`
3. ☑ Check Stitch for UI mockups (if UI work)
4. ☑ Run verification: `pytest`, `ruff`, `mypy`, `cargo test`

## Key Files

- `pyproject.toml` – Python build config
- `Cargo.toml` – Rust workspace
- `crates/rme_core/` – Rust core library
- `pyrme/` – Python package
- `.gsd/preferences.md` – GSD-2 config
- `.pi/agent/skills/` – Project-scope skills
