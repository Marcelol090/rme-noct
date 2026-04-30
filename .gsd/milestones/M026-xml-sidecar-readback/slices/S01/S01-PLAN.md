# M026 XML Sidecar Readback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load legacy waypoint, spawn, and house XML sidecars during OTBM load.

**Architecture:** Keep parsing in `crates/rme_core/src/io/xml.rs`; keep OTBM parsing unchanged. `EditorShellState.load_otbm` calls XML readback after binary load, then marks the map clean.

**Tech Stack:** Rust 2021, PyO3, `quick-xml`, existing `MapModel`, pytest native bridge tests.

---

## File Structure

- Modify `crates/rme_core/Cargo.toml`: add `quick-xml`.
- Modify `crates/rme_core/src/io/xml.rs`: parser, path resolver, load report, tests.
- Modify `crates/rme_core/src/map.rs`: sidecar count helper only.
- Modify `crates/rme_core/src/editor.rs`: load integration, count bridge, Rust roundtrip test.
- Modify `tests/python/test_rme_core_editor_shell.py`: native save/load sidecar readback test.
- Create `.gsd/milestones/M026-xml-sidecar-readback/slices/S01/tasks/T01-SUMMARY.md`.
- Update `.gsd/milestones/M026-xml-sidecar-readback/slices/S01/S01-PLAN.md` checkboxes during execution.
- Update `.gsd/STATE.md` at closeout.

## Environment

Run all commands from:

```bash
cd "/mnt/c/Users/Marcelo Henrique/Desktop/rme-noct/.worktrees/m026-xml-sidecar-readback"
export PYO3_PYTHON=/tmp/rme-noct-m026-py312/bin/python
export LD_LIBRARY_PATH=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib:${LD_LIBRARY_PATH:-}
export RUSTFLAGS="-L native=/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib -l python3.12 -C link-arg=-Wl,-rpath,/home/marcelo/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/lib"
```

---

### Task 1: XML Readback Parser

**Files:**
- Modify: `crates/rme_core/Cargo.toml`
- Modify: `crates/rme_core/src/io/xml.rs`

- [x] **Step 1: Write failing parser tests**

Append tests to `crates/rme_core/src/io/xml.rs`:

```rust
#[test]
fn xml_loads_waypoints_and_skips_invalid_nodes() {
    let mut map = MapModel::new();
    let loaded = load_waypoints_xml(
        &mut map,
        r#"<?xml version="1.0"?>
<waypoints>
    <waypoint name="Temple" x="100" y="200" z="7" />
    <waypoint name="" x="101" y="201" z="7" />
    <waypoint name="Bad X" x="0" y="201" z="7" />
</waypoints>
"#,
    )
    .unwrap();

    assert_eq!(loaded, 1);
    assert_eq!(map.waypoints().len(), 1);
    assert_eq!(map.waypoints()[0].name(), "Temple");
    assert_eq!(map.waypoints()[0].position().as_tuple(), (100, 200, 7));
}

#[test]
fn xml_loads_spawns_and_creatures_with_legacy_validation() {
    let mut map = MapModel::new();
    let report = load_spawns_xml(
        &mut map,
        r#"<?xml version="1.0"?>
<spawns>
    <spawn centerx="101" centery="201" centerz="7" radius="5">
        <monster name="Rat" x="1" y="-1" spawntime="60" direction="2" />
        <npc name="Guide" x="0" y="0" spawntime="30" />
        <monster name="" x="2" y="2" spawntime="15" />
    </spawn>
    <spawn centerx="0" centery="201" centerz="7" radius="5" />
    <spawn centerx="102" centery="202" centerz="7" radius="0" />
</spawns>
"#,
    )
    .unwrap();

    assert_eq!(report.spawns, 1);
    assert_eq!(report.creatures, 2);
    assert_eq!(map.spawns().len(), 1);
    assert_eq!(map.spawns()[0].center().as_tuple(), (101, 201, 7));
    assert_eq!(map.spawns()[0].radius(), 5);
    assert_eq!(map.spawns()[0].creatures().len(), 2);
    assert!(map.spawns()[0].creatures()[1].is_npc());
}

#[test]
fn xml_loads_houses_and_skips_missing_townid() {
    let mut map = MapModel::new();
    let loaded = load_houses_xml(
        &mut map,
        r#"<?xml version="1.0"?>
<houses>
    <house name="Depot" houseid="12" entryx="102" entryy="202" entryz="7" rent="500" guildhall="true" townid="3" size="14" />
    <house name="No Town" houseid="13" entryx="103" entryy="203" entryz="7" rent="0" />
</houses>
"#,
    )
    .unwrap();

    assert_eq!(loaded, 1);
    assert_eq!(map.houses().len(), 1);
    assert_eq!(map.houses()[0].id(), 12);
    assert_eq!(map.houses()[0].name(), "Depot");
    assert_eq!(map.houses()[0].entry().as_tuple(), (102, 202, 7));
    assert_eq!(map.houses()[0].townid(), 3);
    assert!(map.houses()[0].guildhall());
}

#[test]
fn xml_sidecar_loader_uses_explicit_paths_and_stem_fallback() {
    let dir = tempfile::tempdir().unwrap();
    let otbm_path = dir.path().join("world.otbm");
    std::fs::write(&otbm_path, b"").unwrap();
    std::fs::write(
        dir.path().join("custom-spawn.xml"),
        r#"<?xml version="1.0"?><spawns><spawn centerx="101" centery="201" centerz="7" radius="5" /></spawns>"#,
    )
    .unwrap();
    std::fs::write(
        dir.path().join("world-house.xml"),
        r#"<?xml version="1.0"?><houses><house name="Depot" houseid="12" entryx="102" entryy="202" entryz="7" rent="500" townid="3" size="14" /></houses>"#,
    )
    .unwrap();
    std::fs::write(
        dir.path().join("world-waypoint.xml"),
        r#"<?xml version="1.0"?><waypoints><waypoint name="Temple" x="100" y="200" z="7" /></waypoints>"#,
    )
    .unwrap();

    let mut map = MapModel::new();
    map.set_spawnfile("custom-spawn.xml");

    let report = load_sidecar_xml(&mut map, &otbm_path).unwrap();

    assert_eq!(report.spawns, 1);
    assert_eq!(report.houses, 1);
    assert_eq!(report.waypoints, 1);
    assert_eq!(report.missing_files, 0);
}
```

