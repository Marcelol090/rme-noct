# M030 Roadmap - Autoborder rules

## S01 - AUTOBORDER-RULES-CONTRACT

Create the pure autoborder rule core:

- map legacy edge names to stable border types
- validate autoborder rule tables
- resolve 8-neighbour plans deterministically
- preserve optional and target-filter fields
- keep Rust tests local to `rme_core`

## Follow-up

Next slice should only consume the plan, not reinterpret legacy rules:

- map or UI seams can adopt `AutoborderPlan` later
- preview rendering stays out of scope for this milestone
