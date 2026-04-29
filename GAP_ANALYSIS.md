# RME Noct - Gap Analysis & Progression Report

This document outlines the current progression of **RME Noct** (Python/Rust) relative to the **Legacy Remere's Map Editor Redux** (C++). It identifies achieved parity, ongoing work, and features that are currently considered gaps or non-goals.

## 1. Project Overview

| Feature | Legacy Redux (C++) | RME Noct (Python/Rust) | Status |
| :--- | :--- | :--- | :--- |
| **Language** | C++17 / Qt5 | Python 3.12 / Rust / PyQt6 | **Transitional** |
| **Renderer** | OpenGL (Fixed/Legacy) | wgpu-rs (Modern GPU API) | **In Progress** |
| **Architecture** | Monolithic C++ | Split Shell (Python) & Core (Rust) | **Active** |
| **Design System** | Native OS / Standard Qt | Noct Glassmorphism (Premium) | **Superior** |

---

## 2. Functional Parity

### 2.1 UI & Experience
- **Menubar**: 100% parity achieved. Uses `menubar.xml` as source of truth for all labels, shortcuts, and ordering.
- **Dialogs**: Parity achieved for Tier 2/3 Dialogs (`Find Item`, `Goto Position`, `Map Properties`).
- **Honest Placeholders**: `Town Manager`, `Preferences`, and `About` are integrated with the Noct design system but currently serve as functional placeholders.
- **Toolbars**: Basic parity achieved; Noct uses a refined, high-fidelity dock system.
- **Docks**: Parity achieved for viewport navigation and visibility flags (`Show All Floors`, `Grid`, etc.). `Minimap` and `In-game Preview` are current placeholders.

### 2.2 Map & Core Logic
- **Map Model**: Ported to Rust (`rme_core`). Supports sparse storage, metadata, and generation tracking.
- **Asset Loading**: High parity for OTB, DAT, and SPR parsing via `rme_core`. Reliable support for Extended Edition format.
- **Persistence**: OTBM Read/Write parity achieved.
- **Selection System**: Parity achieved for multi-floor selection and basic map manipulation math (screen-to-map). Selection-dependent actions (Replace on Selection) are still pending wiring.

### 2.3 Brushes & Tools
- **Basic Brushes**: Parity for Raw and Item brushes.
- **Autoborder**: **GAP**. Legacy has highly mature recursive autobordering logic. Noct implements high-level hooks, but the granular rule-based logic is still being migrated to Rust core.
- **Advanced Brushes**: **GAP**. `Wall`, `Doodad`, `Carpet`, `Table`, and `Spawn` brushes are currently missing.

---

## 3. Major Gaps (Non-Goals & Deferred)

### 🛑 Undo/Redo System
Legacy RME maintains an `ActionQueue` for full undo/redo support.
- **Noct Status**: **GAP**. Neither the Rust core nor the Python shell currently implements a command pattern for undoable operations.

### 🛑 Copy/Paste/Cut
- **Noct Status**: **GAP**. No implementation of map-region buffers or clipboard serialization exists yet.

### 🛑 Complex Item Attributes
Legacy support for `Sign Text`, `Teleport Destination`, and `Container` content.
- **Noct Status**: **GAP**. `Item` in `rme_core` only carries `id`, `count`, `action_id`, and `unique_id`. Text and nested items are deferred.

### 🛑 Map Manipulation & Cleanup
- **Noct Status**: **GAP**. Advanced map-wide operations such as `Randomize Selection/Map`, `Remove Items by ID`, `Remove Corpses`, and `Unreachable Tile Cleanup` are currently not implemented.
- **Legacy Match**: These are mature C++ utilities in `source/editor/action.cpp`.

### 🛑 Import / Export Systems
- **Noct Status**: **GAP**. While the menu structure exists, the following are functional placeholders:
    - `Import Map / Monsters / NPC`
    - `Export Minimap / Tilesets`
    - `Reload Data Files`
    - `Missing Items Report`
- **Architectural Note**: These require tight integration between the Rust `io` module and the Python UI shell, currently deferred to post-rendering milestones.

### 🛑 Creatures & Spawns
- **Noct Status**: **GAP**. No data model or rendering logic for NPC/Monster spawns exists in Noct yet.

### 🛑 Houses & Towns
- **Noct Status**: **GAP**. While the map properties support house-file paths, the actual house-tile management and town-entry logic are missing.

### 🛑 Live Collaborative Editing
Legacy RME includes a standalone networking layer (`source/live`) for real-time collaborative map editing.
- **Noct Status**: **GAP**. Considered a low-priority feature.

### 🛑 Lua Scripting Engine
- **Noct Status**: **GAP**. Python serves as the shell layer, but a sandboxed user-scripting API is not on the immediate roadmap.

---

## 4. Architectural Improvements (The "Noct Advantage")

- **GPU Acceleration**: Move from legacy OpenGL to `wgpu`, allowing for modern effects and higher tile counts.
- **Search-First UX**: Item Palette and Find Item tools use model-based virtualization and caching.
- **Type Safety**: Rust core ensures map integrity and safe concurrency.
- **WGPU Pipeline**: Decoupled rendering from UI state, allowing for frame-plan resource collection before draw calls.

---

## 5. Progression Status (Milestones)

- [x] **LEGACY-00-CONTRACT**: Menubar and Action system parity.
- [x] **TIER-2-DIALOGS**: Core management windows (Towns, Map Props).
- [x] **CANVAS-HOST**: Renderer host and viewport math.
- [x] **OTBM-PERSISTENCE**: Full Read/Write parity for binary map files.
- [x] **SPRITE-RESOLVER**: High-performance item-id to sprite mapping.
- [/] **SPRITE-PARITY**: Drawing real items instead of diagnostic placeholders (Active).
- [ ] **WGPU-CORE**: Migration of diagnostic drawing to full WGPU sprite pipeline.
- [ ] **AUTOBORDER-CORE**: Migration of C++ autoborder rules to Rust.
- [ ] **UNDO-REDO-CORE**: Command-pattern implementation for map mutations.

