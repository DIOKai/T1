# Making an MLO (Blender + Sollumz + CodeWalker)

Sources: Sollumz wiki "Creating Interiors" and ytyp docs, Sollumz/szio source (`ytyp/properties/flags.py`, `cwxml/ytyp.py`, `cwxml/ymap.py`), FiveM assets manual (fivem-docs `assets-manual/beginner-series` parts 4, 6, 8), ht_mlotool docs.

## Files and how they fit

| File | Role |
|---|---|
| `.ydr` | the interior meshes (shell, props) — Drawables |
| `.ytd` | textures (or embedded in the `.ydr`) |
| `.ybn` | collision; vanilla buildings have `name.ybn` and `hi@name.ybn` (the `hi@` one is high-detail, e.g. for bullets) |
| `.ytyp` | archetype definitions: one per model, plus one **MLO archetype** holding rooms, portals, entities, entity sets, timecycle modifiers |
| `.ymap` | places things in the world; an MLO is placed with a `CMloInstanceDef` entity whose `archetypeName` = the MLO archetype name |
| `_manifest.ymf` | ytyp ↔ ymap dependencies; FiveM docs: generating it in CodeWalker "is necessary to load the models correctly" |
| `.ymt` + `.dat151.rel` | audio occlusion (optional) |

Resource: all of these in `stream/` (audio `.rel` in another folder), and `fxmanifest.lua`:

```lua
fx_version 'cerulean'
game 'gta5'
lua54 'yes'
this_is_a_map 'yes'
```

`this_is_a_map` marks the resource as a map and reloads the map store when it loads (fivem-docs manifest reference; `ResourcesTest.cpp`).

## 1. Pick and extract the building

Start small (one or two rooms). In CodeWalker find the building, note its model and `.ymap` names, and in RPF Explorer export to XML: the `.ydr`, its textures, every `.ybn` touching it (both `name` and `hi@name`), the ground and decals around it, and the `.ymap`(s). Export from **the user's own game files**.

## 2. Model (Blender + Sollumz)

- Import the `.ydr`/`.ybn` XML first, then the `.ymap` (it gives the exact world placement).
- Align a working plane to the building (select a face, `Shift+Num7`, cursor to it, add plane aligned to cursor).
- Keep a linked duplicate at the world location ("Location" object) and move the original to the origin; you'll copy the location into CodeWalker later.
- Model floor, walls, ceiling; leave openings for doors and windows; then **Sollumz Tools → Drawable → Convert to Drawable** (the mesh goes to the High LOD).
- If the exterior must change (doorway, windows), edit a copy of the vanilla building and stream it under the **same name**, together with edited `.ybn`s.

## 3. Texture and vertex colour

- Sollumz shader materials (e.g. `normal.sps` for colour + normal map). Textures must be **DDS** and **power-of-two** sizes; embed them or put them in a `.ytd`.
- Vertex colour attribute `Color 1` (Face Corner, Byte Color) drives lighting: **R** = night ambient occlusion (high = dark at night), **G** = artificial light (fake glow near lamps), **B** = moonlight reflection. A dark interior at night is often all-red vertex colour with no lights.
- Put real lights in the `.ydr` (Sollumz lights, light flags, flashiness) — an interior without lights is pitch black at night.

## 4. Collision

- Cut a hole in the exterior `.ybn` at the doorway (check from inside too).
- Duplicate the interior shell, unparent, convert to **Bound Composite** with "Apply flag preset", assign collision materials matching the surfaces (footsteps and bullet effects use them). Use a different floor material per room so room ids can be set.

## 5. YTYP: archetypes, rooms, portals

In **Sollumz Tools → Archetype Definition**:
1. New YTYP; select the drawables → type **Base** → *Auto-Create From Selected*; select the collision → type **MLO** → *Auto-Create From Selected*.
2. **Rooms:** *Create Limbo Room* first (room 0 = limbo = "outside"), then `+` for each room; set each room's bounds with *Set Bounds From Selection* on the collision's corner vertices.
3. **Portals:** one per opening between two rooms, or between a room and limbo (doors **and windows**). Select the 4 corners of the opening and create the portal from **inside to outside** (`Room → Limbo`); flip it if the arrow points the wrong way. An opening without a portal is a wall you can't see through.
4. **Entities:** add the meshes as entities and assign each to its room (or to a portal, e.g. a door in the doorway). An entity in no room isn't drawn when you're inside.
5. Optional: **entity sets** (groups of entities toggled by script), **timecycle** per room (`timecycleName`, e.g. vanilla `int_*` modifiers, for interior lighting mood), room and portal flags.

