# M022: Welcome Dialog — PLAN

## Milestone
**M022 — Welcome Dialog (Startup Screen)**
Branch: `gsd/M022/S01`
Worktree: `.worktrees/m022-welcome-dialog`

## Design System Reference
All tokens from `.stitch/DESIGN.md` — Noct Map Editor.

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
- [ ] RED: test Primary variant renders with Amethyst Core bg, white label
- [ ] RED: test Secondary (Ghost) variant renders with ghost border, Ash Lavender label
- [ ] RED: test hover states change colors correctly
- [ ] RED: test disabled state uses Muted Slate
- [ ] GREEN: implement `pyrme/ui/components/startup_button.py`
- [ ] REFACTOR: extract shared style helpers
- Design: `border-radius: 6px`, height 36px, Inter 12px/500

#### T02 — StartupCard component (3 min)
- [ ] RED: test card renders with Obsidian Glass bg + Ghost Border
- [ ] RED: test glass rim (1px Active Border top)
- [ ] RED: test UPPERCASE header with 0.08em tracking, Inter 11px/600
- [ ] GREEN: implement `pyrme/ui/components/startup_card.py`
- Design: `border-radius: 8px`, blur 16px, header 28px

#### T03 — StartupListBox component (4 min)
- [ ] RED: test renders list items at 24px row height
- [ ] RED: test hover state applies Lifted Glass
- [ ] RED: test selected row has 3px Amethyst left accent bar
- [ ] RED: test emits selection signal with index
- [ ] GREEN: implement `pyrme/ui/components/startup_list.py`
- Design: primary text Moonstone White, secondary Ash Lavender, 24px rows

#### T04 — StartupInfoPanel component (3 min)
- [ ] RED: test renders key-value fields
- [ ] RED: test field labels are UPPERCASE Ash Lavender 11px
- [ ] RED: test field values use correct font (Inter for text, JetBrains Mono for versions)
- [ ] GREEN: implement `pyrme/ui/components/startup_info.py`

### Phase 2: Dialog Shell

#### T05 — WelcomeDialog layout (5 min)
- [ ] RED: test dialog has minimum size 1180×720
- [ ] RED: test all 5 panels present (header, actions, recent, clients, footer)
- [ ] RED: test header shows title + subtitle + preferences button
- [ ] RED: test quick actions has New Map + Browse Map buttons
- [ ] RED: test footer has status text + force load checkbox + load button
- [ ] GREEN: implement `pyrme/ui/dialogs/welcome_dialog.py` layout
- Design: use all tokens from Phase 1 components

#### T06 — Theme integration (2 min)
- [ ] RED: test dialog background is Void Black `#0A0A12`
- [ ] RED: test header uses Elevated Surface
- [ ] RED: test cards use Obsidian Glass
- [ ] GREEN: wire theme tokens into dialog stylesheet

### Phase 3: Behavioral Wiring

#### T07 — Fixture data models (3 min)
- [ ] RED: test `StartupRecentMapEntry` holds path, modified label, ephemeral flag
- [ ] RED: test `StartupConfiguredClientEntry` holds name, path, version id
- [ ] RED: test `StartupCompatibilityStatus` enum has all 5 states
- [ ] GREEN: implement data models in `pyrme/ui/models/startup_models.py`

#### T08 — Map selection + info display (4 min)
- [ ] RED: test selecting map in list updates map info panel
- [ ] RED: test map info shows peeked OTBM data (stub)
- [ ] RED: test no map selected shows empty state
- [ ] GREEN: wire map list selection → info panel update

#### T09 — Client selection + info display (3 min)
- [ ] RED: test selecting client in list updates client info panel
- [ ] RED: test client info shows version, path, OTB version
- [ ] RED: test no clients shows empty state message
- [ ] GREEN: wire client list selection → info panel update

#### T10 — Auto-client matching (4 min)
- [ ] RED: test map selection auto-selects matching client (OTB major/minor match)
- [ ] RED: test manual client selection persists across map changes
- [ ] RED: test fallback to first client when no match found
- [ ] GREEN: implement auto-matching logic

#### T11 — Compatibility status engine (3 min)
- [ ] RED: test Compatible → green status, Load enabled
- [ ] RED: test ForceRequired → amber status, Load disabled
- [ ] RED: test Forced (checkbox) → amber status, Load enabled
- [ ] RED: test MissingSelection → Ash Lavender status, Load disabled
- [ ] RED: test MapError → red status, Load disabled
- [ ] GREEN: implement status computation + message generation

#### T12 — Button event emission (3 min)
- [ ] RED: test Load button emits load event with path + client id + force flag
- [ ] RED: test Browse button opens file dialog (mock) and adds to list
- [ ] RED: test New Map emits new map event
- [ ] RED: test Exit closes dialog
- [ ] GREEN: wire button signals

### Phase 4: Integration

#### T13 — MainWindow startup flow (4 min)
- [x] RED: test MainWindow shows WelcomeDialog on startup
- [x] RED: test load event triggers map open flow
- [x] RED: test new map event creates blank editor tab
- [x] RED: test Preferences round-trip (open → close → refresh clients)
- [x] GREEN: wire WelcomeDialog into MainWindow launch

#### T14 — Logo + polish (3 min)
- [x] Generate wolf-howling-at-amethyst-moon logo (40px)
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
All 14 tasks green. Dialog launches from MainWindow. 260+ tests pass (no regressions). Visual match with Noct design tokens.
