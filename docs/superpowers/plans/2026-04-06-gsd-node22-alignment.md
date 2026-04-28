# GSD, Node.js 22, and Workflow Alignment Plan

> For agentic workers: use `superpowers:writing-plans` to refine this plan, then use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement it task by task.

**Goal:** Align the repo documentation and local setup text with the official GSD, Superpowers, OpenAI, and Jules terminology already validated in Context7, while keeping runtime behavior unchanged.

**Architecture:** Codex is the orchestrator, Superpowers is the workflow discipline layer, GSD 2 is the worktree and verification layer, and Context7 is the documentation source. The editor remains Rust-first for performance and Python-visual for the user-facing shell. Behavioral parity remains anchored to the legacy redux C++ source tree.

**Tech Stack:** Node.js 22, npm, Python 3.12+, PyQt6, Rust, PyO3, maturin

---

## Task 1: Normalize the local GSD contract in docs

**Files:**
- Modify: `README.md`
- Modify: `scripts/setup-devtools.sh`

- [ ] Update README wording to say `RME Extended Edition 3.8`, `Node.js 22+`, and local `gsd` usage from `node_modules`.
- [ ] Replace any remaining `gsd-pi` wording with the repo-local GSD wrapper contract.
- [ ] Keep the setup script focused on bootstrap and verification text only.

## Task 2: Make the multi-agent story explicit

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/workflows/2026-04-06-codex-first-superpowers-gsd.md`

- [ ] State clearly that Codex orchestrates subagents.
- [ ] State clearly that Superpowers supplies workflow discipline and reusable skills.
- [ ] State clearly that GSD owns worktree isolation and verification commands.
- [ ] State clearly that Context7 is the source for official docs and terminology.

## Task 3: Document the Rust-first / Python-visual split

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/workflows/2026-04-06-tier2-docks-dialogs-workflow.md`

- [ ] Add a short architecture note that Python stays focused on the visible shell.
- [ ] Add a short architecture note that Rust owns performance-sensitive logic.
- [ ] Keep this documentation-only and avoid changing runtime behavior.

## Task 4: Keep the workflow guidance aligned with GSD

**Files:**
- Modify: `docs/superpowers/workflows/2026-04-06-tier2-docks-dialogs-workflow.md`
- Modify: `docs/superpowers/workflows/2026-04-06-codex-first-superpowers-gsd.md`

- [ ] Use `.gsd/preferences.md`, `git.isolation: worktree`, and `verification_commands` as the canonical GSD terms.
- [ ] Keep the workflow sequencing centered on planning, isolated execution, verification, review, and branch closeout.

## Notes

- This plan is documentation and setup text only.
- Do not change runtime behavior in this pass.
- Do not reintroduce stale `gsd-pi` wording.
