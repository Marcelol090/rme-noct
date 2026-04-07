# Codex-First Superpowers + GSD Workflow Contract

## Runtime Ownership

- `Codex/OpenAI` is the primary runtime contract for this repo.
- `AGENTS.md`, `config.toml`, MCP wiring, skills, subagents, and workflow surfaces follow Codex semantics first.
- `Context7` is the required documentation source for third-party tools and libraries.

## Workflow Ownership

- `Superpowers` is the workflow-discipline layer, not a replacement runtime.
- The required sequence is:
  - `using-superpowers`
  - `brainstorming`
  - `using-git-worktrees`
  - `writing-plans`
  - `subagent-driven-development` or `executing-plans`
  - `test-driven-development`
  - `requesting-code-review`
  - `finishing-a-development-branch`
- In Codex, subagents are explicit. When a Superpowers workflow calls for subagents, Codex must spawn them intentionally rather than assuming automatic fan-out.

## Orchestration Ownership

- `GSD 2` starts after spec and plan approval.
- `GSD 2` owns:
  - milestone/worktree isolation
  - status and progress tracking
  - budget and supervision policy
  - verification commands
  - skill routing hints in `.gsd/preferences.md`
- `GSD` skill rules are routing metadata only. They must point toward the same skills Codex already knows how to use.

## Example End-to-End Chain

1. Load Codex runtime context:
   - `AGENTS.md`
   - `config.toml`
   - active MCP servers
   - repo-local docs
2. Use Superpowers to define the work:
   - brainstorm the design
   - write the implementation plan
3. Start the milestone in `GSD 2`:
   - assign the milestone ID
   - create the isolated worktree
   - track progress and verification
4. Execute inside Codex:
   - inline for small slices
   - explicit subagents for parallelizable plan tasks
5. Finish with both:
   - Superpowers review and branch-close workflow
   - Codex-native verification and review workflow

## References

- Superpowers via Context7: `/obra/superpowers`
- GSD 2 via Context7: `/gsd-build/gsd-2`
- Codex docs:
  - `https://developers.openai.com/codex/guides/agents-md`
  - `https://developers.openai.com/codex/mcp`
  - `https://developers.openai.com/codex/skills`
  - `https://developers.openai.com/codex/subagents`
  - `https://developers.openai.com/codex/workflows`
