# Design System: Noct Map Editor

**Project:** Noct Map Editor
**Version:** 1.0.0
**Theme Mode:** Dark-only (no light mode variant)

---

## 1. Visual Theme & Atmosphere

**Noct Map Editor** embodies the aesthetic of the **night wolf**. A dense, purposeful tool built for power users. Every panel feels like dark obsidian glass under moonlight: dark, slightly translucent, with faint reflections. The logo is a **wolf howling at an amethyst moon**.

The overall density is **compact and utilitarian**, never sparse. The interface does not breathe — it works. Whitespace is used surgically, only where it aids parsing. The map canvas is always the dominant surface; every other element exists in service of it.

The mood is **nocturnal precision** — the UI of a tool that was clearly built by someone who has spent thousands of hours editing Tibia maps. It borrows visual cues from code editors (JetBrains-style monospaced coordinates, VS Code-style dock headers) but dresses them in the dark glass aesthetic of a premium desktop application.

Glassmorphism appears **only on floating panels and dialogs** — never on the map canvas itself, which must remain crisp, opaque, and unfiltered. The glass effect creates a hierarchy: panels float *above* the workspace, reinforcing the mental model of "tools hovering over the map."

Animation is minimal and purposeful. Dock expansions and dialog entrances use short ease-out transitions (150ms). No decorative motion.

---

## 2. Color Palette & Roles

### Base Surfaces
| Name | Hex | Role |
|---|---|---|
| Void Black | `#0A0A12` | Application background, canvas surround, deepest surface |
| Obsidian Glass | `rgba(255,255,255,0.04)` | Dock panel backgrounds, floating window fills |
| Lifted Glass | `rgba(255,255,255,0.07)` | Hovered rows, focused list items |
| Elevated Surface | `rgba(255,255,255,0.09)` | Dropdowns, context menus, tooltips, modals |

### Accent & Interactive
| Name | Hex | Role |
|---|---|---|
| Amethyst Core | `#7C5CFC` | Primary accent — active tool highlight, progress fill, selected item ring, CTA buttons |
| Deep Amethyst | `#4F3DB5` | Hover state on accent elements, pressed state |
| Amethyst Glow | `rgba(124,92,252,0.15)` | Halo behind active dock header, focus ring outer glow |
| Amethyst Rim | `rgba(124,92,252,0.5)` | Active border on selected tiles, focused inputs |

### Text
| Name | Hex | Role |
|---|---|---|
| Moonstone White | `#E8E6F0` | Primary labels, menu items, dialog headings, item names |
| Ash Lavender | `#9490A8` | Secondary labels, placeholder text, counts, timestamps |
| Muted Slate | `#4A4860` | Disabled controls, locked layer labels, inactive tabs |

### Borders & Dividers
| Name | Value | Role |
|---|---|---|
| Ghost Border | `rgba(255,255,255,0.08)` | Default panel borders, dock separators |
| Active Border | `rgba(255,255,255,0.14)` | Top-edge highlight of glass panels (the "rim of the glass") |
| Focus Border | `rgba(124,92,252,0.5)` | Focused inputs, selected list rows |

### Semantic Status
| Name | Hex | Role |
|---|---|---|
| Ember Red | `#E05C5C` | Invalid coordinates, error states, missing assets |
| Verdant Green | `#5CBF8A` | Loaded assets, valid spawn radius, success states |
| Amber Caution | `#D4A847` | Missing sprite warnings, beta features, unstable states |
| Steel Blue | `#5B8ECC` | Info states, documentation links, readonly highlights |

---

## 3. Typography Rules

The typography system is split into two families that never mix roles: **Inter** for all human-readable UI text, and **JetBrains Mono** for all machine-generated or coordinate data.

### Font Families
- **UI Labels:** Inter, system-ui, sans-serif
- **Coordinates & IDs:** JetBrains Mono, Consolas, monospace
- **Code/Debug values:** JetBrains Mono, monospace

