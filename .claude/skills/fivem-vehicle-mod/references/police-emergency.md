# Police, EMS and fire vehicles

Sources: FiveM docs vehicle flags; real add-on packs' meta files (lds-lorevehicles); citizenfx/natives `SET_VEHICLE_EXTRA`; qbx_police / qbx_core and qb-policejob configs; Renewed-Sirensync, pma-sirensync, Luxart Vehicle Control, ELS-FiveM, WMServerSirens and Live Lights READMEs/configs; Sollumz wiki (siren glass); muto-atlas bone tags.

A modded police car is a normal add-on vehicle (everything in the other references applies) plus five things: **emergency flags and class**, **siren lights** (bones + a carcols siren setting), **liveries**, **extras** (lightbars, push bars, equipment toggled on/off), and **siren sound/control** in game.

## 1. Model: lights, extras, liveries

- Start from a vanilla emergency car (`police`, `police2`, `police3`, `sheriff`, `fbi`, `ambulance`, `firetruk`…) or a civilian base of the same shape; see `modeling-sollumz.md`.
- **Siren lights**: each light is a bone `siren1` … `siren20` (tags 24999+n per muto-atlas). Light glass meshes are skinned to their bone; the carcols siren setting (below) decides colour, rotation and flash per bone. Siren glass collision: shattermap mode **Simple** in current Sollumz (older guides say `MANUAL_NO_SHATTERMAP` — same intent: break fully, no shattermap).
- **Extras**: parts on bones `extra_1`, `extra_2`, … (muto-atlas lists `extra_1`–`extra_4`, `extra_ten`, `extra_11`, `extra_12`; scripts loop ids 1–20) — remember **extra 10 is `extra_ten`**. Typical: lightbar variants, push bar, spotlight, cage, antennas, slicktop/marked.
- **Liveries**: department markings via texture liveries (`FLAG_HAS_LIVERY`, `<model>_sign_N`) or modkit livery parts (`VMT_LIVERY_MOD`) — see `modkits-liveries-sirens.md`. Packs that add liveries later usually use modkit liveries.

## 2. Meta files

`vehicles.meta` (real pack example, castella police variant):

```xml
<vehicleClass>VC_EMERGENCY</vehicleClass>
<flags>FLAG_EXTRAS_STRONG FLAG_HAS_LIVERY FLAG_LAW_ENFORCEMENT FLAG_EMERGENCY_SERVICE FLAG_NO_RESPRAY FLAG_DONT_SPAWN_IN_CARGEN ...</flags>
```

Flag meanings (FiveM docs): `FLAG_LAW_ENFORCEMENT` — helicopter searchlights, wanted-level dynamics; `FLAG_EMERGENCY_SERVICE` — ped reactions and how theft is perceived; `FLAG_EXTRAS_STRONG` — extras don't break off; `FLAG_EXTRAS_ALL` — spawn with all extras; `FLAG_EXTRAS_REQUIRE` — at least one extra; `FLAG_EXTRAS_MATCH_LIVERY` — extra matching the livery id; `FLAG_HAS_LIVERY` — texture liveries (up to 30); `FLAG_NO_RESPRAY`; `FLAG_DONT_SPAWN_IN_CARGEN` — not parked around the map.

`carvariations.meta` links the siren setting: `<sirenSettings value="190"/>` (and `<lightSettings>`). `plateProbabilities` can force a government plate.

`carcols.meta` defines the siren setting:

```xml
<Sirens>
  <Item>
    <id value="190"/>                <!-- one byte: 1–254, unique on the server -->
    <name>dio_pd_pattern</name>
    <timeMultiplier value="1"/>
    <lightFalloffMax value="100"/> <lightFalloffExponent value="200"/>
    <lightInnerConeAngle value="2.29"/> <lightOuterConeAngle value="30"/>
    <textureName>VehicleLight_misc_searchlight</textureName>
    <sequencerBpm value="110"/>
    <leftHeadLight><sequencer value="0"/></leftHeadLight>   <!-- wig-wag headlights -->
    <rightHeadLight><sequencer value="0"/></rightHeadLight>
    <leftTailLight><sequencer value="0"/></leftTailLight>
    <rightTailLight><sequencer value="0"/></rightTailLight>
    <useRealLights value="true"/>
    <sirens>
      <Item>   <!-- one per siren bone, in order: siren1, siren2, ... (max 20) -->
        <rotation> <delta/><start/><speed/><sequencer value="…"/><multiples/><direction/><syncToBpm/> </rotation>
        <flashiness> <delta/><start/><speed/><sequencer value="…"/><multiples/><direction/><syncToBpm/> </flashiness>
        <corona> <intensity/><size/><pull/><faceCamera/> </corona>
        <color value="0xFFFF1405"/>   <!-- ARGB -->
        <intensity value="0.5"/> <lightGroup value="0"/>
        <rotate value="true"/> <scale value="true"/> <scaleFactor value="10"/>
        <flash value="true"/> <light value="true"/> <spotLight value="true"/> <castShadows value="false"/>
      </Item>
    </sirens>
  </Item>
</Sirens>
```

