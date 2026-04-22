# Codex, Superpowers, and GSD Workflow Contract

## Purpose

This document defines the repo's multi-agent operating model. Codex is the orchestrator, Superpowers supplies workflow discipline, GSD supplies worktree isolation and verification, and Context7 supplies the official documentation source. When behavior already exists in the legacy redux C++ tree, that source remains the behavioral authority.

## Runtime Ownership

- `Codex` is the operator and routing layer for subagents.
- `AGENTS.md`, `config.toml`, MCP wiring, skills, subagents, and workflow surfaces follow Codex semantics first.
- Optional Codex agent definitions may live in `~/.codex/agents/`.
- Installed Codex and project skills should be validated from `~/.agents/skills/`, `.agents/skills/`, and repo-local workflow docs.
- `Context7` is the required documentation source for third-party tools, libraries, and agent workflow terminology.

## Workflow Ownership

- `Superpowers` is the workflow-discipline layer, not a replacement runtime.
- The recommended sequence is:
  - `writing-plans`
  - `subagent-driven-development`
  - `using-git-worktrees`
  - `requesting-code-review`
  - `finishing-a-development-branch`
- Use `executing-plans` when the work is already decomposed and does not benefit from additional orchestration.
- When a task is parallelizable, Codex should dispatch subagents explicitly instead of pretending the fan-out is automatic.
- Verification is required for each slice, but it should be driven by the legacy contract and repo tests rather than by inventing a separate workflow layer.
- `caveman` handles closeout formatting:
  - `caveman-review` for terse review comments
  - `caveman-commit` for concise commit messages
  - `compress` for token-efficient memory/doc compression when needed

## Preferred Agent Topology

- Planning and coordination: one orchestrator agent using `writing-plans`.
- Parallel execution: up to eight `gpt-5.4-mini` worker agents using `subagent-driven-development`.
- Review and quality: up to two `gpt-5.4-mini` reviewer agents using `requesting-code-review` and evaluator passes.
- Utility tasks: lightweight `gpt-5.4-mini` agents for codebase lookup, API docs, and contract validation.
- Repo-local subagent contracts live in `.jules/newagents/` so repeat work does not need ad hoc prompts.
- The orchestrator owns final merge decisions and keeps the work scoped to one active plan.

## Orchestration Ownership

- `GSD` starts after the plan is approved.
- `GSD` owns:
  - milestone and worktree isolation
  - status and progress tracking
  - budget and supervision policy
  - verification commands
  - routing hints in `.gsd/preferences.md`
- Durable task memory lives in `.gsd/task-registry.json` and follows `.gsd/task-registry.schema.json`; update it as tasks complete so future sessions can see what has already been done.
- `git.isolation: worktree` is the standard execution mode.

## Implementation Split

- Python should stay focused on the visible editor shell: menus, dialogs, docks, preferences, and interaction wiring.
- Rust should own performance-sensitive work: parsing, map data, search, rendering, and concurrency-heavy logic.
- Keep the Python side responsive by pushing long-running work into Rust threads, worker pools, or background tasks.

## Example End-to-End Chain

1. Load Codex runtime context:
   - `AGENTS.md`
   - `config.toml`
   - active MCP servers
   - repo-local docs
2. Use Context7 to validate the contract for any external tool or library.
3. Use Superpowers to define the work:
   - write the plan
   - split the work into parallel slices when useful
4. Start the milestone in GSD:
   - assign the milestone ID
   - create the isolated worktree
   - track progress and verification
5. Execute inside Codex:
   - inline for small slices
   - explicit subagents for parallelizable tasks
6. Finish with both:
   - Superpowers review and branch-close workflow
   - Codex-native verification and review workflow

## References

- Superpowers via Context7: `/obra/superpowers`
- GSD via Context7: `/gsd-build/gsd-2`
- OpenAI docs via Context7: `/websites/developers_openai`
- Jules docs via Context7: `/websites/developers_google_jules`
