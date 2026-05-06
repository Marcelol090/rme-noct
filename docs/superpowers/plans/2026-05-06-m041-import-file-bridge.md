# M041 Import File Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a real `EditorShellState.import_otbm()` bridge that imports another `.otbm` into the current map through the M040 merge primitive.

**Architecture:** Keep file import in the Rust editor bridge, not UI. Rust loads the source `.otbm`, converts a string collision policy into M040 `CollisionPolicy`, calls `merge_map_tiles`, and returns report counts. Python `EditorShellCoreBridge` wraps the native method into an `ImportMapReport` dataclass and returns `None` when native support is absent or stale.

**Tech Stack:** Rust, PyO3, `rme_core`, Python bridge adapter, pytest, WSL cargo/pytest verification, Windows Git for staging/commit, `rtk` for compact shell output where useful.

---

## File Structure

- Modify `crates/rme_core/src/editor.rs`
  - Add `crate::merger` imports.
  - Add collision-policy parser helper.
  - Add PyO3 `import_otbm()` method beside `load_otbm()` / `save_otbm()`.
  - Add Rust bridge tests in the existing `#[cfg(test)] mod tests`.
- Modify `pyrme/core_bridge.py`
  - Add `ImportMapReport`.
  - Add `EditorShellCoreBridge.import_otbm()`.
  - Do not add Python fallback merge behavior.
- Modify `tests/python/test_core_bridge.py`
  - Add adapter-level tests for report conversion, missing native method, and native exception.
- Modify `tests/python/test_rme_core_editor_shell.py`
  - Add native smoke test that imports a saved source file when the rebuilt native extension exposes `import_otbm`.
- Modify `docs/superpowers/specs/2026-05-06-m041-import-file-bridge-design.md`
  - Already corrected: tile import advances generation, not metadata-only dirty flag.

---

### Task 1: Add Rust Import Bridge

**Files:**
- Modify: `crates/rme_core/src/editor.rs`

- [ ] **Step 1: Add failing Rust bridge tests**

Append these tests inside the existing `#[cfg(test)] mod tests` in `crates/rme_core/src/editor.rs`, after `editor_load_otbm_loads_xml_sidecars_and_marks_clean()`:

```rust
    fn save_source_with_ground(
        dir: &tempfile::TempDir,
        name: &str,
        x: i32,
        y: i32,
        z: i32,
        item_id: u16,
    ) -> std::path::PathBuf {
        let path = dir.path().join(name);
        let path_str = path.to_str().unwrap();
        let mut source = EditorShellState::default();
        assert!(source.set_tile_ground(x, y, z, item_id));
        source.save_otbm(path_str).unwrap();
        path
    }

    #[test]
    fn editor_import_otbm_copies_offset_source_tile() {
        let dir = tempfile::tempdir().unwrap();
        let source_path = save_source_with_ground(&dir, "source.otbm", 10, 20, 7, 100);
        let source_path = source_path.to_str().unwrap();

        let mut target = EditorShellState::default();
        let generation_before = target.map_generation();

        let report = target
            .import_otbm(source_path, 5, -2, 1, "replace")
            .unwrap();

        assert_eq!(report, (1, 0, 0, 0));
        assert_eq!(
            target.get_tile_data(15, 18, 8),
            Some((Some(100), Vec::new(), 0, 0))
        );
        assert!(target.map_generation() > generation_before);
        assert!(!target.map_is_dirty());
    }

    #[test]
    fn editor_import_otbm_replace_policy_overwrites_destination() {
        let dir = tempfile::tempdir().unwrap();
        let source_path = save_source_with_ground(&dir, "source.otbm", 10, 20, 7, 100);
        let source_path = source_path.to_str().unwrap();

        let mut target = EditorShellState::default();
        assert!(target.set_tile_ground(15, 18, 8, 500));

        let report = target
            .import_otbm(source_path, 5, -2, 1, "replace")
            .unwrap();

        assert_eq!(report, (1, 1, 0, 0));
        assert_eq!(
            target.get_tile_data(15, 18, 8),
            Some((Some(100), Vec::new(), 0, 0))
        );
    }

    #[test]
    fn editor_import_otbm_skip_policy_keeps_destination() {
        let dir = tempfile::tempdir().unwrap();
        let source_path = save_source_with_ground(&dir, "source.otbm", 10, 20, 7, 100);
        let source_path = source_path.to_str().unwrap();

        let mut target = EditorShellState::default();
        assert!(target.set_tile_ground(15, 18, 8, 500));

        let report = target.import_otbm(source_path, 5, -2, 1, "skip").unwrap();

        assert_eq!(report, (0, 0, 1, 0));
        assert_eq!(
            target.get_tile_data(15, 18, 8),
            Some((Some(500), Vec::new(), 0, 0))
        );
    }

    #[test]
    fn editor_import_otbm_discards_out_of_bounds_destination() {
        let dir = tempfile::tempdir().unwrap();
        let source_path = save_source_with_ground(&dir, "source.otbm", 0, 0, 0, 100);
        let source_path = source_path.to_str().unwrap();

        let mut target = EditorShellState::default();
        let generation_before = target.map_generation();

        let report = target
            .import_otbm(source_path, -1, 0, 0, "replace")
            .unwrap();

        assert_eq!(report, (0, 0, 0, 1));
        assert_eq!(target.tile_count(), 0);
        assert_eq!(target.map_generation(), generation_before);
    }

    #[test]
    fn editor_import_otbm_rejects_unknown_collision_policy() {
        let dir = tempfile::tempdir().unwrap();
        let source_path = save_source_with_ground(&dir, "source.otbm", 10, 20, 7, 100);
        let source_path = source_path.to_str().unwrap();

        let mut target = EditorShellState::default();
        let err = target
            .import_otbm(source_path, 0, 0, 0, "merge")
            .unwrap_err();

        assert!(err.to_string().contains("Unsupported collision policy"));
    }

    #[test]
    fn editor_import_otbm_reports_missing_source_path() {
        let mut target = EditorShellState::default();
        let err = target
            .import_otbm("missing-source-file.otbm", 0, 0, 0, "replace")
            .unwrap_err();

        assert!(err.to_string().contains("Failed to read import file"));
    }
```

