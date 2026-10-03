# carcols.meta and carvariations.meta: modkits, liveries, sirens, lights

Sources: CodeWalker CarColsFile.cs / CarVariationsFile.cs (field types), FiveM source ModKitIdRelocation.cpp, CFX-Software/carcols-id-fixer, cpast/SirenSetting_Limit_Remover, LividDS/lds-lorevehicles (real examples), Curiosity-GitHub/addon-liveries, citizenfx/natives.

## carcols.meta

Root `<CVehicleModelInfoVarGlobal>` with `<Kits>`, `<Lights>`, `<Sirens>`.

### Kits (modkits)
```xml
<Kits>
  <Item>
    <kitName>2048_mycar_modkit</kitName>
    <id value="2048" />
    <kitType>MKT_SPECIAL</kitType>
    <visibleMods> ... </visibleMods>
    <linkMods> ... </linkMods>
    <statMods> ... </statMods>
    <slotNames />
    <liveryNames />
  </Item>
</Kits>
```
- `kitType`: `MKT_STANDARD`, `MKT_SPORT`, `MKT_SUV`, `MKT_SPECIAL`.
- **`visibleMods` items** (one per tuning part): `modelName` (the part .yft), `modShopLabel` (text key — add an AddTextEntry for it), `linkedModels`, `turnOffBones` (bones hidden when fitted, e.g. the stock bumper), `type`, `bone` (where it attaches), `collisionBone`, `cameraPos` (`VMCP_DEFAULT`…), `audioApply`, `weight`, `turnOffExtra`, `disableBonnetCamera`, `allowBonnetSlide`.
- **`type` values**: `VMT_SPOILER`, `VMT_BUMPER_F`, `VMT_BUMPER_R`, `VMT_SKIRT`, `VMT_EXHAUST`, `VMT_CHASSIS`, `VMT_GRILL`, `VMT_BONNET`, `VMT_WING_L`, `VMT_WING_R`, `VMT_ROOF`, `VMT_PLTHOLDER`, `VMT_PLTVANITY`, `VMT_INTERIOR1`–`5`, `VMT_SEATS`, `VMT_STEERING`, `VMT_KNOB`, `VMT_PLAQUE`, `VMT_ICE`, `VMT_TRUNK`, `VMT_HYDRO`, `VMT_ENGINEBAY1`–`3`, `VMT_CHASSIS2`–`5`, `VMT_DOOR_L`, `VMT_DOOR_R`, `VMT_LIVERY_MOD`, `VMT_ENGINE`, `VMT_BRAKES`, `VMT_GEARBOX`, `VMT_HORN`, `VMT_SUSPENSION`, `VMT_ARMOUR`, `VMT_TURBO`, `VMT_TYRE_SMOKE`, `VMT_HYDRAULICS`, `VMT_XENON_LIGHTS`, `VMT_WHEELS`, `VMT_WHEELS_REAR_OR_HYDRAULICS` (CodeWalker enum).
- **`linkMods`**: extra models that always attach with a part (`modelName`, `bone`, `turnOffExtra`), e.g. mirrors on `door_pside_f`.
- **`statMods`**: performance upgrades — `identifier`, `modifier value`, `audioApply`, `weight`, `type`. Example values from lds: ENGINE 75/150/225/300, BRAKES 25/65/100, GEARBOX 70/120/180, ARMOUR 20–100; horns use an `identifier` like `HORN_TRUCK`.
- Part bones must be GTA's fixed bone names (muto-atlas `/vehicle`); `turnOffBones` typically hides `misc_*` or stock part bones.

