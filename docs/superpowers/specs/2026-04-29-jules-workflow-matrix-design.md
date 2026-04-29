# Jules Workflow Matrix Design

## Goal

Expose Jules through clear GitHub Actions entrypoints for UI/UX, test, and system work while preserving the existing shared `Jules Invoke` runner.

## Approach

Use one reusable workflow, `.github/workflows/jules-invoke.yml`, as the single prompt renderer and action caller. Add explicit `uiux`, `test`, and `system` focus routing there, then add small wrapper workflows that call it with fixed focus values.

## Components

- `.jules/newagents/uiux.md`: UI/UX specialist contract. Requires legacy parity, Stitch/Figma evidence for UI design work, PyQt6 conventions, and targeted UI tests.
- `.jules/newagents/system.md`: system/workflow specialist contract. Owns GitHub Actions, repo automation, GSD/Codex/Jules glue, and verification contracts.
- `.github/workflows/jules-uiux.yml`: manual UI/UX workflow. Calls `Jules Invoke` with `focus=uiux`.
- `.github/workflows/jules-test.yml`: manual and scheduled verification workflow. Calls `Jules Invoke` with `focus=test`.
- `.github/workflows/jules-system.yml`: manual and scheduled system workflow. Calls `Jules Invoke` with `focus=system`.
- `.github/workflows/jules-dispatch.yml`: accepts `@jules /uiux`, `@jules /test`, and `@jules /system` comment routes.
- `.github/workflows/README.md` and `README.md`: document new focus values and workflow commands.

## Data Flow

Manual dispatch or trusted comment chooses a focus. Wrapper workflows set `focus`, `starting_branch`, and `additional_context`, then call `jules-invoke.yml`. `jules-invoke.yml` maps focus to the matching `.jules/newagents/*.md` prompt and sends that rendered prompt to `google-labs-code/jules-invoke@v1.0.0`.

## Error Handling

Unknown focus remains supported through the existing `auto` fallback prompt. Wrapper workflows pass fixed known focuses. Comment dispatch rejects comments that do not match the allowed focus regex or trusted author associations.

## Testing

Add Python contract tests that parse workflow YAML, verify dispatch choices and comment regex, verify `jules-invoke.yml` prompt routing, and verify every new workflow calls the reusable invoke workflow with the intended focus.