- [ ] **Step 2: Run Rust test to verify RED**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && export PYO3_PYTHON=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin/python3.12 && export LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:${LD_LIBRARY_PATH:-} && export RUSTFLAGS="-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l dylib=python3.12" && cargo test -p rme_core editor_import_otbm --quiet'
```

Expected: FAIL because `EditorShellState` has no `import_otbm` method.

- [ ] **Step 3: Add Rust imports and collision parser**

In `crates/rme_core/src/editor.rs`, add this import after the `crate::map` import block:

```rust
use crate::merger::{merge_map_tiles, CollisionPolicy, MapMergeOptions};
```

Add this helper after `py_changes()` and before `py_snapshot_from_tile()`:

```rust
fn import_collision_policy(value: &str) -> PyResult<CollisionPolicy> {
    match value {
        "replace" => Ok(CollisionPolicy::Replace),
        "skip" => Ok(CollisionPolicy::Skip),
        other => Err(PyValueError::new_err(format!(
            "Unsupported collision policy: {other}"
        ))),
    }
}
```

- [ ] **Step 4: Add `EditorShellState.import_otbm()`**

In `crates/rme_core/src/editor.rs`, add this method between `load_otbm()` and `save_otbm()`:

```rust
    /// Imports an OTBM map file into the current map. Returns merge report counts.
    #[pyo3(signature = (path, offset_x=0, offset_y=0, offset_z=0, collision_policy="replace"))]
    fn import_otbm(
        &mut self,
        path: &str,
        offset_x: i32,
        offset_y: i32,
        offset_z: i32,
        collision_policy: &str,
    ) -> PyResult<(u64, u64, u64, u64)> {
        let data = std::fs::read(path)
            .map_err(|e| PyValueError::new_err(format!("Failed to read import file: {e}")))?;
        let (_header, source_map) = crate::io::otbm::load_otbm(&data)
            .map_err(|e| PyValueError::new_err(format!("OTBM import parse error: {e:?}")))?;
        let report = merge_map_tiles(
            &mut self.map,
            &source_map,
            MapMergeOptions {
                offset_x,
                offset_y,
                offset_z,
                collision_policy: import_collision_policy(collision_policy)?,
            },
        );
        Ok((
            report.copied_tiles,
            report.replaced_tiles,
            report.skipped_existing_tiles,
            report.discarded_tiles,
        ))
    }
```

- [ ] **Step 5: Run Rust test to verify GREEN**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && export PYO3_PYTHON=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin/python3.12 && export LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:${LD_LIBRARY_PATH:-} && export RUSTFLAGS="-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l dylib=python3.12" && cargo test -p rme_core editor_import_otbm --quiet'
```

Expected: PASS. Six `editor_import_otbm_*` tests pass.

