# pyrme/ui/AGENTS.md

- PyQt6 only — no Qt5 imports.
- All Qt signal/slot signatures: verify via Context7 before wiring.
- No new dock types without spec in active S##-PLAN.md.
- Manual smoke test via `python3 -m pyrme` before marking UI task done. In headless sessions, `QT_QPA_PLATFORM=offscreen` only proves startup.
- 8px grid, all 5 interaction states required on every widget.
