# Weapon meta files

Contents: 1 Names that must match · 2 weapons.meta (CWeaponInfo, carbine example) · 3 weaponarchetypes.meta · 4 weaponcomponents.meta · 5 weaponanimations.meta · 6 pedpersonality, loadouts, unlocks, shop · 7 Text label · 8 fxmanifest and data_file · 9 Resource template · 10 Add-on vs replacement · 11 Type 38 notes · 12 Unverified

(V) = read from vanilla `update.rpf\common\data\ai\weapons.meta`, `weaponcomponents.meta`, `weaponanimations.meta`, `update.rpf\common\data\weaponarchetypes.meta` and the mpindependence (musket) DLC, read-only 2026-11-08. Public add-on example: github.com/NoobySloth/Custom-Weapons `metas/m4/*`.

## 1. Names that must match

```
weapons.meta  <Name>WEAPON_TYPE38       → ox_inventory key, weaponanimations key, pedpersonality, give/spawn code
              <Model>w_sr_type38        → weaponarchetypes modelName → stream/w_sr_type38.ydr (+ _hi.ydr)
              <Slot>SLOT_TYPE38         → SlotNavigateOrder Entry (unique)
              <HumanNameHash>WT_TYPE38  → AddTextEntry('WT_TYPE38', 'Type 38 Rifle')
              AttachPoints <Name>COMPONENT_TYPE38_CLIP_01 → weaponcomponents <Name>
weaponcomponents <Model>w_sr_type38_mag1 → weaponarchetypes modelName → stream/w_sr_type38_mag1.ydr
weaponarchetypes <txdName>w_sr_type38   → stream/w_sr_type38.ytd
```
"Names must match across all meta files" (ImTrevorTbh, forum.cfx.re 2019). Comparisons in the game are hash-based (joaat), so case does not matter (vanilla writes `W_AR_CARBINERIFLE` in weapons.meta and `w_ar_carbinerifle` in archetypes) (V).

## 2. weapons.meta — `CWeaponInfoBlob`

```xml
<CWeaponInfoBlob>
  <SlotNavigateOrder><Item><WeaponSlots>
    <Item><OrderNumber value="481"/><Entry>SLOT_TYPE38</Entry></Item>
  </WeaponSlots></Item></SlotNavigateOrder>
  <SlotBestOrder>…</SlotBestOrder>          <!-- musket has it; the M4 example omits it -->
  <TintSpecValues/> <FiringPatternAliases/> <UpperBodyFixupExpressionData/> <AimingInfos/>
  <Infos><Item><Infos>
    <Item type="CWeaponInfo"> … </Item>
  </Infos></Item></Infos>
  <VehicleWeaponInfos/>
  <Name>Type 38</Name>
</CWeaponInfoBlob>
```
OrderNumber values may be anything unique; a reused number can push a weapon out of the inventory (2019 melee guide, forum.cfx.re/t/246436). gtamods wiki (Weapons.meta) describes four Infos groups: ammo, main weapons, vehicle weapons, environmental.

### Key CWeaponInfo fields (V, `WEAPON_CARBINERIFLE`)

