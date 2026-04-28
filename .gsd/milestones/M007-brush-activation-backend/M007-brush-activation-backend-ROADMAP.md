# M007 Roadmap - Brush activation backend

## S01 - BRUSH-10-ACTIVATION-BACKEND-CONTRACT

Lock the backend contract that palette and canvas seams rely on:

- session activation fields delegate to `EditorModel`
- invalid modes normalize to drawing
- item and palette brush commands update canonical state
- selection, drawing, erasing, and unsupported tools report honest changed/no-op results

## Follow-up

Next slice should target shell command wiring:

- separate `main_window.py` legacy-shell changes from activation-specific changes
- avoid staging unrelated menu parity, toolbar, and window management hunks together
- prove palette and toolbar commands drive the backend through focused tests
