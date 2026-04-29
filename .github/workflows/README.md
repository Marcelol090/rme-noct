# GitHub Workflows

This directory owns repo automation. Keep workflow names stable because README
examples, Jules routing, and GitHub run history depend on them.

## Workflows

| File | Name | Main trigger | Notes |
|---|---|---|---|
| `ci.yml` | `CI` | push, pull request | Python 3.12 lane plus Rust lane |
| `jules-invoke.yml` | `Jules Invoke` | workflow dispatch, workflow call | Direct wrapper for `google-labs-code/jules-invoke@v1.0.0` |
| `jules-dispatch.yml` | `Jules Dispatch` | issue/PR comments, workflow dispatch | Accepts trusted `@jules /focus` comments |
| `jules-maintenance.yml` | `Jules Maintenance` | weekly schedule, workflow dispatch | Calls `Jules Invoke` with maintenance focus |
| `jules-ci-fix.yml` | `Jules CI Fix` | failed/timed-out CI workflow run | Sends failing CI context to `Jules Invoke` |
| `jules-uiux.yml` | `Jules UI/UX` | workflow dispatch | Sends visual/UI shell context to Jules |
| `jules-test.yml` | `Jules Test` | weekly schedule, workflow dispatch | Sends verification context to Jules |
| `jules-system.yml` | `Jules System` | weekly schedule, workflow dispatch | Sends repo automation context to Jules |

## Jules Requirements

- GitHub secret: `JULES_API_KEY`
- Action tag: `google-labs-code/jules-invoke@v1.0.0`
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