| Group | Field = vanilla value | Meaning |
|---|---|---|
| identity | `Name` WEAPON_CARBINERIFLE | weapon hash = joaat(Name) |
| | `Model` W_AR_CARBINERIFLE | ydr name |
| | `Audio` AUDIO_ITEM_CARBINERIFLE | existing sound set (animation-effects-audio §3) |
| | `Slot` SLOT_CARBINERIFLE, `WheelSlot` WHEEL_RIFLE, `Group` GROUP_RIFLE | inventory slot, wheel segment, group |
| | `HumanNameHash` WT_RIFLE_CBN | text label key |
| | `PickupHash`, `MPPickupHash`, `StatName` | pickups, stats (copy, rename if unique) |
| damage | `DamageType` BULLET, `FireType` INSTANT_HIT, `Damage` 32.0 | base damage |
| | `HeadShotDamageModifierPlayer` 18.0, `Min/MaxHeadShotDistancePlayer` 5/40 | headshots |
| | `HitLimbsDamageModifier` 0.5, `NetworkHitLimbsDamageModifier` 0.8, `LightlyArmouredDamageModifier` 0.75 | limbs, armour |
| | `Force` 75, `ForceHitPed` 140, `Penetration` 0.1 | impact |
| range | `WeaponRange` 120, `LockOnRange` 65, `Speed` 2000 | |
| ammo | `AmmoInfo ref="AMMO_RIFLE"`, `ClipSize` 30 | the clip component's `ClipSize` overrides (2019 guide; CWeaponComponentClipInfo has its own ClipSize (V)) |
| fire rate | `TimeBetweenShots` 0.135 (musket 1.567), `BulletsInBatch` 1, `ReloadTimeMP/SP` -1, `AnimReloadRate` 1.0 | |
| accuracy | `AccuracySpread` 3.0, `RecoilAccuracyMax` 0.5, `RecoilErrorTime` 3.0, `RecoilRecoveryRate` 1.0 | |
| recoil | `RecoilShakeHash` ASSAULT_RIFLE_RECOIL_SHAKE, `RecoilShakeHashFirstPerson` FPS_ASSAULT_RIFLE_RECOIL_SHAKE, `RecoilShakeAmplitude` 0.333 | camera shake |
| camera | `DefaultCameraHash` DEFAULT_THIRD_PERSON_PED_AIM_CAMERA, `CameraFov` 35, `FirstPersonScopeFov`, `FirstPerson*Offset`, `AimOffset*`, `LeftHandIkOffset` | first-person placement lives here |
| reticule | `ReticuleStyleHash` WEAPONTYPE_RIFLE | |
| effects | `<Fx>`: `EffectGroup` WEAPON_EFFECT_GROUP_RIFLE_ASSAULT, `FlashFx` muz_assault_rifle, `FlashFxFP` muz_assault_rifle_fp, `MuzzleSmokeFx` muz_smoking_barrel, `ShellFx` eject_auto, `TracerFx` bullet_tracer, `TracerFxChanceSP/MP` 0.15/0.75, `FlashFxLight*`, `PedDamageHash` BulletLarge | |
| misc | `MovementModeConditionalIdle` MMI_2Handed, `NmShotTuningSet` Automatic, `TintSpecValues ref="TINT_DEFAULT"`, `FiringPatternAliases ref="FIRING_PATTERN_RIFLE"`, `AimingInfo ref="RIFLE_LO_BASE_STRAFE"` | |

AttachPoints (V, carbine):
```xml
<AttachPoints>
  <Item><AttachBone>WAPClip</AttachBone><Components>
    <Item><Name>COMPONENT_CARBINERIFLE_CLIP_01</Name><Default value="true" /></Item>
    <Item><Name>COMPONENT_CARBINERIFLE_CLIP_02</Name><Default value="false" /></Item>
  </Components></Item>
  <Item><AttachBone>WAPFlshLasr</AttachBone><Components><Item><Name>COMPONENT_AT_AR_FLSH</Name><Default value="false" /></Item></Components></Item>
  <Item><AttachBone>WAPScop</AttachBone><Components><Item><Name>COMPONENT_AT_SCOPE_MEDIUM</Name><Default value="false" /></Item></Components></Item>
  <Item><AttachBone>WAPSupp</AttachBone><Components><Item><Name>COMPONENT_AT_AR_SUPP</Name><Default value="false" /></Item></Components></Item>
  <Item><AttachBone>WAPGrip</AttachBone><Components><Item><Name>COMPONENT_AT_AR_AFGRIP</Name><Default value="false" /></Item></Components></Item>
  <Item><AttachBone>gun_root</AttachBone> … VARMOD_LUXE skins</Item>
  <Item><AttachBone>gun_gripr</AttachBone> … COMPONENT_GUNRUN_MK2_UPGRADE</Item>
</AttachPoints>
```
Vanilla attachments (scope, suppressor) can be listed on an add-on weapon by their vanilla names; the bone must exist in your skeleton.

