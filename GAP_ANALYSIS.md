# RME Noct - Gap Analysis & Progression Report

This document outlines the current progression of **RME Noct** (Python/Rust) relative to the **Legacy Remere's Map Editor Redux** (C++). It identifies achieved parity, ongoing work, and features that are currently considered gaps or non-goals.

## 1. Project Overview

| Feature | Legacy Redux (C++) | RME Noct (Python/Rust) | Status |
| :--- | :--- | :--- | :--- |
| **Language** | C++17 / Qt5 | Python 3.12 / Rust / PyQt6 | **Transitional** |
| **Renderer** | OpenGL (Fixed/Legacy) | wgpu-rs (Modern GPU API) | **In Progress** |
| **Architecture** | Monolithic C++ | Split Shell (Python) & Core (Rust) | **Active** |
| **Design System** | Native OS / Standard Qt | Hyprland-inspired Noct Glassmorphism | **Superior** |

---

## 2. Functional parity

### 2.1 UI & Experience
- **Menubar**: 100% parity achieved. Uses `menubar.xml` as source of truth for all labels, shortcuts, and ordering.
- **Design System**: Hyprland-inspired Arch-blue glass tokens now cover focus state, shared QSS helpers, and selected dock chrome.
- **Active State Tracking**: Welcome lists and editor canvases expose stable focus state; `GlassPanel` now uses focus-rim and shadow contracts without compositor claims.
- **Dialogs**: Parity achieved for Tier 2/3 Dialogs (Town Manager, Waypoints, Map Properties, Find Item, About).
- **Toolbars**: Basic parity achieved; Noct uses a refined, high-fidelity dock system.
- **Docks**: Parity achieved for viewport navigation and visibility flags (Show All Floors, Grid, etc.).

### 2.2 Map & Core Logic
- **Map Model**: Legacy uses a deep C++ tile/floor hierarchy. Noct uses a performance-optimized Rust model with sparse updates.
- **Asset Loading**: High parity for OTB, DAT, and SPR parsing via `rme_core`. Reliable support for Extended Edition format.
- **Selection System**: Parity achieved for multi-floor selection and basic map manipulation math (screen-to-map).

### 2.3 Brushes & Tools
- **Basic Brushes**: Parity for Raw and Item brushes.
- **Autoborder**: **GAP**. Legacy has highly mature recursive autobordering logic for 100+ categories. Noct currently implements high-level hooks, but the granular rule-based logic is still being migrated to Rust core.

---

## 3. Major Gaps (Non-Goals)

These features exist in the legacy C++ codebase but are either not implemented or explicitly deferred in RME Noct.

### 🛑 Live Collaborative Editing
Legacy RME includes a standalone networking layer (`source/live`) for real-time collaborative map editing.
- **Noct Status**: **GAP**. There is currently no implementation of the Networking/Live protocol. This is considered a low-priority feature compared to stable rendering and performance.

### 🛑 Lua Scripting Engine
Legacy RME allows users to write Lua scripts for map generation and tool automation (`source/lua`).
- **Noct Status**: **GAP**. No integrated scripting engine exists in Noct yet. Python itself serves as the "scripting" layer for the shell, but a sandboxed user-scripting API is not on the immediate roadmap.

### 🛑 Minimap Generation
Legacy RME maintains a real-time minimap with export capabilities.
- **Noct Status**: **GAP**. Priority is currently on the high-performance main canvas rendering. Minimap generation is a future milestone.

---

## 4. Architectural Improvements (The "Noct Advantage")

Where RME Noct intentionally deviates from legacy for better results:

> [!TIP]
> **Performance at Scale**: Legacy RME often hit memory and UI thread bottlenecks with `50k+` items or massive maps. Noct offloads performance-critical logic (IO, Map Math, Rendering) to Rust/WGPU, keeping the UI responsive via Python/PyQt6's event loop.

- **GPU Acceleration**: Move from legacy OpenGL to `wgpu`, allowing for more efficient tile drawing and modern effects.
- **Search-First UX**: The Item Palette and Find Item tools use model-based virtualization and caching, providing instant feedback that the legacy `QListWidget` path could not sustain.
- **Type Safety**: Rust core ensures map integrity and provides safe concurrency that was difficult to maintain in the legacy C++ pointers/manual memory management.

---

## 5. Progression Status (Milestones)

- [x] **LEGACY-00-CONTRACT**: Menubar and Action system parity.
- [x] **TIER-2-DIALOGS**: Core management windows (Towns, Map Props).
- [/] **CANVAS-HOST**: Renderer host and viewport math (Complete).
- [ ] **SPRITE-PARITY**: Drawing real items instead of diagnostic placeholders (Next).
- [ ] **AUTOBORDER-CORE**: Migration of C++ autoborder rules to Rust.