- `sequencer` is a 32-bit on/off pattern stepped at `sequencerBpm`: `4294967295` (all bits) = always on, `0` = off; complementary patterns such as `2863311530` (0xAAAAAAAA) and `1431655765` (0x55555555) alternate — give left and right lights complementary patterns for a wig-wag.
- `rotate` + `rotation.speed` make rotating beacons; `flash` + `flashiness.sequencer` make LED flashers.
- **Ids are one byte** and shared server-wide: two packs both using 190 → one gets the other's pattern. Keep a list; `check_vehicle_resource.py` reports duplicates and ids > 255 across every scanned resource. SSLA (more ids/lights) is a client mod — not for FiveM servers, never on Enhanced.
- **Design patterns live**: *Live Lights* (free RagePluginHook plugin for **single-player** GTA V) edits every siren parameter in game and imports/exports carcols.meta. It runs on the user's PC in story mode only — ask before suggesting the install.

## 3. Extras and liveries from scripts

`SetVehicleExtra(vehicle, extraId, disable)` — the third argument is **disable**: `false`/0 turns the extra **on**, `true`/1 turns it **off** (citizenfx/natives note). Check `DoesExtraExist` first. qbx_core wraps it the readable way: `qbx.setVehicleExtra(veh, id, enable)` calls `SetVehicleExtra(veh, id, not enable)`.

Police job configs:
- **qbx_police** `config/client.lua`: `authorizedVehicles[grade] = { spawnname = 'Label' }` per grade; `vehicleSettings[model] = { extras = { [1] = true, ... }, livery = 1 }` applied on spawn (`qbx.setVehicleExtras`, `SetVehicleLivery`).
- **qb-policejob** `config.lua`: `Config.AuthorizedVehicles`, `Config.VehicleSettings` (extras/livery per model), `Config.CarItems` (trunk items on spawn), `Config.WhitelistedVehicles`.
Add each new model's **spawn name** (= `modelName`) there, with the extras and livery the department should get.

## 4. Siren sound and control

GTA's default siren is one button and badly synced. Servers replace it with a siren controller that mutes the vanilla siren (`SetVehicleHasMutedSirens`) and plays tones with `PlaySoundFromEntity`, synced through state bags:

| Resource | Notes | Licence |
|---|---|---|
| **Renewed-Sirensync** | ox_lib; Q lights, E horn, R hold/cycle, Left Alt siren toggle; per-model groups of tones in `config.lua` (`sirenModes`, `horn`, optional `audioRef` for custom banks); `sirenShutOff`, damaged-siren options | MIT |
| pma-sirensync | the TypeScript original; moved to Renewed-Sirensync | MIT |
| Luxart Vehicle Control v3 | feature-rich, siren packs and server-side audio tester available | GPL-3 |
| ELS-FiveM | old ELS with per-vehicle VCF files driving extras as lights; development branch only | GPL-3 |

Vanilla tone names used by these configs: `VEHICLES_HORNS_SIREN_1`, `VEHICLES_HORNS_SIREN_2`, `VEHICLES_HORNS_POLICE_WARNING`, `SIRENS_AIRHORN`, fire/EMS `RESIDENT_VEHICLES_SIREN_FIRETRUCK_QUICK_01`, `..._WAIL_01`, `VEHICLES_HORNS_AMBULANCE_WARNING`, `VEHICLES_HORNS_FIRETRUCK_WARNING`.

A sirensync README warns: if another resource calls `GetSoundId()` without `ReleaseSoundId()`, the sound limit fills and sirens break — look there first when sirens go silent after a while.

**Custom siren sounds (server-side)**: an audio resource ships a wave pack and sound data:

```lua
files { 'dlc_mysirens/sirenpack_one.awc', 'data/mysirens_sounds.dat54.nametable', 'data/mysirens_sounds.dat54.rel' }
data_file 'AUDIO_WAVEPACK'  'dlc_mysirens'
data_file 'AUDIO_SOUNDDATA' 'data/mysirens_sounds.dat'      -- path stops at .dat
```

and the controller requests the bank (`RequestScriptAudioBank('DLC_MYSIRENS\\SIRENPACK_ONE', false)`) and plays its sound names (`audioRef` in Renewed-Sirensync). WMServerSirens is the well-known template, but its licence is **non-commercial** — fine to learn from, not for a monetised server. Only use siren recordings you have the right to use.

## 5. Checklist

- [ ] `VC_EMERGENCY` + `FLAG_LAW_ENFORCEMENT` / `FLAG_EMERGENCY_SERVICE` (checker: `EMERGENCY_FLAGS`)
- [ ] siren setting defined, id unique and ≤ 254, ≤ 20 lights (checker: `SIREN_ID_DUPLICATE`, `SIREN_ID_RANGE`, `SIREN_ID_UNDEFINED`, `SIREN_LIGHTS_OVER_20`)
- [ ] siren bones `siren1…N` match the number of `<sirens>` items; siren glass breaks (Simple)
- [ ] extras on the right bones (`extra_ten`!), `FLAG_EXTRAS_STRONG` if they shouldn't fall off
- [ ] liveries show and cycle; police job config lists the spawn name, extras and livery
- [ ] siren controller tones set for the model; lights/sound synced for a second player watching
