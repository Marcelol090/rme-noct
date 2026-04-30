# M018 S01: XML Writing implementation

## Goal
Implement basic XML string builders for `waypoints`, `spawns`, and `houses` directly in `rme_core/src/io/xml.rs`, and expose the execution alongside `save_otbm`.

## Steps
- `[x]` Extend `MapModel` with `Waypoint`, `Creature`, `Spawn`, and `House` structures in `map.rs`.
- `[x]` Create `io/xml.rs` and implement `save_waypoints`, `save_spawns`, `save_houses` returning standard XML strings matching legacy RME outputs.
- `[x]` Connect `io/xml.rs` generation directly in the Python bridge `EditorShellState::save_otbm` to write files to disk.
- `[x]` Add integration tests in `test_rme_core_editor_shell.py` confirming XML string content creation.

## Stop Condition
`save_otbm` from Python creates the `.otbm`, `<map>-house.xml`, `<map>-spawn.xml`, and `<map>-waypoint.xml` properly constructed.
