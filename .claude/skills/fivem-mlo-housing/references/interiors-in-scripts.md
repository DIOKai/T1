# Interiors from scripts

Native names from citizenfx/natives (`INTERIOR`, `STREAMING`, `OBJECT`) and the FiveM CFX natives. Lua names shown.

## Interior id and entity sets

```lua
local interior = GetInteriorAtCoords(x, y, z)          -- 0 if none loaded there
if interior ~= 0 then
    PinInteriorInMemory(interior)                        -- optional: keep it loaded while editing
    while not IsInteriorReady(interior) do Wait(0) end
    ActivateInteriorEntitySet(interior, 'dio_set_party')
    DeactivateInteriorEntitySet(interior, 'dio_set_empty')
    SetInteriorEntitySetColor(interior, 'dio_set_party', 2)   -- tint index, if the set's props support tints
    RefreshInterior(interior)                            -- changes appear after a refresh
end
```

- Entity set names come from the MLO archetype's `entitySets` (unique per MLO).
- Entity sets are **client-side**: every client must apply them. Sync the state from the server (state bags or a callback) and apply on join and when entering the area, not just once.
- `IsInteriorEntitySetActive(interior, name)` reads the state. `GetInteriorFromEntity(PlayerPedId())` and `GetRoomKeyFromEntity` tell you where a player is.

## Vanilla interiors (IPLs)

`RequestIpl('name')` / `RemoveIpl('name')` / `IsIplActive('name')` load and unload Rockstar map sections (many online interiors and "map hole" fixes). Don't hand-roll this for every interior — use **bob74_ipl** (MIT): it loads the fixes and exposes a per-interior API (its wiki lists each interior's functions and the defaults `LoadDefault()` sets) for styles, entity sets and colours. bob74_ipl calls `RefreshInterior` after changes and uses `EnableExteriorCullModelThisFrame` where exteriors would clip.

Two resources toggling the same IPL or entity set fight each other; pick one owner per interior.

## Doors

Door-lock scripts (ox_doorlock, qb-doorlock) are simplest. Natively: `AddDoorToSystem(hash, model, x, y, z, ...)`, `DoorSystemSetDoorState(hash, state, ...)`, `DoorSystemGetDoorState(hash)`. Custom doors only move if their archetype has a door special attribute and the Dynamic + Enable Door Physics flags (see `mlo-authoring.md`).

## Instancing with routing buckets

Shells stacked at the same coordinates (or IPL apartments shared by many owners) need players separated: `SetPlayerRoutingBucket(source, bucket)` and `SetEntityRoutingBucket` on the server; each bucket is its own world. `SetRoutingBucketPopulationEnabled(bucket, false)` stops ambient peds/cars. qbx_properties avoids buckets for shells by spawning each property's shell under its own street location (`shellUndergroundOffset`), so players in different houses never overlap.

## Shells: things the script must handle

A shell is an ordinary object, so the game thinks the player is outdoors:
- weather and rain reach inside → disable rain or freeze weather/time for that player while inside (weather sync resources offer an "inside" toggle);
- outside traffic and ambience can be heard → keep shells far from roads (deep underground or high up);
- spawn the shell before teleporting and freeze it (`FreezeEntityPosition`); fade the screen; wait for collision around the player;
- delete the shell and all furniture on exit and on resource stop.

## Furniture placement

Spawn props client-side (`CreateObjectNoOffset` with network false) from saved data, so they cost nothing for other players. Use a gizmo for placement — qbx_properties has one built in; `object_gizmo` (GPL-3, ox_lib) exposes `exports.object_gizmo:useGizmo(entity)` for custom scripts. Validate on the server: owner, object model on an allow-list, count limits per property, coordinates inside the property bounds.
