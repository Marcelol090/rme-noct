# Noct Map Editor

<p align="center">
  <strong>Python + Rust Remere's Map Editor rewrite targeting Extended Edition 3.8 parity</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Rust-2021-orange?logo=rust&logoColor=white" />
  <img src="https://img.shields.io/badge/UI-PyQt6-green?logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/GPU-wgpu-purple?logo=webgpu&logoColor=white" />
  <img src="https://img.shields.io/badge/License-GPL--2.0-red" />
</p>

## Project State

Noct Map Editor is a ground-up rewrite of
[Remere's Map Editor Redux](https://github.com/karolak6612/remeres-map-editor-redux).
The current repo has the Python shell, Rust core seams, sprite asset discovery,
SPR/DAT parsing slices, the startup Welcome Dialog, and Jules automation wired
into GitHub Actions.

Legacy behavior still wins. The nested `remeres-map-editor-redux/` tree is a
reference implementation, not the active project root. When behavior is unclear,
read legacy C++ first, then encode the contract in tests.

## Stack

| Layer | Tech | Responsibility |
|---|---|---|
| UI shell | Python 3.12, PyQt6 | menus, dialogs, docks, canvas host, workflow glue |
| Core bridge | PyO3, maturin | typed Python/Rust boundary |
| Rust core | Rust 2021 | map model, parsing, file I/O, renderer data, performance paths |
| Renderer path | Python contracts now, wgpu target | frame plans, sprite resources, future GPU draw path |
| Automation | GSD, Superpowers, Jules, GitHub Actions | slice planning, worktrees, CI, repair/maintenance agents |

## Quick Start

Use WSL2/Linux for development. The repo contract assumes `python3`, not
Windows `python`. Node.js 22+ is required for local GSD tooling.

```bash
git clone https://github.com/Marcelol090/rme-noct.git
cd rme-noct

npm install
npm run preflight

python3 -m venv .venv
source .venv/bin/activate
pip install maturin
maturin develop
pip install -e ".[dev]"
```

`npm install` runs the `postinstall` hook, which patches the local `gsd-pi`
runtime. Keep `GSD_HOME` repo-local when using automation so generated sessions
and extensions stay isolated from global tools.

Launch:

```bash
python3 -m pyrme
```

Core verification:

```bash
python3 -m pyrme stack --quiet
npm run preflight
python3 -m pytest tests/python/ -q --tb=short
cargo test --manifest-path crates/rme_core/Cargo.toml
```

## Development Contract

Root instructions live in [AGENTS.md](AGENTS.md). Treat it as the repo-level
contract before changing code.

- Use git worktrees for feature work.
- Keep slices narrow and test-first.
- Read active `.gsd/STATE.md` plus the current milestone/slice docs before
  moving GSD state.
- Use Context7 or official docs for third-party API details.
- Codex/OpenAI is the primary orchestration layer; Superpowers supplies local
  workflow gates, GSD 2 stores slice state, and Context7 is the library-docs
  source of truth.
- Preserve legacy `rme/` behavior when docs, generated designs, or new code
  disagree with the reference implementation.
- Run the smallest relevant test path before marking a task done.

## GSD Workflow

Common commands:

```bash
npm run gsd:status
npm run gsd:plan -- "Plan the next milestone"
npm run gsd:auto
gsd headless query
gsd headless new-milestone --context-text
```

`npm run gsd:auto` runs `npm run preflight` first. If preflight fails, fix the
baseline blocker before trusting autonomous mode.

Milestone docs live under `.gsd/milestones/`. Active sprite and editor-shell
history currently includes:

| Area | Milestones |
|---|---|
| Renderer frame/canvas | `M003`, `M004`, `M005` |
| Sprite lookup/draw pipeline | `M006` through `M014`, `M019` through `M021` |
| UI shell and tools | item palette, brush activation, Welcome Dialog |
| Future renderer | WGPU sprite renderer planning lives in later milestone docs |

## GitHub Actions

| Workflow | Trigger | Purpose |
|---|---|---|
| `CI` | push, pull request | Python 3.12 tests and Rust tests |
| `Jules Invoke` | workflow dispatch, reusable workflow call | direct Jules task execution |
| `Jules Dispatch` | trusted issue/PR comments, workflow dispatch | route `@jules /focus` requests |
| `Jules Maintenance` | weekly schedule, workflow dispatch | scheduled maintenance prompt |
| `Jules CI Fix` | failed/timed-out CI workflow runs, workflow dispatch | route failing CI context to Jules |

The Jules action is pinned to `google-labs-code/jules-invoke@v1.0.0` because
the upstream repo publishes `v1.0.0`, not `v1`.

Manual Jules examples:

```bash
gh workflow run "Jules Invoke" \
  --repo Marcelol090/rme-noct \
  --ref main \
  -f focus=maintenance \
  -f starting_branch=main \
  -f additional_context="post-merge maintenance" \
  -f include_last_commit=true \
  -f include_commit_log=true
```

Trusted comments also work on issues and PRs:

```text
@jules /python investigate the failing PyQt test
@jules /rust inspect the rme_core parsing path
@jules /bridge review PyO3 boundary changes
@jules /maintenance check repo hygiene
@jules /ci fix the latest failing Actions run
```

Set `JULES_API_KEY` in GitHub Actions secrets before relying on these workflows.

## Current Feature Surface

- Legacy menu contracts and shell state seams
- PyQt6 docks and dialogs, including item palette and Welcome Dialog
- Renderer frame plan and diagnostic tile primitives
- Sprite catalog, resolver, asset provider, draw command, DAT metadata, SPR
  frame table, and compressed payload parsing
- Rust core modules for map, item, editor, file I/O, and OTBM/XML sidecar work
- GSD/Superpowers/Codex/Jules automation assets

## Repository Layout

```text
pyrme/                 Python editor shell and devtools
pyrme/ui/              PyQt6 UI, docks, dialogs, canvas host
pyrme/rendering/       renderer contracts, frame plans, sprite seams
crates/rme_core/       Rust core crate
.gsd/                  GSD state, milestones, slice plans
.github/workflows/    CI and Jules workflows
.jules/                Jules prompt agents
docs/superpowers/      workflow and planning docs
```

## License

GPL-2.0-or-later. See [LICENSE](LICENSE).

## Credits

- Original RME by Remere and the OpenTibia community
- Redux reference by @karolak6612