`WeaponFlags` (V): carbine `CarriedInHand Automatic Gun CanLockonOnFoot CanLockonInVehicle CanFreeAim TwoHanded AnimReload AnimCrouchFire UsableOnFoot UsableInCover AllowEarlyExitFromFireAnimAfterBulletFired NoLeftHandIKWhenBlocked AllowCloseQuarterKills HasLowCoverReloads HasLowCoverSwaps LongWeapon UseFPSAimIK UseFPSSecondaryMotion FPSOnlyExitFireAnimAfterRecoilEnds`. The single-shot musket drops `Automatic` and adds `IgnoreAnimReloadRateModifiers PlayOutOfAmmoAnim AttachReloadObjectToRightHand BlockFirstPersonStateTransitionWhileFiring`.

Balancing for RP: edit `Damage` and `HeadShotDamageModifierPlayer` in a streamed weapons.meta (JSP Coding `Xrj_y_lzq9g` [02:02]–[03:23]); numbers for an economy belong to `game-balance-economy`, and the client can still lie — server checks in `framework-and-server.md`.

## 3. weaponarchetypes.meta — `CWeaponModelInfo__InitDataList` (V)

```xml
<CWeaponModelInfo__InitDataList><InitDatas>
  <Item><modelName>w_sr_type38</modelName><txdName>w_sr_type38</txdName><ptfxAssetName>NULL</ptfxAssetName><lodDist value="500"/></Item>
  <Item><modelName>w_sr_type38_mag1</modelName><txdName>w_sr_type38</txdName><ptfxAssetName>NULL</ptfxAssetName><lodDist value="300"/></Item>
</InitDatas></CWeaponModelInfo__InitDataList>
```
Every streamed weapon, mag and attachment ydr needs an entry; a crash on reload was fixed by adding the magazine (2019 thread 293807). Vanilla musket: `ptfxAssetName` wpn_musket, `lodDist` 50; vanilla range 50–500. The `_hi` model has no own entry (V).

## 4. weaponcomponents.meta — `CWeaponComponentInfoBlob`

Vanilla base file wraps items in `<Data>`; DLC files and add-ons use `<Infos>` + `<InfoBlobName/>` (V, mpindependence; NoobySloth). Use `<Infos>` for add-ons.

Types in the base file (V): CWeaponComponentClipInfo 42, CWeaponComponentVariantModelInfo 45 (finishes; `TintIndexOverride`, `ExtraComponents`), CWeaponComponentScopeInfo 7, CWeaponComponentSuppressorInfo 5, CWeaponComponentFlashLightInfo 3, CWeaponComponentInfo 3 (grips), CWeaponComponentReloadData 8, CWeaponSwapData 2.

```xml
<CWeaponComponentInfoBlob><Infos>
  <Item type="CWeaponComponentClipInfo">
    <Name>COMPONENT_TYPE38_CLIP_01</Name>
    <Model>w_sr_type38_mag1</Model>            <!-- empty Model = nothing drawn -->
    <LocName>WCT_CLIP1</LocName><LocDesc>WCD_CLIP1</LocDesc>
    <AttachBone>AAPClip</AttachBone>          <!-- the component's own root bone -->
    <WeaponAttachBone>WAPClip</WeaponAttachBone>   <!-- add-on example writes it; vanilla omits -->
    <AccuracyModifier type="NULL"/><DamageModifier type="NULL"/>
    <bShownOnWheel value="false"/><CreateObject value="true"/>
    <HudDamage value="0"/><HudSpeed value="0"/><HudCapacity value="0"/><HudAccuracy value="0"/><HudRange value="0"/>
    <ClipSize value="5"/>
    <ReloadData ref="RELOAD_DEFAULT"/>
  </Item>
</Infos><InfoBlobName/></CWeaponComponentInfoBlob>
```
Scope (V, `COMPONENT_AT_SCOPE_MEDIUM`): `CWeaponComponentScopeInfo`, `AttachBone` AAPScop, `bShownOnWheel` true, `CameraHash` (empty; the large scope uses SNIPER_LOW_ZOOM_AIM_CAMERA), `RecoilShakeAmplitude` 0.28, `ExtraZoomFactorForAccurateMode` 1.2, `Reticule`/`ReticuleHash` (large: SNIPER_LARGE).
Suppressor (V, `COMPONENT_AT_AR_SUPP`): `CWeaponComponentSuppressorInfo`, AAPSupp, `DamageModifier type="CWeaponDamageModifier"` 1.0, `MuzzleBone` Gun_SuMuzzle, `FlashFx` muz_pistol_silencer, Hud deltas −5.

