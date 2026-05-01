# M030/S01 - Autoborder Rules Contract

Plan source: `docs/superpowers/plans/2026-05-01-m030-autoborder-rules.md`

## Scope

- pure Rust autoborder rule module
- legacy edge mapping
- deterministic 8-neighbour resolver
- stable placement plan output
- Rust tests only

## Tasks

- [x] T01: pure edge contract and rule model
- [x] T02: deterministic resolver and stable plan output
- [x] T03: closeout docs and state

## Stop Condition

S01 done when `cargo test -p rme_core autoborder --quiet` passes and plan output matches legacy edge contract.
