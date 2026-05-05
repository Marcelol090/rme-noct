# M035 Autoborder Core Bridge Context

## Source

`GAP_ANALYSIS.md` still tracks Autoborder as a gap. M030 already landed the pure
Rust `AutoborderPlan`; M031 kept Borderize actions deferred because no Python map
mutation consumer existed.

## Current State

- M030 implemented `crates/rme_core/src/autoborder.rs`.
- M033 exposed real brush catalog entries in PyQt shell.
- M034 wired real tool mode selection.
- `Borderize Selection/Map` still report the missing Python map mutation bridge.
- `Randomize Selection/Map` still lack ground variant catalog data.

## Slice Boundary

M035/S01 bridges existing Rust autoborder plan output to Python map mutation and
Edit menu Borderize actions. It does not implement randomize, renderer, minimap,
Search menu, or broad legacy rule import.