Component pool: a 2019 report said ~6–7 add-on components broke things and a later update raised the pool (current limit unverified).

## 5. weaponanimations.meta — `CWeaponAnimationsSets`

`WeaponAnimationsSets/Item key=` Ballistic, Default, Franklin, Gang, Michael, MP_F_Freemode, Trevor, FirstPerson, FirstPersonAiming, Fat, SuperFat, Female, GangFemale, ZOMBIE (V, base file),, each with `<Fallback>` and `<WeaponAnimations><Item key="WEAPON_X">` holding `MotionClipSetHash`, `WeaponClipSetHash`, `WeaponClipSetStreamedHash`, `WeaponClipSetHashStealth`, `CoverWeaponClipSetHash`, `MeleeClipSetHash`, `AnimFireRateModifier`, `WeaponSwapClipSetHash`… (V).

Vanilla clipsets (V): carbine `weapons@rifle@lo@carbine`; heavy sniper `weapons@rifle@lo@sniper_heavy` (cover `Cover_Wpn_RifleSniperHeavy`); sniper rifle `weapons@rifle@hi@sniper_rifle`; Ballistic set uses `move_ballistic_2h`; FirstPerson uses `weapons@first_person@aim_rng@generic@…`. Musket clipsets are in its DLC file (not read).

Practice: copy every `<Item key="WEAPON_TEMPLATE">` block of the template under each set and rename the key (2019 guide; vWeaponsToolkit generates it). Missing entry = wrong or no holding animation.

## 6. pedpersonality, loadouts, unlocks, shop

- `CPedModelInfo__PersonalityDataList/MovementModeUnholsterData/Item Name=UNHOLSTER_UNARMED|UNHOLSTER_2H_MELEE|UNHOLSTER_1H|UNHOLSTER_2H|…` → `UnholsterClips/Item/Weapons/Item WEAPON_X` + `Clip` (`unarmed_holster_2h`, `2h_melee_holster_2h`, `1h_holster_2h` …) (NoobySloth M4). Groups: unarmed (melee/bombs), 1h (pistols, small SMGs), 2h (everything else), minigun (2019 guide).
- `loadouts.meta` (`LOADOUTS_FILE`) exists in base and DLC (V). Item-based servers give weapons by script, so it is optional.
- `contentunlocks.meta` / `shop_weapon.meta` — GTAO unlocks/shop; optional (some public resources ship contentunlocks).

## 7. Text label

```lua
-- client/names.lua
AddTextEntry('WT_TYPE38', 'Type 38 Rifle')   -- key = HumanNameHash
```
`ADD_TEXT_ENTRY` is a client CFX native. Without it the wheel shows NULL.

## 8. fxmanifest and data_file

docs.fivem.net "Data Files": `WEAPONINFO_FILE` (+`WEAPONINFO_FILE_PATCH`) = weapons.meta, `WEAPON_METADATA_FILE` = weaponarchetypes, `WEAPON_ANIMATIONS_FILE`, `WEAPONCOMPONENTSINFO_FILE`, `LOADOUTS_FILE`, `PED_PERSONALITY_FILE`, `CONTENT_UNLOCKING_META_FILE`, `WEAPON_SHOP_INFO_METADATA_FILE`, `DLC_WEAPON_PICKUPS`, `CLIP_SETS_FILE`, `PTFXASSETINFO_FILE`, audio `AUDIO_GAMEDATA` / `AUDIO_SOUNDDATA` / `AUDIO_WAVEPACK`. Globs work; every data file must also be in `files {}` (resource-manifest docs).

