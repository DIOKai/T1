---
name: fivem-mlo-housing
description: Build, fix and use GTA V / FiveM interiors and housing — custom MLOs made in Blender with Sollumz and placed with CodeWalker (rooms, portals, limbo, entity sets, room timecycles, doors, collisions, audio occlusion, _manifest.ymf), vanilla IPL interiors (bob74_ipl, entity sets), and shell-based or IPL-based housing systems (qbx_properties, qb-houses, ps-housing) with furniture and decorating. Use whenever the user wants to make or edit an MLO or interior, put an interior into a building, add a house, apartment, shop or police station interior, set up a housing script, toggle interior props, place furniture, or asks why an interior is invisible, flickers, is dark, lets rain in, or sounds wrong — even if they only say "做屋子", "室内", "MLO", "房子", "公寓", "装修", "ytyp", "ymap", "进去看不到".
---

# FiveM interiors and housing

Three kinds of interior exist in FiveM, and choosing the right one decides everything after:

| Kind | What it is | Good for | Cost |
|---|---|---|---|
| **MLO** | a real interior streamed into the map (`.ytyp` MLO archetype with rooms and portals + `.ymap` placing it) | businesses, police stations, unique houses players walk into from the street | most work; collision, portals and lighting must be right |
| **IPL / vanilla interior** | Rockstar's own interiors switched on with `RequestIpl` and entity sets | apartments, offices, clubs, garages — free and polished | fixed locations and layouts |
| **Shell** | one `.ydr` model spawned as an object far below or above the map, players teleported in | mass housing — hundreds of houses sharing a few layouts | not a real interior: no portals, weather and outside sounds leak in unless the script handles them |

Housing scripts mostly use shells and IPLs; custom MLOs are for places that need to exist at a real address. Read the reference you need:

- `references/mlo-authoring.md` — making an MLO: picking a building, Blender + Sollumz modelling, vertex colours, collisions, ytyp (limbo, rooms, portals, entities, entity sets, flags), export, CodeWalker ymap, `_manifest.ymf`, doors, LODs, audio occlusion.
- `references/interiors-in-scripts.md` — natives for interiors and entity sets, IPLs and bob74_ipl, doors, routing buckets.
- `references/housing-systems.md` — qbx_properties, qb-houses/qb-apartments/qb-interior, ps-housing; shells vs IPL vs MLO in each; furniture and decorating; licences.
- `references/troubleshooting.md` — symptom → cause → fix.

Related skills: `fivem-pro` (Sollumz + CodeWalker basics, resmon), `fivem-script` (housing logic in Lua), `oxlib` / `ox-target` / `ox-inventory` (zones, interactions, stashes), Blender skills `set-dressing`, `archviz`, `prop-artist`, `environment-artist`, `uv-workflow`, `texture-workflow`, `lod-pipeline` (via the `blender` MCP — ask first), `muto-atlas` (vanilla archetype names, ask before `/asset-setup`), `fivem-graphics-pack` (room timecycle looks).

## Workflow

### 1. Pick the kind
Ask what it's for. A house in a housing script → shell or IPL first (qbx_properties already supports both). A specific building on the map players should walk into → MLO. A vanilla interior that already exists → IPL with bob74_ipl. Mention the cost honestly: a first MLO is a multi-day job.

### 2. Building an MLO
Follow `references/mlo-authoring.md`. The short version (Sollumz wiki "Creating Interiors" and the FiveM assets manual):
1. In CodeWalker find the building; export its `.ydr`, textures, `.ybn` (both `name.ybn` and `hi@name.ybn`) and `.ymap` to XML.
2. Import into Blender with Sollumz; model the inside aligned to the building; convert to a Drawable; Sollumz shaders, DDS power-of-two textures; vertex colours (R night AO, G artificial light, B moonlight).
3. Cut the doorway out of the exterior collision; make the interior collision (Bound Composite) with sensible materials.
4. YTYP: base archetypes for the meshes, one **MLO** archetype; **Create Limbo Room first**, then one room per space, bounds from the collision; portals at every doorway and window, made from inside to outside (`Room → Limbo`); add the meshes as entities and attach them to rooms.
5. Export XML from Sollumz, import with CodeWalker RPF Explorer; in CodeWalker add a `.ymap` with an entity whose archetype is the MLO name at the right position, **Calculate Extents** and **Calculate All Flags**, then **Tools → Manifest Generator → `_manifest.ymf`**.
6. Resource: everything in `stream/`, `fxmanifest.lua` with `this_is_a_map 'yes'`.

### 3. Using interiors from scripts
Entity sets (furniture variants, upgrades, damage states) are toggled with `ActivateInteriorEntitySet` / `DeactivateInteriorEntitySet` + `RefreshInterior` on the interior id from `GetInteriorAtCoords`. Vanilla interiors: `RequestIpl` or bob74_ipl's API. Details and examples: `references/interiors-in-scripts.md`.

### 4. Housing system
Follow `references/housing-systems.md`. Default recommendation for a Qbox server: qbx_properties (free, GPL-3, maintained, built-in decorating). For QBCore: qb-houses + qb-apartments + qb-interior (GPL-3). ps-housing is archived and CC BY-NC-SA (no commercial use — a server with paid perks counts). Paid housing scripts are out.

### 5. Check
Run `python .claude/skills/fivem-mlo-housing/scripts/check_mlo_resource.py <resource> [export-folder]` (local, read-only, Python only). Point it at both the map resource and the folder with the Sollumz/CodeWalker `.ytyp.xml`/`.ymap.xml`. It catches:
- **Manifest:** missing `this_is_a_map`; a custom `.ytyp` without `_manifest.ymf` or `DLC_ITYP_REQUEST`; `data_file` paths that match nothing, including the audio `.dat` → `.dat151.rel` convention; XML left in `stream/`.
- **Files:** files without an RSC7 header; assets over 16/48 MiB, decoded the same way FXServer does; duplicate file or archetype names across resources.
- **MLO structure:** room 0 not limbo; portals pointing at missing rooms or the same room; portals without 4 corners; wrong `portalCount`; rooms with no portal; `attachedObjects` indices past the entity list; entities in no room (invisible inside); duplicate entity-set names.
- **Doors:** door archetypes without the Dynamic and Enable Door Physics flags.
- **ymap:** zero streaming extents; MLO instances whose archetype isn't in the local ytyp.

Then test in game: walk in and out through every portal, look out of every window, check day and night, rain, sound from outside, and at least two players at once (shells and instancing).

## Ground rules
- Free tools only: Blender, Sollumz (GPL-3), CodeWalker, OpenIV, ht_mlotool (LGPL-3) for audio occlusion. Paid MLOs, paid housing scripts and paid "MLO packs" are out; never redistribute a purchased or leaked MLO.
- Edit copies of vanilla files exported from the user's own game; don't download "fixed" vanilla files from strangers.
- Don't invent flag values, natives or config keys — use the references, which cite the Sollumz wiki/source, the FiveM docs and source, citizenfx/natives, and the scripts' own configs.
- Driving Blender through the `blender` MCP and running a local server/MCP need asking first, per the project rules.
