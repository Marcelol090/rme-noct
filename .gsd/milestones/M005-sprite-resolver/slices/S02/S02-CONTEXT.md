# S02 Context - CANVAS-61-FRAME-SPRITE-RESOURCES

## Purpose

Use the S01 resolver contract from frame-plan resource collection so visible tile commands can request sprite resources before a real draw pass exists.

## Existing Inputs

- `RenderFramePlan.tile_commands` already lists visible tile commands in stable order.
- Each `RenderTileCommand` carries `ground_item_id` and `item_ids`.
- `SpriteResourceResolver.resolve_item()` returns cached `SpriteResourceResult` objects.

## Honest Boundary

This slice should produce pure resource data from frame plans. It must not paint sprites, pack atlases, add renderer host visual claims, or change diagnostic primitive rendering.