### Modkit ids — the most common car-pack bug
- `id` is a 16-bit number. FiveM relocates the modkit index array to **65536** entries and removes the vanilla 1024 bounds check, so FiveM accepts ids **0–65535**; vanilla Legacy caps at 1023. (FiveM source: ModKitIdRelocation.cpp; carcols-id-fixer README)
- Every id is a single global slot. Two kits with the same id overwrite each other → the tuning menu is empty, shows another car's parts, or parts float.
- Recommendation: use ids **≥ 1024** (can't collide with vanilla) and keep one registry for the server (e.g. a text file listing id → car). Run `check_vehicle_resource.py resources/[cars]` to find collisions. CFX-Software/carcols-id-fixer can bulk-reassign ids in downloaded packs (it counts down from 65535).
- Naming convention `<id>_<model>_modkit` (e.g. `2048_mycar_modkit`) keeps the id visible; whether the number in the name has to match is unverified — keep them equal to avoid confusion.
- Scripts must call `SetVehicleModKit(vehicle, 0)` before `SetVehicleMod` (natives doc) — index 0 = the first kit in carvariations.

### Sirens
- `<Sirens><Item><id value="190"/><name>…</name>` + timing/flash settings + a `<sirens>` list of up to **20 lights**, one per bone `siren1`…`siren20`.
- Siren-setting ids are **one byte**: usable 1–254 (carcols-id-fixer); above 255 overflows and collides. Shared ids between resources = wrong patterns.
- SirenSetting Limit Adjuster (SSLA) raises ids to 65535 and lights to 32, but it's a client ASI every player must install, and the Enhanced client runs in pure mode (no client mods) — don't rely on it.
- Siren glass: in Sollumz set the collision child's shattermap mode to `MANUAL_NO_SHATTERMAP`.

### Lights
`<Lights><Item><id value="65"/>` with indicator / headLight / tailLight / reversingLight settings and coronas. Light-setting ids are also one byte (usable 1–255) and global — same collision rules as sirens.

## carvariations.meta

```xml
<CVehicleModelInfoVariation>
  <variationData>
    <Item>
      <modelName>mycar</modelName>
      <colors>
        <Item>
          <indices content="char_array">0 0 0 156 0 0</indices>
          <liveries>
            <Item value="false" />
          </liveries>
        </Item>
      </colors>
      <kits>
        <Item>2048_mycar_modkit</Item>
      </kits>
      <windowsWithExposedEdges />
      <plateProbabilities>
        <Probabilities>
          <Item><Name>Standard White</Name><Value value="100" /></Item>
        </Probabilities>
      </plateProbabilities>
      <lightSettings value="0" />
      <sirenSettings value="0" />
    </Item>
  </variationData>
</CVehicleModelInfoVariation>
```
- `colors`: each `<Item>` is one spawn colour combination. `indices` order: primary, secondary, pearlescent, wheel, then interior trim and dashboard. Palette indices: Cfx docs vehicle-references/vehicle-colors. The `liveries` bool array ties a combination to livery indices.
- `kits`: must equal the carcols `kitName`. Vanilla kits (e.g. a `0_default_modkit`) can be referenced too.
- `plateProbabilities`: values should total 100.
- `lightSettings` / `sirenSettings`: point at carcols ids; 0 = none/default.

## Liveries

**Method A — texture liveries (simplest):** set `FLAG_HAS_LIVERY` in vehicles.meta; the game cycles liveries from the vehicle's texture dictionary, up to 30 (Cfx docs vehicle-flags). Textures are conventionally `<model>_sign_1`, `_sign_2`, … and the paint material must reference the sign texture (community; exact shader slot unverified). DDS with full mipmaps. `GetVehicleLiveryCount` returns -1 when the vehicle has none.

**Method B — modkit livery parts:** separate `.yft` files (e.g. `mycar_livery1.yft`) listed in carcols `visibleMods` with `<type>VMT_LIVERY_MOD</type>` and `<bone>chassis</bone>`; selected through the mod system. The Curiosity-GitHub/addon-liveries guide removes `FLAG_HAS_LIVERY` for this method. Good for many liveries or for police/EMS packs where liveries are added later without touching the base ytd.

Kits also have `<liveryNames />` / `<livery2Names />`; their exact use (roof livery / livery2) is unverified.
