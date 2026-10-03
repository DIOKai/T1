# Resource layout and meta files

Sources are listed per section. "Source code" means the citizenfx/fivem repository (commit e34d12c, 2026-09-30); "Cfx docs" means citizenfx/fivem-docs (commit c2b2125, 2026-10-01), the source of docs.fivem.net. "Community" marks practice seen in real resources but not stated by Cfx/Rockstar.

## Contents
1. Folder layout
2. fxmanifest.lua template
3. data_file types
4. Display names (AddTextEntry)
5. Names that must match across files
6. stream/ file naming
7. vehicles.meta
8. vehiclelayouts.meta
9. Custom engine sound

---

## 1. Folder layout

```
mycar/
├── fxmanifest.lua
├── vehicle_names.lua          # AddTextEntry display names (client script)
├── data/
│   ├── vehicles.meta
│   ├── handling.meta
│   ├── carcols.meta           # only if modkit / sirens / custom lights
│   ├── carvariations.meta
│   └── vehiclelayouts.meta    # only if no vanilla layout fits
├── stream/
│   ├── mycar.yft
│   ├── mycar_hi.yft           # only if the model has a Very High LOD
│   ├── mycar.ytd
│   └── mycar+hi.ytd           # only if HD textures were split out
└── stream_enhanced/           # optional: Gen9 assets for the GTA V Enhanced client
```

- Everything under `stream/` (recursively, sub-folders allowed) is streamed automatically; it does **not** go in the manifest. (Source code: ResourceStreamComponent.cpp)
- Every meta file needs **both** a `files {}` entry and a `data_file` line. (Cfx docs: resource-manifest, data_file)
- Streaming entries are keyed by file name, so two resources streaming the same file name conflict — keep file names unique per vehicle.
- On the Enhanced client, a resource with a `stream_enhanced/` folder loads assets only from there; without it, `stream/` still works but is deprecated. (Cfx docs: legacy-vs-enhanced; Enhanced patch notes 2026-09-22)

## 2. fxmanifest.lua template

```lua
fx_version 'cerulean'
game 'gta5'

files {
  'data/vehicles.meta',
  'data/handling.meta',
  'data/carcols.meta',
  'data/carvariations.meta',
  -- 'data/vehiclelayouts.meta',
}

data_file 'HANDLING_FILE'          'data/handling.meta'
data_file 'VEHICLE_METADATA_FILE'  'data/vehicles.meta'
data_file 'CARCOLS_FILE'           'data/carcols.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/carvariations.meta'
-- data_file 'VEHICLE_LAYOUTS_FILE' 'data/vehiclelayouts.meta'

client_script 'vehicle_names.lua'
```

- `fx_version 'cerulean'` + `game 'gta5'` is the standard pair; since `adamant` a game must be specified. (Cfx docs)
- Globs work in both places, e.g. `files { 'data/**/*.meta' }` and `data_file 'HANDLING_FILE' 'data/**/handling.meta'`. Useful for car packs. (Cfx docs: data_file supports globbing)
- **Order of data_file lines doesn't matter for handling and layouts**: FiveM stable-sorts mounted data files so `VEHICLE_LAYOUTS_FILE` and `HANDLING_FILE` load first. The old forum advice "put vehiclelayouts above vehicles.meta" is unnecessary. (Source code: LoadStreamingFile.cpp, LoadDataFiles)

## 3. data_file types

Use exactly these names (Cfx docs: game-references/data-files):

| File | Type |
|---|---|
| handling.meta | `HANDLING_FILE` |
| vehicles.meta | `VEHICLE_METADATA_FILE` |
| carcols.meta | `CARCOLS_FILE` |
| carvariations.meta | `VEHICLE_VARIATION_FILE` |
| vehiclelayouts.meta | `VEHICLE_LAYOUTS_FILE` |
| game.dat151.rel / sounds.dat54.rel / dat10 / .awc folder | `AUDIO_GAMEDATA` / `AUDIO_SOUNDDATA` / `AUDIO_SYNTHDATA` / `AUDIO_WAVEPACK` |
| vehicle weapons | `WEAPONINFO_FILE` |
| others sometimes seen | `CONTENT_UNLOCKING_META_FILE`, `VEHICLE_SHOP_DLC_FILE`, `VEHICLEEXTRAS_FILE`, `VFXVEHICLEINFO_FILE`, `EXPLOSION_INFO_FILE` |