### Type Scale
| Role | Font | Size | Weight | Color |
|---|---|---|---|---|
| Dialog heading | Inter | 14px | 600 | Moonstone White |
| Dock title / section heading | Inter | 11px | 600, UPPERCASE, 0.08em tracking | Ash Lavender |
| Menu item / body label | Inter | 12px | 400 | Moonstone White |
| Secondary label / caption | Inter | 12px | 400 | Ash Lavender |
| Coordinate display (large) | JetBrains Mono | 14px | 400 | Moonstone White |
| Coordinate display (inline) | JetBrains Mono | 12px | 400 | Moonstone White |
| Item ID / Sprite ID | JetBrains Mono | 11px | 400 | Ash Lavender |
| Debug / DevTools values | JetBrains Mono | 11px | 400 | varies by status |
| Hotkey badge | JetBrains Mono | 10px | 400 | Muted Slate |

### Typography Principles
Dock section headers always appear in UPPERCASE with generous letter-spacing (0.08em) — this is the visual language for organizational hierarchy within panels. Never use UPPERCASE for row content or interactive items.
Coordinates (X, Y, Z) are always monospaced and always show leading zeros on Z (`07` not `7`). This is non-negotiable — it mirrors the Tibia coordinate convention.
Numeric values in the DevTools overlay use semantic color: 60fps appears in Verdant Green (`#5CBF8A`), values below 30fps in Ember Red (`#E05C5C`), intermediate values in Amber Caution (`#D4A847`).

---

## 4. Component Stylings

### Buttons
**Primary (CTA):** Solid fill using Amethyst Core (`#7C5CFC`), generously rounded ends (`border-radius: 6px`), Moonstone White label in Inter 12px weight 500. On hover, background shifts to Deep Amethyst (`#4F3DB5`). Used exclusively for the primary action in dialogs (Save, Export, Import, Jump).
**Ghost (Secondary):** No fill, 1px border in Ghost Border (`rgba(255,255,255,0.08)`), Ash Lavender label. On hover, background becomes Lifted Glass (`rgba(255,255,255,0.07)`) and border brightens to Active Border. Used for Cancel and secondary actions.
**Icon Button:** Square or slightly rectangular, 28×28px, no label. Ghost background treatment. Lucide icons at 16px, stroke-width 1.5px, in Ash Lavender. On hover, icon shifts to Moonstone White. Used in dock headers and table row actions.
**Destructive:** Same shape as Ghost, but border and label use Ember Red (`#E05C5C`). Only for Delete and Remove actions.

### Cards & Dock Panels
Dock panels use the glass treatment: Obsidian Glass background (`rgba(255,255,255,0.04)`), 1px Ghost Border, `backdrop-filter: blur(16px) saturate(140%)`, `border-radius: 8px`. The top edge gets a 1px border in Active Border (`rgba(255,255,255,0.14)`) to simulate the "rim of the glass" catching light from above. Box shadow: `0 8px 32px rgba(0,0,0,0.6)`.
Dialog modals use the elevated variant: same glass treatment but `border-radius: 12px` and slightly brighter background (`rgba(255,255,255,0.06)`). Backdrop overlay is `rgba(10,10,18,0.85)`.
Dock header strips (the title bar of each panel) are 28px tall, flush with the panel top. They hold the section title in UPPERCASE Ash Lavender Inter 11px + optional icon buttons flush right. A 1px Ghost Border separates the header from the panel body.

### List Rows
Standard row height: **24px** for compact lists (spawn entries, layer rows, waypoints), **36px** for rows with sprite previews (brush palette, item palette).
Default state: transparent background, Moonstone White label.
Hovered state: Lifted Glass background (`rgba(255,255,255,0.07)`).
Selected/Active state: Lifted Glass background + left accent bar (3px wide, full row height, Amethyst Core `#7C5CFC`) flush against the left edge of the panel.

