# M008 Roadmap - Brush shell wiring

## S01 - BRUSH-20-SHELL-COMMAND-WIRING

Isolate and verify the pending shell wiring delta that sits on top of the M007 backend contract:

- `Jump to Brush` and `Jump to Item` must drive canonical brush/item activation through local dialog seams.
- Palette switching must clear stale shared search text and stale item activation honestly.
- Brush mode toolbar changes must update `EditorSessionState.mode` and the Tool Options dock label from one source of truth.
- WSL preflight must pass with the repo-local Python launcher and the platform-default npm script shell.

## Follow-up

Next work should review and stage only the scoped M008 hunks before any commit or publish step; do not stage unrelated `main_window.py` or toolchain changes file-wide.