- An unknown type is ignored and the client logs `Could not add data_file %s - invalid type %s.` (Source code: LoadStreamingFile.cpp)
- **`TEXTFILE_METAFILE` (dlctext.meta) is refused on purpose** ("these don't work and will fail to unload"). Delete dlctext.meta from FiveM resources. (Source code)
- Many templates contain `data_file 'DLCTEXT_FILE'` and `'CARCONTENTUNLOCKS_FILE'` — neither is a valid type, so those lines do nothing. Remove them.

## 4. Display names (AddTextEntry)

```lua
-- vehicle_names.lua (client_script)
CreateThread(function()
  AddTextEntry('MYCAR', 'My Car GT')   -- key = vehicles.meta <gameName>
  AddTextEntry('DIO', 'Dio Motors')    -- key = <vehicleMakeName>
  -- also one entry per carcols <modShopLabel> so tuning parts have names
end)
```

The key is hashed case-insensitively (joaat); entries are removed when the resource stops. (Source code: TextChangingFunctions.cpp.) Using `gameName` as the key is the observed convention (`GetDisplayNameFromVehicleModel` returns it) — community.

## 5. Names that must match across files

| This value | Must equal | If not |
|---|---|---|
| vehicles.meta `modelName` | `<modelName>.yft` file name; carvariations `<modelName>` | car won't spawn / no colours or kit |
| vehicles.meta `txdName` | `<txdName>.ytd` file name; txdRelationships `<child>` | untextured / invisible parts |
| vehicles.meta `handlingId` | handling.meta `<handlingName>` | falls back to **Adder** handling; log: `Couldn't find handling for hash %08x - returning ADDER instead!` (Source code: CrashFixes.cpp) |
| carvariations `<kits><Item>` | carcols `<kitName>` | tuning menu empty |
| carvariations `sirenSettings` / `lightSettings` | carcols `<Sirens>` / `<Lights>` `<id>` | wrong siren pattern / light colours |
| vehicles.meta `layout` | a vanilla `LAYOUT_*` name or a name in your vehiclelayouts.meta | wrong seats / entry animations |
| vehicles.meta `audioNameHash` | a loaded audio bank (vanilla car name or your sound resource's bank) | no / wrong engine sound |

The bundled `check_vehicle_resource.py` checks all of these that can be checked without the game.

Also across resources: a `handlingName` loaded by two resources — the **last loaded wins** and the earlier one comes back when that resource stops (Source code: HandlingDataManager.cpp). Same `modelName` in two resources conflicts too.

## 6. stream/ file naming

| File | Meaning |
|---|---|
| `<model>.yft` | main fragment (High/Medium/Low/Very Low LODs = L0–L3) |
| `<model>_hi.yft` | high-detail fragment; Sollumz writes it only when a mesh has a **Very High** LOD (built from that level only) |
| `<model>.ytd` | texture dictionary (= `txdName`) |
| `<model>+hi.ytd` | HD textures; the base .ytd then holds a half-resolution copy. Loaded within vehicles.meta `HDTextureDist` |
| `<frag>+hifr.ytd` | HD dictionary for embedded fragment textures (Sollumz) |
| tuning parts, e.g. `mycar_bumf1.yft` | free-form names, linked only by carcols `visibleMods/Item/modelName`. Convention `<prefix>_<slot><n>` (bumf, bumr, skirt, chas, boot, roof…) |
| livery parts, e.g. `mycar_livery1.yft` | referenced by `VMT_LIVERY_MOD` items in carcols |

(Sollumz source: yft/yftexport.py, ytd/*; vanilla pairs like `zeno_hi.yft` / `zeno+hi.ytd` in FiveM's LoadStreamingFile.cpp)

## 7. vehicles.meta

Root `<CVehicleModelInfo__InitDataList>` → `<residentTxd>vehshare</residentTxd>`, `<InitDatas><Item>…</Item></InitDatas>`, `<txdRelationships>`. Start from a vanilla or known-good add-on entry (e.g. LividDS/lds-lorevehicles) rather than writing from scratch — there are many fields and missing ones fall back to defaults.

Key fields:
- `modelName` (lowercase, = .yft), `txdName` (= .ytd), `handlingId` (= handlingName), `gameName` (text label key), `vehicleMakeName`, `audioNameHash`, `layout`.
- `type`: `VEHICLE_TYPE_CAR` (others: `_BIKE`, `_HELI`, `_PLANE`, `_BOAT`, `_TRAILER`, `_QUADBIKE`, `_SUBMARINE`, `_BICYCLE`).
- `vehicleClass`: `VC_COMPACT`, `VC_SEDAN`, `VC_SUV`, `VC_COUPE`, `VC_MUSCLE`, `VC_SPORT_CLASSIC`, `VC_SPORT`, `VC_SUPER`, `VC_MOTORCYCLE`, `VC_OFF_ROAD`, `VC_INDUSTRIAL`, `VC_UTILITY`, `VC_VAN`, `VC_CYCLE`, `VC_BOAT`, `VC_HELICOPTER`, `VC_PLANE`, `VC_SERVICE`, `VC_EMERGENCY`, `VC_MILITARY`, `VC_COMMERCIAL`, `VC_RAIL`, `VC_OPEN_WHEEL` (same order as `GetVehicleClass` 0–22). Watch for typos like `VC_COMPACTS` in downloaded packs.
- `wheelType`: `VWT_SPORT`, `VWT_MUSCLE`, `VWT_LOWRIDER`, `VWT_SUV`, `VWT_OFFROAD`, `VWT_TUNER`, `VWT_BIKE`, `VWT_HIEND`, `VWT_SUPERMOD1`, `VWT_SUPERMOD2` (CodeWalker VehiclesFile.cs).
- `plateType`: `VPT_FRONT_AND_BACK_PLATES`, `VPT_BACK_PLATES`, `VPT_NONE`. `dashboardType`: `VDT_*` (e.g. `VDT_RACE`, `VDT_SULTAN`).
- `lodDistances content="float_array"`: 6 floats; vanilla-style `15 30 60 120 500 500`. Which slot maps to which LOD is not documented — copy a similar vanilla car's values and test vehicles disappearing/popping at distance.
- `HDTextureDist`: distance at which `+hi.ytd` loads (e.g. 5.0).
- `flags` (Cfx docs: vehicle-flags): e.g. `FLAG_HAS_LIVERY` (cycles up to 30 liveries from the vehicle's texture dictionary), `FLAG_SPORTS`, `FLAG_RICH_CAR`, `FLAG_LAW_ENFORCEMENT`, `FLAG_EMERGENCY_SERVICE`, `FLAG_NO_RESPRAY`, `FLAG_IS_ELECTRIC`, `FLAG_EXTRAS_ALL`, `FLAG_DONT_SPAWN_IN_CARGEN`. Only use names from the Cfx flag list.
- `txdRelationships`: `<Item><parent>vehicles_sultan_interior</parent><child>mycar</child></Item>` lets the car reuse shared vanilla interior textures (chains can stack).
- `wheelScale` / `wheelScaleRear`: reported not to resize the tyre mesh (community).

## 8. vehiclelayouts.meta

Root `<CVehicleMetadataMgr>`; sections for clip sets, seat infos, seat anims, entry points, entry anims, drive-by, cover offsets, and `VehicleLayoutInfos`. It controls seats, entry/exit points and their animations, drive-by animations and cover offsets.

Only ship one when no vanilla layout fits (unusual seat positions, RHD, odd doors, extra seats). Otherwise reference a vanilla name in vehicles.meta: `LAYOUT_STANDARD`, `LAYOUT_LOW`, `LAYOUT_LOW_RESTRICTED`, `LAYOUT_4X4`, `LAYOUT_VAN`, `LAYOUT_RANGER`, `LAYOUT_STD_EXITFIXUP` (community practice; e.g. ~100 cars in lds-lorevehicles mostly reuse vanilla). Copy the layout of the vanilla car the model is closest to (muto-atlas `/vehicle <vanilla>` shows it).

## 9. Custom engine sound

Pattern from alberttheprince/AddonCarSounds (community):

```lua
files { '**/**/*.dat151.rel', '**/**/*.dat54.rel', '**/**/*.awc' }
data_file 'AUDIO_GAMEDATA'  'audioconfig/roxanne_game.dat'    -- on disk: roxanne_game.dat151.rel
data_file 'AUDIO_SOUNDDATA' 'audioconfig/roxanne_sounds.dat'  -- on disk: roxanne_sounds.dat54.rel
data_file 'AUDIO_WAVEPACK'  'sfx/dlc_roxanne'                 -- folder with roxanne.awc, roxanne_npc.awc
```

- The data_file path drops the numeric suffix and `.rel`. `AUDIO_SYNTHDATA` covers `.dat10.rel` if present.
- vehicles.meta `<audioNameHash>` must be the **audio bank name** (here `roxanne`), not the car's name.
- The same README says audio data_files can't be globbed and the sound resource should be `ensure`d before the car (community, unverified).
- Simplest option: reuse a vanilla engine sound by setting `audioNameHash` to a vanilla car name of the same class.
