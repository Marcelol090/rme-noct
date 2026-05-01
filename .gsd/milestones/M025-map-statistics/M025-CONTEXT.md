# M025 Map Statistics Context

## Mission

Turn `Map -> Statistics` from a safe explicit gap into a real read-only dialog
fed by Rust map-domain data.

## Base

- Branch: `gsd/M025/S01-m018-base`
- Base commit: `gsd/M018/S01`
- Reason: `origin/main` does not yet contain the full `MapModel` tile,
  waypoint, spawn, and house sidecar domains required by this slice.

## Source Of Truth

- Design: `.gsd/milestones/M025-map-statistics/DESIGN.md`
- Legacy menu action: `pyrme/assets/contracts/legacy/menubar.xml`
- Existing menu contract: `pyrme/ui/legacy_menu_contract.py`
- Rust map domain: `crates/rme_core/src/map.rs`
- Shell bridge: `crates/rme_core/src/editor.rs`, `pyrme/core_bridge.py`
- UI shell action: `pyrme/ui/main_window.py`

## Guardrails

- Do not implement cleanup actions.
- Do not mutate maps.
- Do not invent town model behavior; count distinct `house.townid()` only.
- Do not touch renderer, sprite, viewport, persistence readback, or root dirty
  checkout.
- Keep fallback behavior honest: missing native stats provider returns `None`;
  dialog labels remain zero.

## Verification Commands

Use WSL. Build a temporary Python 3.12 venv outside the repo if `.venv` is a
Windows venv:

```bash
rm -rf /tmp/rme-noct-m025-py312
uv venv --python 3.12 /tmp/rme-noct-m025-py312
uv pip install --python /tmp/rme-noct-m025-py312/bin/python -e '.[dev]'
```

Run:

```bash
npm run preflight --silent
QT_QPA_PLATFORM=offscreen /tmp/rme-noct-m025-py312/bin/python -m pytest tests/python/test_map_statistics_dialog.py tests/python/test_legacy_map_menu.py -q --tb=short
PYO3_PYTHON=/tmp/rme-noct-m025-py312/bin/python \
LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:$LD_LIBRARY_PATH \
RUSTFLAGS='-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l python3.12 -C link-arg=-Wl,-rpath,/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib' \
cargo test -p rme_core map_model_collects_statistics_from_tiles_and_sidecars
/tmp/rme-noct-m025-py312/bin/python -m ruff check pyrme/core_bridge.py pyrme/ui/dialogs/__init__.py pyrme/ui/dialogs/map_statistics.py pyrme/ui/main_window.py tests/python/test_legacy_map_menu.py tests/python/test_map_statistics_dialog.py
rustfmt --check --edition 2021 crates/rme_core/src/editor.rs crates/rme_core/src/map.rs
rustfmt --check --edition 2021 --config skip_children=true crates/rme_core/src/lib.rs
git diff --check
```
