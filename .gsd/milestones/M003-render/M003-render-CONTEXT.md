# M003-render Context

## Purpose

Build the first honest draw-planning seam after the renderer host and viewport model were verified in M002.

## Legacy Basis

- `remeres-map-editor-redux/source/rendering/map_drawer.cpp` owns the legacy render orchestration layer.
- `remeres-map-editor-redux/source/rendering/tile_renderer.cpp` and the drawer stack consume map state through ordered passes.
- Python does not yet have sprite batching, atlas loading, light passes, screenshots, or `wgpu`.

## Boundary

This milestone starts with a pure frame plan derived from `MapModel` plus `EditorViewport.visible_rect()`. It does not draw sprites or pixels.