- [x] **Step 2: Run RED**

Run:

```bash
cargo test -p rme_core io::xml
```

Expected: compile failure because `load_waypoints_xml`, `load_spawns_xml`, `load_houses_xml`, `load_sidecar_xml`, and report fields do not exist.

- [x] **Step 3: Implement parser**

Add dependency:

```toml
quick-xml = "0.39"
```

Add public API in `xml.rs`:

```rust
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct SidecarLoadReport {
    pub waypoints: usize,
    pub spawns: usize,
    pub creatures: usize,
    pub houses: usize,
    pub missing_files: usize,
}

#[derive(Debug)]
pub enum XmlLoadError {
    Io(std::io::Error),
    Parse(String),
}

pub fn load_waypoints_xml(map: &mut MapModel, xml: &str) -> Result<usize, XmlLoadError>;
pub fn load_spawns_xml(map: &mut MapModel, xml: &str) -> Result<SidecarLoadReport, XmlLoadError>;
pub fn load_houses_xml(map: &mut MapModel, xml: &str) -> Result<usize, XmlLoadError>;
pub fn load_sidecar_xml(
    map: &mut MapModel,
    otbm_path: impl AsRef<Path>,
) -> Result<SidecarLoadReport, XmlLoadError>;
```

Implementation rules:
- Use `quick_xml::Reader`.
- Return `XmlLoadError::Parse` for XML reader errors.
- Parse attributes into strings first, then typed values with helper functions.
- Skip invalid nodes, do not fail whole file.
- For `Event::Empty`, parse node immediately.
- For `Event::Start` spawn, collect child monsters/NPCs until matching `spawn` end.

- [x] **Step 4: Run GREEN**

Run:

```bash
cargo test -p rme_core io::xml
```

Expected: all `io::xml` tests pass.

---

### Task 2: Editor Load Integration

**Files:**
- Modify: `crates/rme_core/src/map.rs`
- Modify: `crates/rme_core/src/editor.rs`
- Modify: `tests/python/test_rme_core_editor_shell.py`

- [x] **Step 1: Write failing integration tests**

Add Rust test to `crates/rme_core/src/editor.rs`:

