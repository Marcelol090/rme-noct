# M005-sprite-resolver Context

## Purpose

Create the first honest sprite resolution seam after diagnostic tile primitives and before any real renderer draw pass.

## Legacy Basis

Legacy redux resolves item metadata and sprite resources before lower-level drawing consumes them. Python already has visible tile frame planning and diagnostic primitive projection; the next renderer capability is to turn `TileState.ground_item_id` and `TileState.item_ids` into sprite-resource results without pretending that GL or wgpu sprite rendering exists yet.

## Boundary

This milestone resolves item ids into sprite ids and sprite pixel payload/status through the existing DAT/SPR parsing foundation. It does not implement atlas packing, lighting, animation, screenshots, OpenGL sprite drawing, or wgpu.

## Current Constraints

- `GSD auto` and Ollama are not required for this milestone; slices are materialized manually.
- `git fetch origin` currently fails locally with a socket/DNS startup error, so no rebase or publish should happen until network health returns.
- `npm install` did not restore `node_modules/.bin/gsd.cmd` under the current Node/npm runtime, so CLI-backed GSD status remains unavailable.
