---
name: set-dressing
description: Set dressing and environmental storytelling placement for interiors and exteriors using prop density, narrative clusters, and readability rules via MCP. Also furnishing from a real store cart (buyable furniture list with links, prices and real W×D×H, models scaled to real size, shopping list CSV) — 真实家具清单, 可购买家具, 购物车家具, Airbnb 布置.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: set dressing, dressing, storytelling props, interior dressing, clutter, narrative placement, set decals, buyable furniture, shopping list, store cart, Mercado Livre, IKEA dimensions
  related-skills: prop-artist, scene-assembly, environment-artist, horror-style, qa-review
---

# Set Dressing

Story through placement. Controlled clutter. Readable clusters.

## When to Use

- Interior/exterior dressing passes
- Narrative prop clusters
- Avoiding empty or overstuffed spaces
- After modular layout is locked

## Workflow

```
Layout locked → Hero narrative props → Secondary clusters
  → Background filler → Decals/wear → Lighting check → QA
```

## Density Rules

| Zone | Density |
|------|---------|
| Hero interact zone | High intent, low noise |
| Midground | Supporting story clusters |
| Background | Sparse; silhouette only |
| Traversal path | Clearance for player/camera |

## Cluster Method

1. Pick a story beat (meal abandoned, workbench used, escape rushed)
2. Place 3–7 props that sell the beat
3. Add 1–2 wear/decal cues
4. Stop — do not fill every surface

## Prop Sources

- `prop-artist` for unique pieces
- Kitbash / modular libraries for filler
- Instance repeats; vary rotation/scale slightly

## Buyable Furniture

Furnishing from a real store/cart: keep the furniture list first (name, link, price, W×D×H), check it with `scripts/furniture_list_check.py`, use free stand-in models scaled to the real size and mark substitutes. Read `references/buyable-furniture.md`.

## Horror / Sparse Styles

- Fewer props, more meaning
- Negative space intentional
- Coordinate with `horror-style` / `psx-horror-style`

## Constraints

### MUST DO
- Dress after greybox navigation works
- Keep player/camera paths clear
- Instance repeated meshes

### MUST NOT DO
- Uniform clutter wallpaper
- Block doors/windows without story reason

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Story Clusters | `references/story-clusters.md` | When needed |
| Density Map | `references/density-map.md` | When needed |
| Buyable Furniture | `references/buyable-furniture.md` | Furnishing from a real store cart / shopping list |
