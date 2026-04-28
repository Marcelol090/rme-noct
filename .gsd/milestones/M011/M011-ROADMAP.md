# M011 - Sprite Asset Provider Roadmap

## Goal

Introduce a renderer-facing provider seam that supplies `SpriteCatalog` and `SpriteAtlas` inputs together for live sprite draw planning.

## Slices

| Slice | Title | Status |
|---|---|---|
| S01 | CANVAS-120-SPRITE-ASSET-PROVIDER | Complete |

## Future Work

- Connect the provider seam to real client asset discovery.
- Build atlas placement and texture ownership after provider ownership is stable.
- Add renderer-host sprite painting only after command and asset contracts are verified.
