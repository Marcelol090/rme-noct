---
name: pyrme-context
description: Load this at the start of every task or session to anchor the PyRME contract, architecture split, workflow ownership, and local skill directories.
---

# PyRME Project Context

## Core Contract

PyRME is a ground-up rewrite of [Remere's Map Editor](https://github.com/karolak6612/remeres-map-editor-redux) targeting full feature parity with **RME Extended Edition 3.8**.

Behavioral parity is defined by the legacy redux C++ source tree at `remeres-map-editor-redux/source/`. New implementations should preserve that contract before introducing structural improvements.

The project follows a split architecture:

- **Codex** is the orchestrator and subagent router.
- **Superpowers** provides workflow discipline and reusable local skills.
- **GSD 2** provides worktree isolation, milestone tracking, and verification commands.
- **Context7** is the source of truth for official third-party documentation and terminology.

## Architecture Overview

```text
Python UI layer
- menus, dialogs, docks, preferences, devtools
- editor interaction and presentation

PyO3 bridge
- thin boundary for structured data exchange

Rust core (`rme_core`)
- map model, file I/O, search, rendering, and concurrency-heavy logic
```

## Stack

- Python 3.12+ / PyQt6 for the user-facing editor shell
- Rust via PyO3 + maturin for performance-sensitive logic
- wgpu for GPU canvas rendering
- rayon for parallel processing
- serde for serialization and structured data exchange

## Workflow Ownership

- Codex owns runtime orchestration, subagent routing, and local execution.
- Superpowers owns workflow discipline, including planning, worktree usage, execution slices, review, and branch closeout.
- GSD 2 owns `.gsd/preferences.md`, `git.isolation: worktree`, and `verification_commands`.
- Context7 should be checked before relying on any external tool, library, or agent workflow behavior.

## Skill Directories

- `.agent/skills/` - legacy repo-local context helpers still tracked in this repo
- `.agent/workflows/` - repo-local Codex workflow docs
- `.agents/skills/` - repo-local official Codex skills
- `.pi/agent/skills/` - project-scope GSD skills
- `~/.agents/skills/` - user-scope installed skills
- `.gsd/` - GSD preferences, milestones, and task registry

## Mandatory Checklist

Before any implementation or documentation change:

1. Check Context7 for the official docs that apply to the task.
2. Reference the legacy C++ implementation at `remeres-map-editor-redux/source/` when behavior parity matters.
3. Use the GSD 2 worktree and verification contract for multi-step work.
4. Keep Python on the visual shell path and Rust on the performance path.

## Conventions

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Python: ruff and mypy
- Rust: clippy and cargo fmt
- Tests: pytest for Python, cargo test for Rust
- UI: keep the shell visually intentional, but do not move performance-sensitive logic out of Rust

## Key Files

- `README.md` - repo overview and setup contract
- `pyproject.toml` - Python build config
- `Cargo.toml` - Rust workspace
- `crates/rme_core/` - Rust core library
- `pyrme/` - Python package
- `.gsd/preferences.md` - GSD 2 configuration
- `.pi/agent/skills/` - project-scope GSD 2 skills
