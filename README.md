<p align="center">
  <h1 align="center">🗺️ Noct Map Editor</h1>
  <p align="center">
    <strong>Python + Rust Remere's Map Editor (Extended Edition)</strong>
  </p>
  <p align="center">
    Complete rewrite of the legacy C++ Remere's Map Editor with modern performance and UI
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Rust-2021-orange?logo=rust&logoColor=white" />
  <img src="https://img.shields.io/badge/UI-PyQt6-green?logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/GPU-wgpu-purple?logo=webgpu&logoColor=white" />
  <img src="https://img.shields.io/badge/License-GPL--2.0-red" />
</p>

---

## Overview

**Noct Map Editor** is a ground-up rewrite of [Remere's Map Editor](https://github.com/karolak6612/remeres-map-editor-redux) targeting full feature parity with **RME Extended Edition 2.5 / 3.7**, built with:

- 🐍 **Python 3.12+ / PyQt6** – Modern, dark-first UI with native desktop feel
- 🦀 **Rust (PyO3 + maturin)** – High-performance core for rendering, parsing, and data ops
- 🎮 **wgpu** – GPU-accelerated canvas renderer (60+ FPS on 512×512 maps)

## Architecture

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

## Quick Start

### Prerequisites

- Python 3.12+
- Rust (via [rustup](https://rustup.rs/))
- Node.js 22+ (required for the local GSD toolchain)

### Setup

```bash
# Clone the repository
git clone https://github.com/Marcelol090/rme-noct.git
cd rme-noct

# Install local devtools, including gsd-pi
npm install

# Run the full setup (Python venv + Rust build + devtools)
bash scripts/setup-devtools.sh

# Or manual setup:
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install maturin
maturin develop
pip install -e ".[dev]"
```

### Launch

```bash
python -m pyrme
```

### Development

```bash
# Build Rust core
maturin develop

# Run tests
pytest tests/python/ -v
cargo test --manifest-path crates/rme_core/Cargo.toml

# Lint
ruff check pyrme/

# GSD local CLI entrypoints
npm run gsd:status
npm run gsd:plan -- "Plan the next milestone"

# GSD autonomous mode
npm run gsd:auto
```

`npm run gsd:*` uses the repo-local `gsd-pi` installation from `node_modules`, so Node 22+ and `npm install` are required before those commands will work.

## Features (Planned)

- [ ] OTBM v0–v3 full read/write
- [ ] GPU-accelerated canvas (wgpu)
- [ ] All brush types (Ground, Wall, Border, Door, etc.)
- [ ] Auto-border with configurable rules
- [ ] Selection & clipboard (cross-instance)
- [ ] Undo/redo with unlimited history
- [ ] Live editing (multi-user)
- [ ] In-game preview
- [ ] Shader system (AA, CRT, 4xBRZ)
- [ ] AI-assisted development (GSD-2 + Superpowers)

## Milestones

| # | Milestone | Status |
|---|---|---|
| 1 | Project Scaffolding & Build System | 🟢 In Progress |
| 2 | Rust Core Data Structures | ⬜ Planned |
| 3 | File I/O (OTBM/OTB/DAT/SPR) | ⬜ Planned |
| 4 | Canvas Renderer (wgpu) | ⬜ Planned |
| 5 | Editor Shell & Navigation | ⬜ Planned |
| 6 | Brush Engine | ⬜ Planned |
| 7 | Selection & Clipboard | ⬜ Planned |
| 8 | Dialogs & Properties | ⬜ Planned |
| 9 | Advanced Features | ⬜ Planned |
| 10 | Polish & Release | ⬜ Planned |

## Credits

- Inspired by [Remere's Map Editor Redux](https://github.com/karolak6612/remeres-map-editor-redux) by @karolak6612
- Original RME by Remere and the OpenTibia community

## License

GPL-2.0-or-later. See [LICENSE](LICENSE).
