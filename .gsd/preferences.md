---
version: 1

# ── Model Selection ──────────────────────────────────────────
# Per GSD-2 docs: configure models for each phase
models:
  research: claude-sonnet-4-6
  planning:
    model: claude-opus-4-6
    fallbacks:
      - openrouter/z-ai/glm-5
      - openrouter/minimax/minimax-m2.5
  execution: claude-sonnet-4-6
  completion: claude-sonnet-4-6

# ── Token Optimization ──────────────────────────────────────
token_profile: balanced

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
skill_discovery: suggest
skill_staleness_days: 60
unique_milestone_ids: true
always_use_skills:
  - debug-like-expert
prefer_skills:
  - frontend-design
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

# PyRME – GSD-2 Project Preferences

## Project Context
- **Stack**: Python 3.12+ / PyQt6 / Rust (PyO3 + maturin)
- **Domain**: Tibia map editor (OTBM format)
- **Performance Target**: 60+ FPS on 512x512 maps
- **Parity Target**: RME Extended Edition 3.8

## Conventions
- Conventional commits (feat/fix/refactor/test/docs)
- TDD-first approach via Superpowers skills
- Context7 MCP for all documentation lookups
- Stitch for UI mockups before implementation

## Key Architecture Decisions
- All performance-critical code in Rust (canvas, parsing, spatial hash, hashing)
- Python handles UI, preferences, file dialogs, user interaction
- PyO3 bridge with zero-copy where possible
- FNV-1a 64-bit for sprite hash matching (cross-instance clipboard)