### Inputs & Forms
Text inputs: `background: rgba(255,255,255,0.06)`, 1px border in Ghost Border, `border-radius: 4px`, 8px horizontal padding, Inter 12px. On focus: border becomes Focus Border (`rgba(124,92,252,0.5)`) + subtle Amethyst Glow outer ring.
Coordinate inputs (X/Y/Z fields): same treatment but use JetBrains Mono 14px. Always display with fixed-width sizing. Z field is a `<select>` dropdown (values 0–15), never a free text input.
Dropdowns: same background as inputs, styled chevron icon in Ash Lavender. Open state shows Elevated Surface background with 1px Ghost Border and `border-radius: 6px`.
Checkboxes (tile flags): 14×14px, `border-radius: 3px`, Ghost Border by default. Checked state: Amethyst Core fill with a white checkmark. Disabled: Muted Slate border, no fill.
Progress bars: full-width, height 6px, `border-radius: 3px`. Track color is Ghost Border. Fill color is Amethyst Core. No shimmer animation — a clean linear fill only.
Toggle switches: 32×18px track, `border-radius: 9px`. Default off: Ghost Border track. Active on: Amethyst Core track. Thumb is white, 14×14px.

### Sprite Cells (Item Palette Grid)
Each cell is exactly **36×36px** — this contains a 32×32px Tibia sprite with 2px padding on all sides. Cell background: Lifted Glass. On hover: Focus Border ring (`border: 1px solid rgba(124,92,252,0.5)`). On selected: Amethyst Rim border + Amethyst Glow background.
Grid gap: 2px. The palette container is scrollable vertically, never horizontally.

### Tabs
Used in Brush Palette (Ground / Walls / Doodads / Raw) and Waypoints & Spawns (Spawns / Waypoints). Tabs are inline with the panel header or just below it. Inactive tabs: Ash Lavender label, no border. Active tab: Moonstone White label + 2px Amethyst Core underline — never a filled background pill. Tab switching has no animation.

### Badges & Chips
Hotkey badges: `background: rgba(255,255,255,0.08)`, `border-radius: 4px`, JetBrains Mono 10px in Muted Slate, 4px horizontal padding. Always right-aligned in list rows.
Format badges (OTBM 4, OTMM, etc.): `background: rgba(124,92,252,0.15)`, `border-radius: 4px`, Moonstone White Inter 11px, 6px horizontal padding.
Status badges (✓ valid / ✗ invalid): same shape, fill using 15% opacity of the semantic color. Text uses full saturation of the semantic color.
Position chips (recent positions in Jump dialog): Ghost Border, `border-radius: 20px` (pill), Ash Lavender label, JetBrains Mono 11px.

### Step Indicators (Wizard)
Multi-step dialogs (Asset Loader Wizard) show a horizontal step indicator at the top. Completed steps: filled Amethyst Core circle (16px) with white checkmark. Current step: Amethyst Core outline circle with white number. Upcoming steps: Ghost Border circle with Muted Slate number. Steps connected by a 1px horizontal line in Ghost Border.

---

## 5. Layout Principles

The application is a **canvas-first workspace**. The map canvas always occupies the dominant area — minimum 65% of window width and 80% of window height. Every dock panel is additive and must not crowd the canvas.

### Spacing Scale
Base unit: **4px**. All spacing is a multiple of 4.
| Token | Value | Use |
|---|---|---|
| xs | 4px | Icon gap, badge padding |
| sm | 8px | Dock inner padding (horizontal), row label indent |
| md | 12px | Section gap within panels, input vertical padding |
| lg | 16px | Between panel sections, dialog internal margins |
| xl | 24px | Dialog outer padding, wizard step spacing |
| 2xl | 32px | Dialog from viewport edge, large section gaps |

### Dock Dimensions
| Dock | Width (attached) | Notes |
|---|---|---|
| Brush Palette | 220px | Fixed width, vertical scroll |
| Item Palette | 260px | Fixed width, grid layout |
| Minimap | 180px | Fixed width, 200px height |
| Properties / Inspector | 220px | Fixed width |
| Layers | 200px | Fits 16 floors + 2 group headers without scroll |
| Waypoints & Spawns | 240px | Two-tab layout |