- [ ] **Step 6: Commit Rust bridge task**

Run:

```bash
git add crates/rme_core/src/editor.rs
git diff --cached --check
git commit -m "feat(M041/T01): add import file bridge"
```

Expected: commit succeeds on `gsd/M041/S01-import-file-bridge`.

---

### Task 2: Add Python Bridge Adapter

**Files:**
- Modify: `pyrme/core_bridge.py`
- Modify: `tests/python/test_core_bridge.py`

- [ ] **Step 1: Add failing Python adapter tests**

Modify the import block in `tests/python/test_core_bridge.py` to include `ImportMapReport`:

```python
from pyrme.core_bridge import (
    SHOW_FLAG_DEFAULTS,
    VIEW_FLAG_DEFAULTS,
    EditorShellCoreBridge,
    ImportMapReport,
    _FallbackEditorShellState,
    create_editor_shell_state,
)
```

Append these tests to `tests/python/test_core_bridge.py`:

```python
class _NativeImportRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, int, int, str]] = []

    def import_otbm(
        self,
        path: str,
        offset_x: int,
        offset_y: int,
        offset_z: int,
        collision_policy: str,
    ) -> tuple[int, int, int, int]:
        self.calls.append((path, offset_x, offset_y, offset_z, collision_policy))
        return (1, 2, 3, 4)


class _NativeImportRaises:
    def import_otbm(
        self,
        path: str,
        offset_x: int,
        offset_y: int,
        offset_z: int,
        collision_policy: str,
    ) -> tuple[int, int, int, int]:
        raise RuntimeError("import failed")


def test_editor_shell_core_bridge_import_otbm_returns_report() -> None:
    native = _NativeImportRecorder()
    core = EditorShellCoreBridge(native, native=True)

    report = core.import_otbm("source.otbm", 5, -2, 1, "skip")

    assert report == ImportMapReport(
        copied_tiles=1,
        replaced_tiles=2,
        skipped_existing_tiles=3,
        discarded_tiles=4,
    )
    assert native.calls == [("source.otbm", 5, -2, 1, "skip")]


def test_editor_shell_core_bridge_import_otbm_missing_native_method() -> None:
    core = EditorShellCoreBridge(_FallbackEditorShellState(), native=False)

    assert core.import_otbm("source.otbm") is None


def test_editor_shell_core_bridge_import_otbm_native_exception() -> None:
    core = EditorShellCoreBridge(_NativeImportRaises(), native=True)

    assert core.import_otbm("source.otbm") is None
```

- [ ] **Step 2: Run Python adapter test to verify RED**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && python3 -m pytest tests/python/test_core_bridge.py -q --tb=short'
```

Expected: FAIL because `ImportMapReport` or `EditorShellCoreBridge.import_otbm` is missing.

- [ ] **Step 3: Add `ImportMapReport`**

In `pyrme/core_bridge.py`, add this dataclass after `TileCommandPayload`:

```python
@dataclass(frozen=True)
class ImportMapReport:
    copied_tiles: int
    replaced_tiles: int
    skipped_existing_tiles: int
    discarded_tiles: int
```

- [ ] **Step 4: Add `EditorShellCoreBridge.import_otbm()`**

In `pyrme/core_bridge.py`, add this method between `resolve_autoborder_items()` and `load_otbm()`:

```python
    def import_otbm(
        self,
        path: str,
        offset_x: int = 0,
        offset_y: int = 0,
        offset_z: int = 0,
        collision_policy: str = "replace",
    ) -> ImportMapReport | None:
        if not hasattr(self._inner, "import_otbm"):
            return None
        try:
            copied, replaced, skipped, discarded = self._inner.import_otbm(
                path,
                int(offset_x),
                int(offset_y),
                int(offset_z),
                collision_policy,
            )
        except Exception:
            return None
        return ImportMapReport(
            copied_tiles=int(copied),
            replaced_tiles=int(replaced),
            skipped_existing_tiles=int(skipped),
            discarded_tiles=int(discarded),
        )
```

- [ ] **Step 5: Run Python adapter test to verify GREEN**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && python3 -m pytest tests/python/test_core_bridge.py -q --tb=short'
```

Expected: PASS. `test_core_bridge.py` passes.

- [ ] **Step 6: Commit Python adapter task**

Run:

```bash
git add pyrme/core_bridge.py tests/python/test_core_bridge.py
git diff --cached --check
git commit -m "feat(M041/T02): add Python import adapter"
```

