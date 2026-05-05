# M034 Tool Selection UI Context

## Source

GitHub issue #72 lists `Tool Selection UI` as an approved Phase 3 task after Brush Engine Foundation and Autoborder Logic.

## Current State

- M029 implemented Rust brush engine foundation.
- M030 implemented pure Rust autoborder rules.
- M033 exposed catalog brush entries in PyQt shell and Jump to Brush.
- `MainWindow` already supports valid editor modes: `selection`, `drawing`, `erasing`, `fill`, and `move`.
- Current toolbar has real Select/Draw actions but inert Erase/Fill/Move actions.

## Slice Boundary

M034/S01 makes toolbar mode selection real for all five modes. It does not implement new backend behavior for Fill or Move.