### Dialog Sizes
| Dialog | Size |
|---|---|
| Preferences / Settings | 780px × 560px |
| Map Loading Progress | 480px × 240px |
| Map Properties | 520px × 420px |
| Find Item | 520px × 460px |
| Jump to Position | 340px × 220px |
| Import / Export Map | 540px × 380px |
| House Manager | 720px × 500px |
| Town Manager | 560px × 400px |
| Map File Info | 480px × 440px |
| Asset Loader Wizard | 560px × 400px |
| Client/Server ID Tool | 640px × 420px |
| Clipboard Manager | 260px × 380px (floating) |
| DevTools Overlay | 360px × 280px (floating, canvas-anchored) |

### Grid & Alignment
All text and interactive elements align to the **4px baseline grid**. Row heights are always multiples of 4 (24px, 28px, 36px, 44px, 56px). Icon centers align to row vertical center. No half-pixel offsets.
Dock panels stack vertically in the side columns. When two docks occupy the same column, a 1px Ghost Border divider separates them — no extra spacing.

---

## 6. Depth & Elevation

The application has four elevation levels, each with distinct surface treatment:

| Level | Surface | Context |
|---|---|---|
| 0 — Canvas | Fully opaque, raw map render | The map viewport — no glass, no transparency |
| 1 — Attached Docks | Obsidian Glass (`rgba(255,255,255,0.04)`) + `blur(16px)` | Panels docked to the window edges |
| 2 — Floating Panels | Obsidian Glass + `blur(20px)` + stronger shadow (`0 12px 40px rgba(0,0,0,0.7)`) | Detached docks, Clipboard Manager, DevTools |
| 3 — Dialogs & Modals | Elevated Surface (`rgba(255,255,255,0.06)`) + `blur(24px)` + modal overlay | All dialogs, alerts, progress overlays |

Never apply blur or transparency to the canvas itself. The canvas is always a hard, opaque surface — it is the "ground" everything else hovers over.
The status bar at the bottom of the window is elevation 1 — it shares the dock surface treatment but runs full width.

---

## 7. Do's and Don'ts

### Do
- Use JetBrains Mono for **every** numeric coordinate, item ID, sprite ID, hash value, and debug metric — no exceptions
- Label Floor 7 as "Floor 7 (Ground)" everywhere it appears — this is Tibia's canonical ground floor
- Apply the Amethyst Core left accent bar (`3px × full row height`) to indicate the selected row in every list
- Show coordinates with leading zeros on Z (`07` not `7`)
- Use UPPERCASE + 0.08em letter-spacing for all dock section headings
- Make the map canvas always visually dominant — it should be the first thing the eye lands on
- Show the current floor indicator (badge or status bar) on every screen where the map is visible
- Use the glass rim (1px Active Border on top edge) on every dock panel and dialog

### Don't
- Apply `backdrop-filter` or any transparency to the map canvas
- Use Amethyst Core as a text color — it is for fills, borders, and accents only
- Display Z coordinates without leading zeros
- Use "PyRME" or "Obsidian Cartographer" — the correct name is **Noct Map Editor**
- Round dialog corners beyond 12px or dock corners beyond 8px
- Use a filled background pill for active tabs — always use an underline
- Let any dock panel overlap or resize the map canvas in attached mode
- Use any font other than JetBrains Mono for coordinates, IDs, or debug values
- Show "Floor 0" as the default or canonical ground level — it is Floor 7

---

## 8. Responsive Behavior

Noct Map Editor is a **desktop-only application** (PySide6/Qt target). Minimum window size: 1280px × 720px. The design is not optimized for smaller viewports.

