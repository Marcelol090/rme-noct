# Jules Workflow Matrix Design

## Goal

Expose Jules through clear GitHub Actions entrypoints for UI/UX, test, system, maintenance, CI, and scheduled area work while preserving the existing shared `Jules Invoke` runner.

## Approach

Use one reusable workflow, `.github/workflows/jules-invoke.yml`, as the single prompt renderer and action caller. Add explicit focus routing for every Jules lane that has a reusable agent contract, then keep small wrapper workflows for manual lanes and one central scheduled workflow for periodic area coverage.

## Components

- `.jules/newagents/uiux.md`: UI/UX specialist contract. Requires legacy parity, Stitch/Figma evidence for UI design work, PyQt6 conventions, and targeted UI tests.
- `.jules/newagents/system.md`: system/workflow specialist contract. Owns GitHub Actions, repo automation, GSD/Codex/Jules glue, and verification contracts.
- `.jules/newagents/maintenance.md`: upkeep specialist contract. Owns narrow cleanup, docs drift, and repo hygiene.
- `.jules/newagents/ci.md`: failure repair specialist contract. Owns failing GitHub Actions runs and minimal CI fixes.
- `.github/workflows/jules-schedule.yml`: weekly area scheduler. Runs python, rust, bridge, review, and test hourly, waits five hours, then runs utility, system, UI/UX, and maintenance.
- `.github/workflows/jules-uiux.yml`: manual UI/UX workflow. Calls `Jules Invoke` with `focus=uiux`.
- `.github/workflows/jules-test.yml`: manual verification workflow. Calls `Jules Invoke` with `focus=test`.
- `.github/workflows/jules-system.yml`: manual system workflow. Calls `Jules Invoke` with `focus=system`.
- `.github/workflows/jules-dispatch.yml`: accepts `@jules /uiux`, `@jules /test`, and `@jules /system` comment routes.
- `.github/workflows/README.md` and `README.md`: document new focus values and workflow commands.

## Data Flow

Manual dispatch, trusted comment, or scheduled lane chooses a focus. Wrapper workflows set `focus`, `starting_branch`, and `additional_context`, then call `jules-invoke.yml`. `jules-schedule.yml` maps the cron that fired to one area focus using `github.event.schedule`, adds the schedule context, and calls the reusable workflow. `jules-invoke.yml` maps focus to the matching `.jules/newagents/*.md` prompt and sends that rendered prompt to `google-labs-code/jules-invoke@v1`.

## Error Handling

Unknown focus remains supported through the existing `auto` fallback prompt. Wrapper workflows pass fixed known focuses. Comment dispatch rejects comments that do not match the allowed focus regex or trusted author associations.

## Testing

Add Python contract tests that parse workflow YAML, verify dispatch choices and comment regex, verify `jules-invoke.yml` prompt routing, verify every new workflow calls the reusable invoke workflow with the intended focus, and verify the area scheduler covers every periodic lane with the required five-hour pause after the first five schedules.