Expected: commit succeeds on `gsd/M041/S01-import-file-bridge`.

---

### Task 3: Add Native Python Smoke Test

**Files:**
- Modify: `tests/python/test_rme_core_editor_shell.py`

- [ ] **Step 1: Add failing native smoke test**

Append this test near the existing native OTBM tests in `tests/python/test_rme_core_editor_shell.py`:

```python
def test_native_rme_core_import_otbm_merges_saved_source(tmp_path) -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )
    required_methods = (
        "get_tile_data",
        "import_otbm",
        "map_generation",
        "save_otbm",
        "set_tile_ground",
    )
    missing = [
        name for name in required_methods if not hasattr(rme_core.EditorShellState, name)
    ]
    if missing:
        pytest.skip(f"pyrme.rme_core missing M041 methods: {missing}")

    source = rme_core.EditorShellState()
    assert source.set_tile_ground(10, 20, 7, 100) is True
    source_path = tmp_path / "source.otbm"
    source.save_otbm(str(source_path))

    target = rme_core.EditorShellState()
    generation_before = target.map_generation()

    assert target.import_otbm(str(source_path), 5, -2, 1, "replace") == (1, 0, 0, 0)
    assert target.get_tile_data(15, 18, 8) == (100, [], 0, 0)
    assert target.map_generation() > generation_before
```

- [ ] **Step 2: Run native Python smoke test**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && python3 -m pytest tests/python/test_rme_core_editor_shell.py::test_native_rme_core_import_otbm_merges_saved_source -q --tb=short'
```

Expected: PASS or SKIP when local `pyrme.rme_core` is stale and lacks M041 native method. FAIL only if import behavior is broken in a rebuilt native module.

- [ ] **Step 3: Commit native smoke test**

Run:

```bash
git add tests/python/test_rme_core_editor_shell.py
git diff --cached --check
git commit -m "test(M041/T03): cover native import bridge"
```

Expected: commit succeeds on `gsd/M041/S01-import-file-bridge`.

---

### Task 4: Final Verification And Review

**Files:**
- Modify: `crates/rme_core/src/editor.rs`
- Modify: `pyrme/core_bridge.py`
- Modify: `tests/python/test_core_bridge.py`
- Modify: `tests/python/test_rme_core_editor_shell.py`
- Existing docs: `docs/superpowers/specs/2026-05-06-m041-import-file-bridge-design.md`
- Existing plan: `docs/superpowers/plans/2026-05-06-m041-import-file-bridge.md`

- [ ] **Step 1: Run focused Rust tests**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && export PYO3_PYTHON=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin/python3.12 && export LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:${LD_LIBRARY_PATH:-} && export RUSTFLAGS="-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l dylib=python3.12" && cargo test -p rme_core editor_import_otbm --quiet'
```

Expected: PASS.

- [ ] **Step 2: Run focused Python tests**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && python3 -m pytest tests/python/test_core_bridge.py tests/python/test_rme_core_editor_shell.py -q --tb=short'
```

Expected: PASS, allowing native smoke SKIP only if local native module is stale.

- [ ] **Step 3: Run formatting and diff checks**

Run:

```bash
wsl -e bash -lc 'cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m041-import-file-bridge-20260506" && cargo fmt --check'
git diff --check
```

Expected: PASS.

- [ ] **Step 4: Run caveman-review on full diff**

Run:

```bash
git diff origin/main -- crates/rme_core/src/editor.rs pyrme/core_bridge.py tests/python/test_core_bridge.py tests/python/test_rme_core_editor_shell.py docs/superpowers/specs/2026-05-06-m041-import-file-bridge-design.md docs/superpowers/plans/2026-05-06-m041-import-file-bridge.md
```

Review with `caveman-review`. Expected: no gaps. If gap found, fix, re-run focused tests, re-review.

- [ ] **Step 5: Commit docs updates if any remain**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-05-06-m041-import-file-bridge-design.md docs/superpowers/plans/2026-05-06-m041-import-file-bridge.md
git diff --cached --check
git commit -m "docs(M041/S01): plan import file bridge"
```

Expected: commit succeeds only if docs are staged. If docs were already committed, skip this commit.

- [ ] **Step 6: Prepare PR gate**

Run:

```bash
git status --short
git log --oneline origin/main..HEAD
```

Expected: worktree clean, branch contains spec, plan, Rust bridge, Python adapter, and tests. Next gate is `caveman-review` clean result, then `github:yeet` push + draft PR after user approval.
