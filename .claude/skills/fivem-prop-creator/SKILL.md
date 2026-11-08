---
name: fivem-prop-creator
description: Use when making, converting, fixing or packaging a GTA V or FiveM prop (.ydr .yft .ydd .ytd .ytyp) with Blender, Sollumz and CodeWalker, including collision, LODs, textures, archetype flags, pushable or breakable props, doors, animated props, hand-held props, DLC_ITYP_REQUEST, and props that are invisible, fall through, have no collision or fail to spawn. Triggers include 做道具, 自制道具, 道具不显示, 道具没碰撞, 可以推动的道具, 门, 手持道具, ytyp, ydr. Not for MLO interiors (fivem-mlo-housing), vehicles or weapons.
---

# FiveM Prop Creator

A prop is four linked things: a model (`.ydr`/`.yft`/`.ydd`), its textures (embedded or `.ytd`), its collision (embedded bounds), and an archetype in a `.ytyp` whose **name = model file name**. Most "invisible / no collision / won't spawn" reports are a broken link between them, not a bad mesh.

Before building, establish: game edition (Legacy or Enhanced), Sollumz/Blender/CodeWalker versions, real size, how it is used (static decor, pushable, breakable, door, animated, hand-held, light), and whether it is new or replaces a vanilla model. Use free tools; ask before driving the user's Blender through the `blender` MCP.

## 1. Choose the container

| Container | Use for | Notes |
|---|---|---|
| `.ydr` Drawable | static or simply-dynamic props: chair, cone, cup, phone, door | embedded bounds and textures allowed; vanilla prop_chair_01a, prop_table_06, v_ilev_ph_door01 |
| `.yft` Fragment | anything that breaks, separates or swings, or must **collide while animated** | bones with physics + one collision per physics bone, Strength -1 = moves but never breaks off; archetype must be **Dynamic** |
| `.ydd` Drawable Dictionary | LOD models, instanced sets | **embedded collision does not work in a YDD** (Sollumz docs) |

Details: [asset-pipeline.md](references/asset-pipeline.md), [doors-fragments-animated.md](references/doors-fragments-animated.md).

Where the model comes from: real-size products → `blender-product-modeling` (photo only → its `references/image-to-fivem-prop.md`, local Hunyuan3D); common objects → `free-3d-assets`; vehicles, shoes, weapons have their own skills (`blender-vehicle-modeling`, `blender-shoe-modeling`, `fivem-weapon`). Before modelling anything new, watch a YouTube modelling tutorial for that kind of object and trace real reference photos (LESSONS).

## 2. Workflow

1. **Model**: real scale, transforms applied, origin where it is placed (bottom centre), held (grip point) or hinged (door edge). UV map named `UVMap 0`; vertex colour `Color 1` (Face Corner, Byte Color) or it glows pink at night / is black in an MLO.
2. **Collision**: primitives first (Bound Box/Cylinder/Sphere/Capsule; inside a BVH use Bound Poly Box), poly mesh only where primitives cannot fit. Apply Flag Preset **General (Default)** to every Bound GeometryBVH — skipping it is the most common reason collision does nothing. Scale stays 1, extents never 0, pick a collision material (footsteps, bullets, mass). Parent the composite under the Drawable (embedded). [collisions-and-flags.md](references/collisions-and-flags.md)
3. **LODs**: world props get High + one Medium at about 15–30% of High; hand-held and MLO furniture keep one level. Sollumz LOD Tools can decimate.
4. **Shaders and textures**: `default` / `normal_spec` / `*_cutout` / `emissivenight` / `glass_*` / `*_tnt` by need. DDS, power of two, full mips, DXT1 opaque, DXT5 alpha, BC5 normals; 256² normal, 512² for big faces.
5. **YTYP archetype**: Auto-Create, then set lodDist, flags, special attribute, texture dictionary. Never leave Sollumz defaults (lodDist 200, hdTextureDist 100) untouched.
6. **Package**: binaries in `stream/`, `data_file 'DLC_ITYP_REQUEST' 'stream/<name>.ytyp'`. [placing-and-streaming.md](references/placing-and-streaming.md)
7. **Place**: script (`CreateObject`, `PlaceObjectOnGroundProperly`, `SetModelAsNoLongerNeeded`) or a ymap + `_manifest.ymf` (CodeWalker: Calculate Extents, Calculate All Flags, Manifest Generator).
8. **Check** (section 5), then test on the local test server.