```rust
#[test]
fn editor_load_otbm_loads_xml_sidecars_and_marks_clean() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("roundtrip.otbm");
    let path_str = path.to_str().unwrap();

    let mut writer = EditorShellState::default();
    assert!(writer.add_waypoint("Temple", 100, 200, 7));
    let spawn_index = writer.add_spawn(101, 201, 7, 5);
    assert!(writer
        .add_spawn_creature(spawn_index, "Rat", 1, -1, 60, false, 2)
        .unwrap());
    assert!(writer.add_house(12, "Depot", 102, 202, 7, 500, 3, true, 14));
    writer.save_otbm(path_str).unwrap();

    let mut reader = EditorShellState::default();
    let loaded = reader.load_otbm(path_str).unwrap();

    assert_eq!(loaded.2, 0);
    assert_eq!(reader.sidecar_counts(), (1, 1, 1, 1));
    assert!(!reader.map_is_dirty());
}
```

Add Python test to `tests/python/test_rme_core_editor_shell.py`:

```python
def test_native_rme_core_load_otbm_reads_xml_sidecars(tmp_path) -> None:
    rme_core = pytest.importorskip(
        "pyrme.rme_core",
        reason="pyrme.rme_core is not built in this environment",
    )
    if not hasattr(rme_core.EditorShellState, "load_otbm"):
        pytest.skip("pyrme.rme_core binary was not rebuilt with load_otbm")
    if not hasattr(rme_core.EditorShellState, "sidecar_counts"):
        pytest.skip("pyrme.rme_core binary was not rebuilt with sidecar_counts")

    writer = rme_core.EditorShellState()
    writer.add_waypoint("Temple", 100, 200, 7)
    spawn_index = writer.add_spawn(101, 201, 7, 5)
    writer.add_spawn_creature(spawn_index, "Rat", 1, -1, 60, False, 2)
    writer.add_house(12, "Depot", 102, 202, 7, 500, 3, True, 14)

    out_file = tmp_path / "roundtrip.otbm"
    writer.save_otbm(str(out_file))

    reader = rme_core.EditorShellState()
    assert reader.load_otbm(str(out_file)) == (0, 0, 0)
    assert tuple(reader.sidecar_counts()) == (1, 1, 1, 1)
    assert reader.map_is_dirty() is False
```

- [x] **Step 2: Run RED**

Run:

```bash
cargo test -p rme_core editor_load_otbm_loads_xml_sidecars_and_marks_clean
```

Expected: compile failure because `sidecar_counts` does not exist, or assertion failure because load ignores XML.

- [x] **Step 3: Implement integration**

Add to `MapModel`:

```rust
pub fn sidecar_counts(&self) -> (usize, usize, usize, usize) {
    let creature_count = self.spawns.iter().map(|spawn| spawn.creatures().len()).sum();
    (
        self.waypoints.len(),
        self.spawns.len(),
        creature_count,
        self.houses.len(),
    )
}
```

Add to `EditorShellState` PyO3 methods:

```rust
fn sidecar_counts(&self) -> (usize, usize, usize, usize) {
    self.map.sidecar_counts()
}
```

Change `load_otbm` after `self.map = model;`:

```rust
crate::io::xml::load_sidecar_xml(&mut self.map, path)
    .map_err(|e| PyValueError::new_err(format!("XML load error: {e}")))?;
self.map.mark_clean();
```

- [x] **Step 4: Rebuild native package**

Run:

```bash
uv pip install --python /tmp/rme-noct-m026-py312/bin/python -e ".[dev]"
```

Expected: package rebuild succeeds.

- [x] **Step 5: Run GREEN**

Run:

```bash
cargo test -p rme_core editor_load_otbm_loads_xml_sidecars_and_marks_clean
/tmp/rme-noct-m026-py312/bin/python -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short
```

Expected: Rust test passes and Python native tests pass.

---

### Task 3: External Fixture Smoke And Closeout

**Files:**
- Modify: `crates/rme_core/src/io/xml.rs`
- Create: `.gsd/milestones/M026-xml-sidecar-readback/slices/S01/tasks/T01-SUMMARY.md`
- Modify: `.gsd/milestones/M026-xml-sidecar-readback/slices/S01/S01-PLAN.md`
- Modify: `.gsd/STATE.md`

- [x] **Step 1: Add env-gated fixture test**

Add test to `xml.rs`:

