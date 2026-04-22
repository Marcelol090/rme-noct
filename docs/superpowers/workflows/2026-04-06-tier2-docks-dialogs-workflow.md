# Tier 2 Docks and Dialogs Workflow

## Purpose

This document is the milestone-local orchestration layer for Tier 2. It keeps GSD workflow context separate from component-level implementation specs.

Repo-wide workflow ownership is defined in `docs/superpowers/workflows/2026-04-06-codex-first-superpowers-gsd.md`.
This file only covers milestone-local sequencing and verification.

## Active Milestone

- Tier 2 Docks and Dialogs
- Source plan: `docs/superpowers/plans/2026-04-05-tier2-docks.md`
- Behavior reference: `remeres-map-editor-redux/source/`

## Required Workflow

1. Start from a committed project base that includes the current repo state and these Tier 2 planning artifacts.
2. Use GSD to create an isolated worktree before implementation begins.
3. Have Codex orchestrate the work as explicit subagents when a slice is parallelizable:
   - one agent for the Python visual shell
   - one agent for Rust-facing performance work
   - one agent for docs or contract validation
4. Execute Tier 2 in this order:
   - QSS and token verification
   - Map Properties
   - Find Item
   - Waypoints and Layers
   - Widget tests and regressions
5. Keep component requirements in their dedicated spec files. Do not mix implementation details back into this workflow document, and use the legacy C++ source as the behavior reference whenever Tier 2 already exists there.

## GSD Usage

- Preferences authority: `.gsd/preferences.md`
- Git isolation mode: `git.isolation: worktree`
- Use the local `gsd` command from the Node.js 22+ toolchain
- If GSD cannot run because the runtime is not available, provision the runtime first, then rerun GSD before implementation starts

## Verification Gates

- Before implementation: baseline repo state committed, worktree created, dependencies and runtime validated
- During implementation: add or update tests for each legacy behavior slice before calling it complete
- After implementation:
  - `pytest tests/python -v --tb=short`
  - `ruff check pyrme/`
  - `mypy pyrme/ --ignore-missing-imports`

## Review Flow

1. Finish implementation in the isolated worktree
2. Run full verification
3. Review diff against the Tier 2 specs
4. Request code review
5. Only then merge or finish the worktree branch
