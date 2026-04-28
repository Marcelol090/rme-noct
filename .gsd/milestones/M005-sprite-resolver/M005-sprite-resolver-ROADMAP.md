# M005-sprite-resolver: Sprite resolver seam

**Vision:** Add a tested sprite-resource lookup layer that lets renderer frame work ask for item artwork data without adding a real draw pass.

## Slices

- [x] **S01: CANVAS-60-SPRITE-RESOLVER-CONTRACT** `risk:medium` `depends:[]`
  > Define and test a Python-facing resolver contract that maps item ids to sprite resource results using existing DAT/SPR capabilities, including honest missing-item and missing-sprite statuses.

- [x] **S02: CANVAS-61-FRAME-SPRITE-RESOURCES** `risk:medium` `depends:[S01]`
  > Let frame-plan tile commands request sprite resources for ground and stack items without changing the renderer host draw path.

- [x] **S03: CANVAS-62-SPRITE-RESOLVER-DIAGNOSTICS** `risk:low` `depends:[S02]`
  > Surface sprite resolution counts and missing-resource diagnostics in the renderer host without claiming visual sprite parity.

## Stop Condition

Stop when visible frame tiles can be translated into cached sprite resource results with tested success and failure states, while the renderer still draws only diagnostics.
