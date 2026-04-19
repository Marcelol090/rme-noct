# M004-render-primitives Context

## Purpose

Consume the verified M003 frame plan in the renderer host as drawable diagnostic primitives before adding sprite atlas or real tile renderer work.

## Legacy Basis

Legacy redux separates `MapDrawer` orchestration from lower-level draw primitives and sprite rendering. Python now mirrors that progression: frame plan first, primitive projection second, sprite draw later.

## Boundary

This milestone draws simple diagnostic tile rectangles from visible tile commands. It does not load sprites, atlas metadata, lighting, or screenshots.
