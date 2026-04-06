# Tier 2 Docks & Dialogs Workflow

## Purpose
This document is the orchestration layer for the Tier 2 milestone. It exists to keep GSD workflow context separate from component-level implementation specs.

## Active Milestone
- Tier 2 Docks & Dialogs
- Source plan: `docs/superpowers/plans/2026-04-05-tier2-docks.md`

## Required Workflow
1. Start from a committed project base that includes the current repo state and these Tier 2 planning artifacts.
2. Use `gsd --worktree` from the committed base to create an isolated implementation workspace.
3. Execute Tier 2 in this order:
   - QSS and token verification
   - Map Properties
   - Find Item
   - Waypoints and Layers
   - Widget tests and regressions
4. Keep component requirements in their dedicated spec files. Do not mix implementation details back into this workflow document.

## GSD Usage
- Preferences authority: `.gsd/preferences.md`
- Git isolation mode: `worktree`
- Use the shell `gsd` command from a Node 22+ runtime
- If GSD cannot run because the runtime is not available, provision the runtime first, then rerun GSD before implementation starts

## Verification Gates
- Before implementation: baseline repo state committed, worktree created, dependencies and runtime validated
- During implementation: follow TDD for each behavior slice
- After implementation:
  - `pytest tests/python -v --tb=short`
  - `ruff check pyrme/`
  - `mypy pyrme/ --ignore-missing-imports`

## Review Flow
1. Finish implementation in the isolated worktree
2. Run full verification
3. Review diff against the Tier 2 specs
4. Request code review
5. Only then merge/finish the worktree branch