```rust
#[test]
fn external_canary_tfs_sidecar_xml_parse_when_configured() {
    let Some(root) = std::env::var_os("RME_NOCT_EXTERNAL_TIBIA_FIXTURES") else {
        return;
    };
    let root = std::path::PathBuf::from(root);
    let cases = [
        "holybaiak-server/data-canary/world/custom/events.otbm",
        "korvusot/data-canary/world/canary.otbm",
        "korvusot/data-otservbr-global/world/korvusot.otbm",
        "KingOT/MAPAS/ATUALIZADO/otservbr.otbm",
    ];

    let mut parsed_cases = 0usize;
    for relative in cases {
        let otbm_path = root.join(relative);
        if !otbm_path.exists() {
            continue;
        }
        let mut map = MapModel::new();
        let report = load_sidecar_xml(&mut map, &otbm_path).unwrap();
        if report.waypoints + report.spawns + report.houses > 0 {
            parsed_cases += 1;
        }
    }

    assert!(parsed_cases > 0, "no configured Canary/TFS sidecar fixtures parsed");
}
```

- [x] **Step 2: Run fixture smoke**

Run:

```bash
RME_NOCT_EXTERNAL_TIBIA_FIXTURES="/mnt/c/Users/Marcelo Henrique/Desktop/PROJETOS TIBIA/PROJETOS TIBIA" cargo test -p rme_core external_canary_tfs_sidecar_xml_parse_when_configured -- --nocapture
```

Expected: pass when at least one configured fixture has parseable sidecar XML. If external path is absent, report blocker instead of changing test to fake success.

- [x] **Step 3: Run full verification**

Run:

```bash
npm run preflight --silent
cargo test -p rme_core io::xml
cargo test -p rme_core editor
/tmp/rme-noct-m026-py312/bin/python -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short
```

Expected: all pass.

- [x] **Step 4: caveman-review gap check**

Run:

```bash
git diff -- crates/rme_core/Cargo.toml crates/rme_core/src/io/xml.rs crates/rme_core/src/map.rs crates/rme_core/src/editor.rs tests/python/test_rme_core_editor_shell.py .gsd | sed -n '1,260p'
```

Review using `caveman-review`: each issue one line with location, problem, fix. If gap exists, fix before commit.

- [x] **Step 5: Write task summary**

Create `.gsd/milestones/M026-xml-sidecar-readback/slices/S01/tasks/T01-SUMMARY.md`:

```markdown
# T01 Summary: XML sidecar readback

## Done
- Added Rust XML sidecar readback for waypoints, spawns, houses.
- Integrated sidecar readback into `EditorShellState.load_otbm`.
- Added sidecar count bridge for verification.
- Added env-gated Canary/TFS fixture smoke.

## Verification
- `npm run preflight --silent`
- `cargo test -p rme_core io::xml`
- `cargo test -p rme_core editor`
- `/tmp/rme-noct-m026-py312/bin/python -m pytest tests/python/test_rme_core_editor_shell.py -q --tb=short`
- `RME_NOCT_EXTERNAL_TIBIA_FIXTURES=... cargo test -p rme_core external_canary_tfs_sidecar_xml_parse_when_configured -- --nocapture`

## Notes
- Missing sidecar files are non-fatal.
- Malformed XML is fatal.
- Invalid individual XML nodes are skipped.
- House load creates Rust house records directly because current Rust model has no preexisting house registry.
```

- [x] **Step 6: Update GSD state**

Set `.gsd/STATE.md`:

```markdown
**Active Milestone:** M026-xml-sidecar-readback
**Active Slice:** S01
**Active Task:** complete
**Phase:** review
**Next Action:** Run caveman-review and choose commit/PR closeout for M026/S01.
```

- [x] **Step 7: Commit only after clean review**

Use commit message:

```bash
git add crates/rme_core/Cargo.toml crates/rme_core/src/io/xml.rs crates/rme_core/src/map.rs crates/rme_core/src/editor.rs tests/python/test_rme_core_editor_shell.py .gsd/milestones/M026-xml-sidecar-readback .gsd/STATE.md
git commit -m "feat(M026/S01): load XML sidecars"
```

Do not commit if verification or caveman-review finds a gap.

---

## Self Review

- Spec coverage: parser, path resolution, editor integration, external fixture smoke, TDD verification covered.
- Placeholder scan: no `TBD`, no fake tests, no unverified success claims.
- Type consistency: `SidecarLoadReport` fields and `sidecar_counts()` tuple are used consistently.
- Scope check: no UI, no server runner, no external writes.
