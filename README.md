# Noct Map Editor

<p align="center">
  <strong>Python + Rust Remere's Map Editor (Extended Edition 3.8)</strong>
</p>

<p align="center">
  A rewrite of the legacy C++ Remere's Map Editor with a Rust-first core and a Python-visual shell.
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

**Noct Map Editor** is a ground-up rewrite of [Remere's Map Editor](https://github.com/karolak6612/remeres-map-editor-redux) targeting full feature parity with **RME Extended Edition 3.8**.

Behavioral parity is defined by the legacy redux C++ source tree. New code should mirror that behavior first, then improve implementation quality only where the legacy contract is already preserved.

The split is intentional:

- **Python 3.12+ / PyQt6** for the visible editor shell: menus, dialogs, docks, preferences, and interaction wiring
- **Rust (PyO3 + maturin)** for the performance core: parsing, map data, search, rendering, and concurrency-sensitive work
- **wgpu** for GPU-accelerated canvas rendering

## Architecture

```text
Python UI layer
- menus, dialogs, docks, preferences, devtools
- canvas presentation and editor interaction

PyO3 bridge
- thin boundary for moving structured data between Python and Rust

Rust core (`rme_core`)
- map model, file I/O, search, rendering, and concurrency-heavy logic
```

## Quick Start

### Prerequisites

- Python 3.12+
- Rust via [rustup](https://rustup.rs/)
- Node.js 22+ for the local GSD toolchain

### Setup

```bash
git clone https://github.com/Marcelol090/rme-noct.git
cd rme-noct

# Install local devtools, including the repo-local GSD wrapper
npm install

# Validate the local preflight stack
npm run preflight

# Run the full setup (Python venv + Rust build + devtools)
bash scripts/setup-devtools.sh

# Or manual setup
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
npm run preflight
npm run stack
npm run gsd:status
npm run gsd:plan -- "Plan the next milestone"

# GSD autonomous mode
npm run gsd:auto
```

`npm run gsd:*` uses the repo-local `gsd` installation from `node_modules`, so Node.js 22+ and `npm install` are required before those commands will work.
`npm run preflight` is the human-readable alias for `npm run stack`; it validates the local Codex/GSD/Superpowers stack and treats local agent TOML files or a standalone `c7-mcp-server` binary as optional when the active Codex session already exposes agents and Context7 MCP tools.
The wrapper also forces `GSD_HOME` to the repo-local `.gsd/` directory before launching the CLI, which keeps the sync path writable even when the user home directory is read-only.
`npm install` also restores the local GSD wrapper contract through `postinstall`, which keeps startup reproducible across reinstalls.
`npm run gsd:status` uses `gsd headless query`, and `npm run gsd:plan -- "..."` creates a new milestone from inline context via `gsd headless new-milestone --context-text`.
`npm run gsd:auto` now runs `npm run preflight` first, so autonomous mode will abort if the local stack preflight fails.

## AI Workflow

This repo uses a multi-agent operating model:

- **Codex/OpenAI** is the orchestrator and routing layer for subagents.
- Optional Codex agent definitions may live in `~/.codex/agents/`:
  - `planner`
  - `worker`
  - `docs_researcher`
  - `reviewer`
- Codex skills are installed from `~/.agents/skills/` and may be supplemented by repo-local `.agents/skills/`; this workspace currently relies on installed Caveman/OpenAI/system skills plus the external frontend-skill reference when UI design work needs it.
- **Superpowers** provides workflow discipline through skills such as `writing-plans`, `subagent-driven-development`, `using-git-worktrees`, `requesting-code-review`, and `finishing-a-development-branch`; project-scope skills live in `.pi/agent/skills/`.
- **GSD 2** provides the worktree and verification layer through `.gsd/preferences.md`, `git.isolation: worktree`, and `verification_commands`.
- **Repository contract** lives in root `AGENTS.md` and is validated by `npm run preflight` / `python3 -m pyrme stack`.
- **Context7** is the required documentation source for third-party tools, libraries, and agent terminology; it can be exposed either as a Codex MCP tool or as a local command.
- **Jules** handles branch and PR automation through `.jules/agents/` and `.github/workflows/jules-*.yml`; set `JULES_API_KEY` in GitHub Secrets and use trusted `@jules /python`, `/rust`, `/bridge`, `/maintenance`, or `/ci` triggers.

The repo-wide contract and end-to-end example live in [docs/superpowers/workflows/2026-04-06-codex-first-superpowers-gsd.md](docs/superpowers/workflows/2026-04-06-codex-first-superpowers-gsd.md).

## Repository Contract

- Root `AGENTS.md` defines the repo-level working rules.
- `npm run preflight` and `python3 -m pyrme stack` validate the local Codex/GSD/Superpowers stack, including the repo contract.
- Read `README.md`, `PLAN.md`, and the active feature docs before changing behavior.
- Use Context7 or official docs for third-party API questions instead of guessing.
- Keep changes surgical and verify them with the smallest relevant test slice.

## Rust-First / Python-Visual Split

- Keep Python focused on the visible editor shell: menus, docks, dialogs, preferences, and interaction wiring.
- Move performance-sensitive work into Rust: parsing, map data, search, rendering, and concurrency-heavy operations.
- Use Rust threads, channels, and worker pools for long-running work so the Qt UI remains responsive.
- Treat Python as the presentation layer and Rust as the execution layer when adding new editor features.

## Features

- [ ] OTBM v0-v3 full read/write
- [ ] GPU-accelerated canvas (wgpu)
- [ ] All brush types (Ground, Wall, Border, Door, etc.)
- [ ] Auto-border with configurable rules
- [ ] Selection and clipboard
- [ ] Undo/redo with unlimited history
- [ ] Live editing
- [ ] In-game preview
- [ ] Shader system (AA, CRT, 4xBRZ)
- [ ] AI-assisted development using GSD and Superpowers

## Milestones

| # | Milestone | Status |
|---|---|---|
| 1 | Project Scaffolding & Build System | In Progress |
| 2 | Rust Core Data Structures | Planned |
| 3 | File I/O (OTBM/OTB/DAT/SPR) | Planned |
| 4 | Canvas Renderer (wgpu) | Planned |
| 5 | Editor Shell & Navigation | Planned |
| 6 | Brush Engine | Planned |
| 7 | Selection & Clipboard | Planned |
| 8 | Dialogs & Properties | Planned |
| 9 | Advanced Features | Planned |
| 10 | Polish & Release | Planned |

## Credits

- Inspired by [Remere's Map Editor Redux](https://github.com/karolak6612/remeres-map-editor-redux) by @karolak6612
- Original RME by Remere and the OpenTibia community

## License

GPL-2.0-or-later. See [LICENSE](LICENSE).
