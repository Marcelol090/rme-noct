# M022: Welcome Dialog — PLAN

## Milestone
**M022 — Welcome Dialog (Startup Screen)**
Branch: `gsd/M022/S01`
Worktree: `.worktrees/m022-welcome-dialog`

## Design System Reference
Tokens from `.stitch/DESIGN.md` — Noct Map Editor.

### Quick Token Reference
- Primary CTA: Amethyst Core `#7C5CFC`, hover Deep Amethyst `#4F3DB5`
- Ghost button: `rgba(255,255,255,0.08)` border, Ash Lavender `#9490A8` text
- Card surface: Obsidian Glass `rgba(255,255,255,0.04)` + 1px Ghost Border
- Glass rim: 1px `rgba(255,255,255,0.14)` top border
- Selected row: Lifted Glass `rgba(255,255,255,0.07)` + 3px Amethyst left bar
- Hovered row: Lifted Glass `rgba(255,255,255,0.07)`
- Header: Elevated Surface `rgba(255,255,255,0.09)`
- Background: Void Black `#0A0A12`
- Text primary: Moonstone White `#E8E6F0`
- Text secondary: Ash Lavender `#9490A8`
- Text disabled: Muted Slate `#4A4860`
- Status compatible: Verdant Green `#5CBF8A`
- Status mismatch: Amber Caution `#D4A847`
- Status error: Ember Red `#E05C5C`
- Font UI: Inter 12px/400, headers 11px/600 UPPERCASE 0.08em
- Font mono: JetBrains Mono for versions/IDs
- Spacing: 4px base grid
- Border radius: cards 8px, buttons 6px, inputs 4px

---

## Tasks

### Phase 1: Component Foundation

#### T01 — StartupButton component (3 min)
- [x] RED: Primary = Amethyst Core bg, white label
- [x] RED: Secondary (Ghost) = ghost border, Ash Lavender label
- [x] RED: hover state color changes
- [x] RED: disabled state = Muted Slate
- [x] GREEN: `pyrme/ui/components/startup_button.py`
- [x] REFACTOR: shared style helpers
- Design: `border-radius: 6px`, height 36px, Inter 12px/500

#### T02 — StartupCard component (3 min)
- [x] RED: Obsidian Glass bg + Ghost Border
- [x] RED: glass rim (1px Active Border top)
- [x] RED: UPPERCASE header 0.08em tracking, Inter 11px/600
- [x] GREEN: `pyrme/ui/components/startup_card.py`
- Design: `border-radius: 8px`, blur 16px, header 28px

#### T03 — StartupListBox component (4 min)
- [x] RED: list items 24px row height
- [x] RED: hover state = Lifted Glass
- [x] RED: selected row = 3px Amethyst left accent bar
- [x] RED: emit selection signal + index
- [x] GREEN: `pyrme/ui/components/startup_list.py`
- Design: primary text Moonstone White, secondary Ash Lavender, 24px rows

#### T04 — StartupInfoPanel component (3 min)
- [x] RED: render key-value fields
- [x] RED: field labels = UPPERCASE Ash Lavender 11px
- [x] RED: field values = correct font (Inter text, JetBrains Mono versions)
- [x] GREEN: `pyrme/ui/components/startup_info.py`

### Phase 2: Dialog Shell

#### T05 — WelcomeDialog layout (5 min)
- [x] RED: min size 1180×720
- [x] RED: 5 panels (header, actions, recent, clients, footer)
- [x] RED: header = title + subtitle + prefs button
- [x] RED: quick actions = New Map + Browse Map buttons
- [x] RED: footer = status text + force load checkbox + load button
- [x] GREEN: `pyrme/ui/dialogs/welcome_dialog.py` layout
- Design: token integration from Phase 1

#### T06 — Theme integration (2 min)
- [x] RED: bg = Void Black `#0A0A12`
- [x] RED: header = Elevated Surface
- [x] RED: cards = Obsidian Glass
- [x] GREEN: wire theme tokens to stylesheet

### Phase 3: Behavioral Wiring

#### T07 — Fixture data models (3 min)
- [x] RED: `StartupRecentMapEntry` (path, modified label, ephemeral)
- [x] RED: `StartupConfiguredClientEntry` (name, path, version id)
- [x] RED: `StartupCompatibilityStatus` enum 5 states
- [x] GREEN: `pyrme/ui/models/startup_models.py`

#### T08 — Map selection + info display (4 min)
- [x] RED: map list selection → update map info panel
- [x] RED: map info = peeked OTBM data (stub)
- [x] RED: no selection = empty state
- [x] GREEN: wire map selection → info panel

#### T09 — Client selection + info display (3 min)
- [x] RED: client list selection → update client info panel
- [x] RED: client info = version, path, OTB version
- [x] RED: no clients = empty state message
- [x] GREEN: wire client selection → info panel

#### T10 — Auto-client matching (4 min)
- [x] RED: map selection → auto-select match client (OTB major/minor)
- [x] RED: manual client selection persists
- [x] RED: fallback to first client if no match
- [x] GREEN: implement auto-match logic

#### T11 — Compatibility status engine (3 min)
- [x] RED: Compatible → green status, Load enabled
- [x] RED: ForceRequired → amber status, Load disabled
- [x] RED: Forced (checkbox) → amber status, Load enabled
- [x] RED: MissingSelection → Ash Lavender status, Load disabled
- [x] RED: MapError → red status, Load disabled
- [x] GREEN: status computation + msg generation

#### T12 — Button event emission (3 min)
- [x] RED: Load button emit load event (path + client id + force flag)
- [x] RED: Browse button open file dialog (mock) + add to list
- [x] RED: New Map emit new map event
- [x] RED: Exit close dialog
- [x] GREEN: wire button signals

### Phase 4: Integration

#### T13 — MainWindow startup flow (4 min)
- [x] RED: MainWindow shows WelcomeDialog on startup
- [x] RED: load event triggers map open flow
- [x] RED: new map event creates blank editor tab
- [x] RED: Preferences round-trip (open → close → refresh clients)
- [x] GREEN: wire WelcomeDialog into MainWindow launch

#### T14 — Logo + polish (3 min)
- [x] Gen wolf-howling-at-amethyst-moon logo (40px)
- [x] Add to header panel
- [x] Final visual review

---

## Verification

```bash
# Per-task
C:\Python312\python.exe -m pytest tests\python\test_welcome_dialog.py -v --tb=short
C:\Python312\python.exe -m pytest tests\python\test_startup_components.py -v --tb=short

# Full suite
C:\Python312\python.exe -m pytest tests\python\ -q --tb=short --ignore=tests\python\test_rust_io.py
```

## Stop Condition
14 tasks green. Dialog launch from MainWindow. 260+ tests pass (no regressions). Visual match Noct design tokens.
