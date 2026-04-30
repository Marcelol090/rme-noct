# AGENTS.md — rme-noct

## Environment
- WSL2 / Linux only. Always `python3`, never `python`.
- Health check at session start:
```bash
python3 -m pyrme stack --quiet && gh auth status
```
- Preflight before any GSD auto-run: `npm run preflight`

## Testing
- Python: `python3 -m pytest tests/python/ -q --tb=short`
- Run slice-relevant path before marking any task done.
- Tests first, implementation second — always.

## GSD Loop (mandatory entry point every session)
```bash
cat .gsd/STATE.md
cat .gsd/milestones/M###/M###-CONTEXT.md
cat .gsd/milestones/M###/slices/S##/S##-PLAN.md
```

1. Confirm slice stop condition before touching code.
2. `use_skill("caveman-review")` on diff before any commit.
3. Gap found → fix → re-review → only advance when clean.
4. `use_skill("caveman")` closeout → `use_skill("superpowers:yeet")`
5. Write `T##-SUMMARY.md` → mark `[x]` in `S##-PLAN.md` → update `STATE.md`

**Never commit with gap. Never stub. Never yeet before caveman-review is clean.**

## Superpowers Skills — invocation rules
- `using-superpowers` is auto-injected at session start. Do NOT invoke manually.
- **1% Rule:** if there is even a 1% chance a skill applies, invoke it. Mandatory.
- If dispatched as subagent to execute a specific task, skip `using-superpowers`.
- Personal skills path: `~/.agents/skills/` (not `~/.codex/skills/` — deprecated)
- `using-git-worktrees` is required before any implementation start.
- Context isolation: subagents receive only the context for their specific task.

| Skill | When |
|---|---|
| `caveman` | Session context large / any closeout / terse review output |
| `caveman-review` | ALWAYS before commit — gap check on diff |
| `caveman-help` | Quick API/syntax question without opening large context |
| `superpowers:yeet` | After clean caveman-review — commit + push + PR |
| `superpowers:gh-address-comments` | PR receives review comments |
| `superpowers:gh-fix-ci` | Actions fail after push |
| `superpowers:subagent-driven-development` | Multi-task slice with parallel subagents |
| `superpowers:brainstorming` | New feature before any plan or code |
| `superpowers:writing-plans` | After brainstorming approval |
| `superpowers:test-driven-development` | Any implementation task (RED-GREEN-REFACTOR) |
| `superpowers:systematic-debugging` | Bug root cause — 4-phase process |
| `superpowers:requesting-code-review` | Before PR open |
| `superpowers:using-git-worktrees` | Required before implementation start |

## Caveman Mode — behavior spec
- **Trigger:** `/caveman` | "caveman mode" | "less tokens please"
- **Stop:** "stop caveman" | "normal mode"
- **Smash:** filler words, articles (a/an/the), pleasantries, hedging
- **Keep normal:** code blocks, technical terms (exact), error messages (exact), git commits, PRs

## Commits
- Branch: `gsd/M###/S##`
- Task: `{feat|fix|test|refactor|docs|perf|chore}(S##/T##): one-liner`
- Squash: `{type}(M###/S##): slice title`

## Architecture
- `pyrme/` — Python shell; project contract surface
- `pyrme/ui/` — PyQt6 UI; preserve dock/window patterns; see `pyrme/ui/AGENTS.md`
- `rme/` (C++) — legacy reference implementation at:
  `/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/remeres-map-editor-redux`
  **Ground truth for all behavior contracts. Match it. When in doubt, read it.**
- Edits surgical only — never widen scope without updating plan

## Third-party Libraries — Context7 MCP (mandatory)
Never use memory or web search for library API details. Always:

1. `resolve-library-id` → `get-library-docs` via Context7 MCP
2. Pin the exact version (e.g., PyQt6, pytest) when resolving
3. Read the official API, not tutorials or StackOverflow
4. If docs conflict with legacy `rme/` behavior, legacy wins — document the divergence in code comment
5. Cache the relevant snippet in the task summary when API is non-obvious
