# GitHub Workflows

This directory owns repo automation. Keep workflow names stable because README
examples, Jules routing, and GitHub run history depend on them.

## Workflows

| File | Name | Main trigger | Notes |
|---|---|---|---|
| `ci.yml` | `CI` | push, pull request | Python 3.12 lane plus Rust lane |
| `jules-invoke.yml` | `Jules Invoke` | workflow dispatch, workflow call | Direct wrapper for `google-labs-code/jules-invoke@v1` |
| `jules-dispatch.yml` | `Jules Dispatch` | issue/PR comments, workflow dispatch | Accepts trusted `@jules /focus` comments |
| `jules-schedule.yml` | `Jules Area Schedule` | weekly schedule, workflow dispatch | Runs area lanes with a five-hour pause after the first five |
| `jules-maintenance.yml` | `Jules Maintenance` | workflow dispatch | Calls `Jules Invoke` with maintenance focus |
| `jules-ci-fix.yml` | `Jules CI Fix` | failed/timed-out CI workflow run | Sends failing CI context to `Jules Invoke` |
| `jules-uiux.yml` | `Jules UI/UX` | workflow dispatch | Sends visual/UI shell context to Jules |
| `jules-test.yml` | `Jules Test` | workflow dispatch | Sends verification context to Jules |
| `jules-system.yml` | `Jules System` | workflow dispatch | Sends repo automation context to Jules |

## Jules Requirements

- GitHub secret: `JULES_API_KEY`
- Action tag: `google-labs-code/jules-invoke@v1`
- Trusted comment associations: `OWNER`, `MEMBER`, `COLLABORATOR`

Supported comment forms:

```text
@jules
@jules /python
@jules /rust
@jules /bridge
@jules /review
@jules /test
@jules /utility
@jules /maintenance
@jules /ci
@jules /uiux
@jules /system
```

## Manual Dispatch

```bash
gh workflow run "Jules Invoke" \
  --repo Marcelol090/rme-noct \
  --ref main \
  -f focus=maintenance \
  -f starting_branch=main \
  -f additional_context="manual maintenance" \
  -f include_last_commit=true \
  -f include_commit_log=true
```

Focused wrappers are available when the GitHub Actions UI should show a lane:

```bash
gh workflow run "Jules UI/UX" --repo Marcelol090/rme-noct --ref main \
  -f starting_branch=main \
  -f additional_context="review dialog spacing and parity"

gh workflow run "Jules Test" --repo Marcelol090/rme-noct --ref main \
  -f starting_branch=main \
  -f additional_context="select the smallest useful verification slice"

gh workflow run "Jules System" --repo Marcelol090/rme-noct --ref main \
  -f starting_branch=main \
  -f additional_context="audit workflow and automation drift"
```

Scheduled area coverage lives in `Jules Area Schedule`. It runs five lanes in
hourly order, pauses five hours, then runs the remaining lanes:

| UTC cron | Focus |
|---|---|
| `0 0 * * 1` | `python` |
| `0 1 * * 1` | `rust` |
| `0 2 * * 1` | `bridge` |
| `0 3 * * 1` | `review` |
| `0 4 * * 1` | `test` |
| `0 10 * * 1` | `utility` |
| `0 11 * * 1` | `system` |
| `0 12 * * 1` | `uiux` |
| `0 13 * * 1` | `maintenance` |

Run one lane manually through the scheduler with:

```bash
gh workflow run "Jules Area Schedule" --repo Marcelol090/rme-noct --ref main \
  -f focus=python \
  -f starting_branch=main \
  -f additional_context="scheduled lane dry run"
```

## Validation

Before changing workflow behavior:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml

for path in sorted(Path(".github/workflows").glob("*.yml")):
    yaml.safe_load(path.read_text(encoding="utf-8"))
    print(f"yaml-ok: {path}")
PY
```

Then use `gh workflow list --all --repo Marcelol090/rme-noct` after merge to
confirm workflows are active.
