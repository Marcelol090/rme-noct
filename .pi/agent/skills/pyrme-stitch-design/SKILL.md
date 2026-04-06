---
name: PyRME Stitch Design
description: Enforces the UI/UX design rules, Obsidian Cartographer theme, and layout constraints for generating PyRME screens with Stitch MCP. Use whenever creating or reviewing UI designs.
---

# PyRME Stitch Design Specifications

## Quick start

When generating UI screens via Stitch MCP or writing PyQt6 code, you MUST adhere to the following established constraints. Failure to do so violates the project acceptance criteria.

## Core Design Decisions

1. **Layout**: **Vertical Toolbar (VS Code Style)**
   - The main tool palette (Brush, Eraser, Selection, etc.) must reside in a neat vertical sidebar on the left.
   - This maximizes horizontal screen space for the Map Canvas on modern 16:9 displays.
   - Top area is reserved for a compact Menu Bar and generic global actions.

2. **Docks Behavior**: **Fixed (Encaixados)**
   - To respect the mandatory rule: *"Nenhum elemento de UI sobrepõe o canvas do mapa"*.
   - Docks (Item Palette, Minimap, Hierarchy) must be anchored to the sides (primarily right) and push the map canvas, never floating over it.
   - *Glassmorphism Application*: Apply the glassmorphism properties (10-15px blur, semi-transparent backgrounds, 1px bright borders) to the dock *container backgrounds* placed over the application's global dark textured background, framing the map perfectly without occlusion.

3. **UI Density**: **Compact**
   - Use compact spacing (minimal padding) and small but highly legible fonts (`~11px` Inter, Roboto, or similar).
   - High data density is required for Tibia map editing.
   - Use borders and subtle background shifts (glass layers) to separate elements rather than large whitespace.

## Acceptance Criteria Checklist

Before submitting any screen generation to the user, verify:
- [ ] Does the UI overlap the map canvas entirely? (Must be NO).
- [ ] Are X/Y/Z coordinates visible without scrolling in the layout? (Must be YES).
- [ ] Is the primary toolbar vertical? (Must be YES).
- [ ] Is the density compact? (Must be YES).
- [ ] Does it use Obsidian Cartographer (dark mode, glassmorphism) themes? (Must be YES).
