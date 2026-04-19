---
version: 1

# ── Model Selection ──────────────────────────────────────────
# Local-first runtime: prefer the installed lightweight Ollama coder model for default phases
models:
  research: ollama/qwen3-8b-gsd
  planning: ollama/qwen3-8b-gsd
  execution: ollama/qwen3-8b-gsd
  completion: ollama/qwen3-8b-gsd

# Keep search local when the planner needs web-style lookup
search_provider: ollama

# Keep milestone planning lean and local-first
phases:
  skip_research: true
  skip_slice_research: true
  skip_reassess: true

# ── Token Optimization ──────────────────────────────────────
token_profile: budget

# ── Budget ───────────────────────────────────────────────────
budget_ceiling: 50.00
budget_enforcement: pause
context_pause_threshold: 80

# ── Supervision ──────────────────────────────────────────────
auto_supervisor:
  soft_timeout_minutes: 20
  idle_timeout_minutes: 10
  hard_timeout_minutes: 30

# ── Git Integration ──────────────────────────────────────────
git:
  auto_push: true
  merge_strategy: squash
  isolation: worktree
  commit_docs: true

# ── Skill Management ────────────────────────────────────────
skill_discovery: off
skill_staleness_days: 60
unique_milestone_ids: true
always_use_skills:
  - debug-like-expert
prefer_skills:
  - superpowers
  - frontend-design
  - caveman-commit
  - caveman-review
  - compress
avoid_skills:
  - aggressive-refactor
skill_rules:
  - when: task involves PyQt6 UI
    use: [frontend-design]
  - when: task involves Rust core or PyO3
    prefer: [systems-programming]
  - when: working with OTBM/OTB/DAT/SPR parsing
    use: [binary-formats]
  - when: performance optimization or profiling
    use: [profiling]
  - when: debugging or troubleshooting
    use: [debug-like-expert]
  - when: task involves cross-instance clipboard
    use: [binary-formats, systems-programming]
  - when: preparing commit messages or branch closeout
    use: [caveman-commit]
  - when: reviewing diffs or PR findings
    use: [caveman-review]
  - when: compressing memory files or workflow docs
    use: [compress]

# ── Verification Commands (Python + Rust) ────────────────────
# Per GSD-2 docs: these run after each task completion
verification_commands:
  - pytest tests/ -v --tb=short
  - ruff check pyrme/
  - mypy pyrme/ --ignore-missing-imports
  - cargo test --manifest-path crates/rme_core/Cargo.toml

# ── Notifications ────────────────────────────────────────────
notifications:
  on_complete: false
  on_milestone: true
  on_attention: true

# ── Visualizer ───────────────────────────────────────────────
auto_visualize: true
auto_report: true

# ── Hooks ────────────────────────────────────────────────────
post_unit_hooks:
  - name: code-review
    after: [execute-task]
    prompt: "Review {sliceId}/{taskId} for quality, security, and PyO3 API correctness."
    artifact: REVIEW.md
  - name: lint-check
    after: [execute-task]
    prompt: "Run ruff and mypy on changed files."
---

# PyRME - GSD-2 Project Preferences

## Project Context
- **Stack**: Python 3.12+ / PyQt6 / Rust (PyO3 + maturin)
- **Domain**: Tibia map editor (OTBM format)
- **Performance Target**: 60+ FPS on 512x512 maps
- **Parity Target**: RME Extended Edition 3.8

## Conventions
- Conventional commits (feat/fix/refactor/test/docs)
- Codex/OpenAI is the primary runtime contract
- Superpowers provides workflow discipline before and after coding
- GSD starts after spec and plan approval and manages milestone orchestration
- TDD-first approach via Superpowers skills
- Context7 MCP for all documentation lookups
- Stitch for UI mockups before implementation

## Workflow Checklist
- Read `README.md`, `PLAN.md`, active spec/plan docs, and `.gsd/STATE.md` before changing scope.
- Confirm slice stop condition before coding.
- Add or tighten tests before implementation.
- Keep delta narrow and contract-first.
- Verify narrow slice first, then adjacent regressions if the seam changed.
- Use `superpowers` for plan/execution discipline.
- Use `caveman-review` for terse review closeout.
- Use `caveman-commit` for commit messages.
- Use `caveman-compress` only for workflow/docs compression.

## Key Architecture Decisions
- All performance-critical code in Rust (canvas, parsing, spatial hash, hashing)
- Python handles UI, preferences, file dialogs, user interaction
- PyO3 bridge with zero-copy where possible
- FNV-1a 64-bit for sprite hash matching (cross-instance clipboard)