## 3. Budgets measured from vanilla Legacy props

Measured 2026-11-08 from the user's own GTA V with CodeWalker.Core (28 props). These are what Rockstar shipped, not engine limits.

| Class | High tris | LODs | archetype lodDist |
|---|---|---|---|
| hand-held (cup, phone, burger, tools) | 64–440 | High only | 10–30 |
| street prop / furniture (cone, chair, bench, bin) | 600–2,300 | + Medium 15–30%, switch 15–50 m | 60–140 |
| large (container, tree, wreck) | up to ~5,300 | 2–3 levels | up to 260 |
| MLO furniture | 1,300–4,000 | High only | 30 |

Textures: 256² typical, never above 1024² on a measured prop, DXT1/DXT5, full mip chain. Collision: almost all primitives (chair = 17 boxes, poly meshes at most 126 polygons). A prop over FXServer's 16 MiB warning is thousands of times a vanilla street prop. More: [lods-textures-budgets.md](references/lods-textures-budgets.md).

## 4. Flags, special attributes, loading

- **Dynamic (flag 18)** for anything pushable or physical — every measured street prop has it (usually with 23/24 "no cover" + 30). **Static (flag 6)** only for MLO furniture that must never move. Never both.
- Animated: Has Anim (10) or UV Anims (11) + Auto Start Anim (20) + a clip dictionary.
- **Doors**: Dynamic + Enable Door Physics (27) + special attribute 7 normal, 8 sliding gate, **10 sliding vertical (Benny's roller door)**, 5 garage door that tilts up; 9 barrier and 12 rail-crossing also exist. The Cfx part 8 page says Garage Door (5) for the Benny's template; its own video and the vanilla `lr_prop_supermod_door_01` say 10. Vanilla `v_ilev_bl_door_l` and gates use attribute 0 + flag 27, which Sollumz says should do nothing — **unverified**, so follow Cfx 7/8/10/5 and test in game.
- **DLC_ITYP_REQUEST matches by file name only** (FiveM `LoadStreamingFile.cpp` ParseBaseName): `stream/x.ytyp` finds `stream/[Props]/sub/x.ytyp`. Fine for prop ytyps; **never for MLO ytyps** on this server (crash — the `.ymf` loads those).
- `this_is_a_map 'yes'` only reloads the map store (ymaps). A spawn-only prop library does not need it; a resource with ymaps does.

## 5. Check

```
py -3 -I .claude/skills/fivem-prop-creator/scripts/check_prop_resource.py <resource or folder> [--json]
```

Read-only, standard library. Reads compiled YTD/YDR/YTYP directly (texture format/mips, LOD triangles, embedded collision, archetype fields, MLO detection) and Sollumz XML (BVH flag presets). Cfx escrow files start with `FXAP`: content unverifiable, never decrypt. Codes and fixes: [acceptance.md](references/acceptance.md). Not readable: `.yft` internals, binary bound flags. Before release run `fivem-asset-acceptance`'s `asset_gate.py`.

## 6. Common mistakes

- No Flag Preset on the BVH → walk-through prop; render mesh reused as collision → heavy and snaggy.
- ytyp not requested, or a glob like `*ytyp.` that matches nothing → invisible / CreateObject fails.
- 2048² A8R8G8B8 textures (the user's `wood_table_v2.ytd` = 64 MiB, over 48 MiB).
- Flags 0 or Static on a pushable prop; fragment without Dynamic.
- Collision only in a separate `.ybn` (world-placed map collision; use by a spawned prop **unverified**) — embed it.
- XML left in `stream/` or renamed to `.ydr`.

## 7. Ground rules

- Conversions keep `.ydr/.yft/.ytd` 1:1; report size problems, never compress or decimate unasked (LESSONS).
- Real-product shapes: symmetric parts symmetric, supports really supporting, nothing passing through (LESSONS).
- Report paths, versions, archetype names and pass / fail / not-run. A render or a clean checker run is not an in-game test.

Sources and video timestamps: [sources.md](references/sources.md).
