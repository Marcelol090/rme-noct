---
name: pyrme-pyqt6-ui
description: Use when working on PyQt6 UI components – dialogs, docks, palettes, menus, toolbars, preferences. Ensures dark theme consistency and parity with RME Extended Edition features.
---

# PyRME PyQt6 UI Development

## Principles

1. **Obsidian Cartographer theme** — all UI components use `dark_theme.qss`
2. **Reference legacy C++ UI** at `remeres-map-editor-redux/source/ui/` for layout/behavior
3. **Check Stitch mockups** before implementing any dialog
4. **Consistent spacing** — 8px grid system, 4px micro-adjustments
5. **Accessible** — all interactive elements have unique IDs
6. **QSS over programmatic styling** — keep styles in `.qss` files

## Feature Parity Checklist (RME Extended 3.8)

### 3.6 Features
- [ ] Monster & NPC names on canvas
- [ ] Duplicate Unique ID warning
- [ ] Client Profiles (multiple data profiles per version)
- [ ] Larger palette icons (optional)
- [x] Dark mode (Obsidian Cartographer)
- [ ] Replace Items via right-click in RAW palette
- [ ] Position highlight for Go to Position
- [ ] Export to minimap.otmm
- [ ] Cross-Instance Clipboard UI (Preferences toggle)

### 3.7 Features
- [ ] Lasso/Freehand Selection tool
- [ ] Lua Monster Import dialog
- [ ] Import Monster Folder dialog
- [ ] Quick Replace from Map (right-click on map)

### 3.8 Features
- [ ] ClientID format support (OTBM 5/6)
- [ ] Auto ID translation UI
- [ ] Map format conversion dialog
- [ ] Appearances menu (optional appearances.dat loading)

## UI Component Architecture

```
pyrme/ui/
├── main_window.py       # QMainWindow shell
├── canvas_widget.py     # wgpu canvas (Rust backend)
├── styles/
│   └── dark_theme.qss   # Obsidian Cartographer
├── dialogs/             # All dialogs (Preferences, Properties, etc.)
├── docks/               # Dock widgets (Palette, Minimap, etc.)
├── toolbars/            # Custom toolbars
└── widgets/             # Reusable custom widgets
```

## Verification

After any UI change:
```bash
ruff check pyrme/
mypy pyrme/ --ignore-missing-imports
pytest tests/python/ -v
```