Room flags (Sollumz `RoomFlags`, value = bit): 1 Freeze Vehicles, 2 Freeze Peds, 4 No Directional Light, 8 No Exterior Lights, 16 Force Freeze, 32 Reduce Cars, 64 Reduce Peds, 128 Force Directional Light On, 256 Dont Render Exterior, 512 Mirror Potentially Visible.

Portal flags (`PortalFlags`): 1 One Way, 2 Link Interiors Together, 4 Mirror, 8 Disable Timecycle Modifier, 16 Mirror Using Expensive Shaders, 32 Low LOD Only, 64 Hide When Door Closed, 128 Mirror Can See Directional, 256 Mirror Using Portal Traversal, 512 Mirror Floor, 1024 Mirror Can See Exterior View, 2048 Water Surface, 4096 Water Surface Extend To Horizon, 8192 Use Light Bleed.

XML shape (what `check_mlo_resource.py` reads): `CMapTypes/archetypes/Item[@type="CMloArchetypeDef"]` with `entities`, `rooms` (`name`, `bbMin`/`bbMax`, `timecycleName`, `flags`, `portalCount`, `attachedObjects`), `portals` (`roomFrom`, `roomTo`, `flags`, `corners` ×4, `attachedObjects`, `audioOcclusion`), `entitySets`, `timeCycleModifiers`.

## 6. Export and place

1. Sollumz → Export (objects must be visible). Import the XML into a folder with CodeWalker RPF Explorer (drag in) to get binaries.
2. CodeWalker → open the folder in the project manager → new **ymap** → new entity → set the archetype to the **MLO archetype name** → paste the location from Blender (Sollumz *Object Location & Rotation Tools* copy button).
3. **Calculate Extents** and **Calculate All Flags** on the ymap, name it, save.
4. **Tools → Manifest Generator → Generate → save `_manifest.ymf`.**
5. Copy binaries (not XML) into `stream/`.

## Doors (fivem-docs part 8)

Origin at the hinge (swinging), bottom corner (sliding/gate) or bottom centre (garage); start from a vanilla template door; in the ytyp set **Special Attribute** Normal Door (7) / Sliding Door (8) / Garage Door (5) and archetype flags **Dynamic** + **Enable Door Physics**. Locking is done by a door-lock script (e.g. ox_doorlock) or the door-system natives.

## LODs (fivem-docs part 6)

For things visible from far away: HD and LOD drawables, two ymaps (HD entity `LODTYPES_DEPTH_HD`, LOD entity `LODTYPES_DEPTH_LOD` at the same position, `ChildLodDist` = HD `LodDist`), HD ymap's **Parent** = LOD ymap, HD `ParentIndex` 0, LOD `NumChildren` 1, regenerate the manifest. MLO interiors themselves rarely need this.

## Audio occlusion (optional, ht_mlotool)

Without it, outside sound passes through walls oddly. ht_mlotool (LGPL-3, needs ox_lib and CodeWalker) runs on a dev server: stand in the MLO, `/openmlo` (admin), set values per room/portal, *Generate Audio Occlusion Files*, convert the XML with CodeWalker, then:

```lua
this_is_a_map 'yes'
files { 'audio/**/*.rel' }
data_file 'AUDIO_GAMEDATA' 'audio/my_map/XXXXXXXX_game.dat'   -- path stops at .dat on purpose
-- stream/my_map/<hash>.ymt , audio/my_map/XXXXXXXX_game.dat151.rel
```

Restart the server to test (the tool warns a resource restart alone may not pick changes up and can crash clients).

## Performance

Keep texture dictionaries under the 16 MiB memory warning (see `fivem-graphics-pack` → textures), reuse vanilla props where possible (no streaming cost), use entity sets instead of duplicate MLOs for variants, and check `resmon`/FPS inside.