### Dock Collapse Behavior
When the window is narrower than 1440px, side docks can be collapsed to icon-only strips (24px wide) by clicking their header. The dock title and controls hide; only the section icon remains visible. Expanding restores full width with a 150ms ease-out slide animation.
When the window is at minimum width (1280px) with both side columns open, the canvas maintains a minimum of 640px width. If docks would violate this, they auto-collapse the lower-priority dock first (right column before left column).

### Resizable Splitters
The boundary between the canvas and each dock column uses a 4px invisible splitter. Hover state: the 4px area highlights in Amethyst Core at 30% opacity. Drag to resize. The dock column minimum width is 160px; maximum is 380px.

### Touch & Density
Target is mouse-and-keyboard primary. No touch optimization required. Minimum click target for interactive elements: 20×20px (enforced by the 24px row height). Icon buttons are 28×28px minimum.

---

## 9. Agent Prompt Guide

### Branding & Logo Prompt
Logo: "A sleek, minimalist logo of a wolf howling at an amethyst moon."
Theme Name: **Noct Map Editor**

### Quick Color Reference for Prompts
- Background: "deep void black (`#0A0A12`)"
- Panels: "frosted obsidian glass panel with subtle blur"
- Accent: "amethyst purple (`#7C5CFC`)"
- Primary text: "soft moonstone white (`#E8E6F0`)"
- Secondary text: "muted ash lavender (`#9490A8`)"
- Success: "soft verdant green (`#5CBF8A`)"
- Error: "ember red (`#E05C5C`)"
- Warning: "amber caution (`#D4A847`)"

### Prompt Templates by Screen Type

**Dock panel:**
> "Generate a [DOCK NAME] panel for Noct Map Editor. Frosted obsidian glass surface (`rgba(255,255,255,0.04)`) with subtle blur. 28px tall header in UPPERCASE ash lavender Inter 11px. [CONTENT DESCRIPTION]. Amethyst purple (`#7C5CFC`) left bar on selected rows. JetBrains Mono for all coordinate and ID values. Compact density, 24px row height."

**Dialog:**
> "Generate a [DIALOG NAME] dialog for Noct Map Editor. Centered on a semi-transparent overlay (`rgba(10,10,18,0.85)`). Frosted glass dialog surface (`rgba(255,255,255,0.06)`), `border-radius: 12px`. Dialog heading in Inter 14px weight 600 moonstone white. [CONTENT DESCRIPTION]. Footer with ghost Cancel button and solid amethyst purple (`#7C5CFC`) primary action button."

**Full editor shell:**
> "Generate the full editor window for Noct Map Editor, a dark map editor for Tibia. Include a sleek logo of a wolf howling at an amethyst moon. Void black background (`#0A0A12`). Map canvas dominates center (65%+ of width). Frosted glass dock panels on left and right. Horizontal menu bar and toolbar at top. Status bar at bottom showing coordinates in JetBrains Mono. Noct Map Editor design system: amethyst accent (`#7C5CFC`), moonstone white text (`#E8E6F0`), compact density."

### Key Phrases for Stitch Prompts
Always include: "Noct Map Editor", "dark-only glassmorphism", "amethyst accent (`#7C5CFC`)", "JetBrains Mono for coordinates and IDs", "wolf howling at amethyst moon theme"
Describe panels as: "frosted obsidian glass", "subtle translucent surface with backdrop blur", "crystalline dark panel"
Describe the canvas as: "crisp opaque map viewport", "hard dark surface", "the dominant workspace"
Describe selected states as: "amethyst left accent bar", "purple selection ring", "glowing amethyst border"

### Stitch Generation Anti-Patterns to Avoid
- Do not prompt for "light mode" or "white background" variants
- Do not prompt for "rounded pill tabs" — specify "underline tabs"
- Do not describe coordinates as just "text" — always specify "JetBrains Mono monospaced coordinates"
- Do not prompt for "card-based layouts" in the main dock panels — the panels are compact list-based, not card grids
- Do not use the phrases "Ethereal Cartographer", "Obsidian Cartographer" or "PyRME" in any prompt — always use "Noct Map Editor"