Order: components first, weapons.meta last (ImTrevorTbh 2019, "otherwise some things will not work"); the public manifests checked (SOZ pickaxe, ProLaser4, NoobySloth) all list `WEAPONINFO_FILE` last.

```lua
fx_version 'cerulean'
game 'gta5'

files { 'meta/*.meta' }

data_file 'WEAPONCOMPONENTSINFO_FILE' 'meta/weaponcomponents.meta'
data_file 'WEAPON_METADATA_FILE'      'meta/weaponarchetypes.meta'
data_file 'WEAPON_ANIMATIONS_FILE'    'meta/weaponanimations.meta'
data_file 'PED_PERSONALITY_FILE'      'meta/pedpersonality.meta'
data_file 'WEAPONINFO_FILE'           'meta/weapons.meta'   -- last

client_script 'client/names.lua'
```
Public packs often start XML with `encoding="UTF - 8"`; the game accepts it, strict parsers do not (the checker tolerates it).

## 9. Resource template

```
resources/[weapons]/w_type38/          -- new category: own `ensure [weapons]`, name unique server-wide
  fxmanifest.lua
  client/names.lua
  meta/weaponcomponents.meta  weaponarchetypes.meta  weaponanimations.meta  pedpersonality.meta  weapons.meta
  stream/
    w_sr_type38.ydr        base, 1–4k tris, box collision
    w_sr_type38_hi.ydr     detailed, 3–10k tris, no collision
    w_sr_type38.ytd        txdName
    w_sr_type38_mag1.ydr   clip/charger (can use txd w_sr_type38)
```
Source files (.blend, .xml, .dds) stay outside `stream/`.

## 10. Add-on vs replacement

- **Replacement**: stream files with the vanilla names (`w_pi_combatpistol.ydr`, `_hi.ydr`, `.ytd`, `_mag1…`), no metas; keep the `_hi` and `+hi` names (TaterTot `5m-wn-zD-bg` [02:13]–[03:36]). Changes that gun for every player.
- **Add-on**: rename every file to a new model name (keep `w_xx_`, `_hi`, `_mag1`, `+hi` patterns), new `WEAPON_X`, `SLOT_X`, `COMPONENT_X_CLIP_01`, `HumanNameHash` (TaterTot [03:16]–[05:42]).
- **Meta-only re-tune**: a streamed weapons.meta entry with a vanilla `Name` overrides that weapon's stats (JSP Coding [01:22]).
- Single-player packs in `dlc.rpf`: open with OpenIV (free) or CodeWalker, copy metas to `meta/` and ydr/ytd to `stream/` (Kamaryn `-iYB4CQIwvc` [02:08]–[02:53]).
- vWeaponsToolkit (github.com/rubbertoe98/vWeaponsToolkit) generates all metas from a template weapon; closed-source exe, no licence, ook_3D recommends v1.0.3 (later builds broken per uploader). **Ask the user before downloading or running it.** Copying vanilla entries by hand (this file) needs no tool.

## 11. Type 38 notes (judgement, test in game)

- Skeleton: `w_sr_heavysniper` (bolt `Gun_Cock1`, `WAPScop`, `WAPClip`). The musket skeleton has no WAP bones, so no scope.
- Stats: start from the heavy sniper or musket entry; single shot → no `Automatic` flag; `ClipSize` 5 on the clip component; a rifle `AmmoInfo` (the musket uses `AMMO_SHOTGUN`).
- Animation: no vanilla 5-round iron-sight bolt rifle exists; try the heavy sniper clipsets first (bolt cycle), compare with the musket set in game.
- Scope: vanilla `COMPONENT_AT_SCOPE_MEDIUM` / `_LARGE` on `WAPScop`, or a self-made `w_at_type38_scope` (`AAPScop` root, `CWeaponComponentScopeInfo`).

## 12. Unverified

- Load order effect (only 2019 community advice).
- Component pool size today.
- What `WeaponAttachBone` in add-on component entries changes (vanilla does not write it).
