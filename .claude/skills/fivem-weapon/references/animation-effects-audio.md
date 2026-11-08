# Animation, effects and audio

## 1. Holding, aiming, reload

- Every pose comes from clipsets named in `weaponanimations.meta` for the weapon's `Name` (meta-files §5). Pick the template whose handling matches (pistol 1h, rifle 2h, bolt rifle, shotgun pump) and copy its entries; to change a pose, point the entry at another vanilla clipset (V names: `weapons@rifle@lo@carbine`, `weapons@rifle@lo@sniper_heavy`, `weapons@rifle@hi@sniper_rifle`, Ballistic `move_ballistic_2h`).
- Brand-new clips need a `.ycd`, a clip dictionary and a `CLIP_SETS_FILE` with your clipset (unverified for weapons — no tested recipe found). Making ycd files: `fivem-animation` (ask first).
- Third-party "weapon animation packs" exist (bozoteko `7zqjwPxOuBo`); they replace vanilla clipsets for everyone — check licence and test first person.
- Unholster clip: `pedpersonality.meta` (meta-files §6).
- First-person placement: `FirstPerson*Offset` fields in `CWeaponInfo`; iron-sight alignment depends on the model matching the template's sight height (modelling §2).
- Moving parts animate through bones: trigger (`Gun_Trigger` / `Gun_Trigger_Pr`), bolt/slide (`Gun_Cock1`, `Gun_Cock2`), hammer, safety, pump (`Gun_Cock1` on the pump shotgun) — the vertex groups decide what moves (ook_3D [01:42]–[02:24]; Anurag Verma `TBma7x7FlCI`). A bolt rifle's bolt motion comes from the template's clips driving `Gun_Cock1` (expected from the vanilla heavy sniper, verify in game).
- Reload speed: `AnimReloadRate`; single-shot flags (`PlayOutOfAmmoAnim`, `AttachReloadObjectToRightHand`) from the musket entry (V).

## 2. Effects (V field names)

| Effect | Where |
|---|---|
| Muzzle flash | `Fx/FlashFx` (+`FlashFxFP` first person, `FlashFxAlt`), spawned at `Gun_Muzzle` |
| Muzzle light | `FlashFxLightEnabled`, `FlashFxLightRGBAMin/Max`, `IntensityMinMax`, `RangeMinMax` |
| Smoke | `MuzzleSmokeFx` (+FP), `MuzzleSmokeFxMinLevel`, `IncPerShot`, `DecPerSec` |
| Shells | `ShellFx` / `ShellFxFP` at `Gun_VFX_Eject` |
| Tracers | `TracerFx`, `TracerFxChanceSP/MP` |
| Suppressed | component `MuzzleBone` `Gun_SuMuzzle` + its own `FlashFx` (`muz_pistol_silencer`) |
| Impact group | `EffectGroup` (e.g. `WEAPON_EFFECT_GROUP_RIFLE_ASSAULT`), `PedDamageHash` |

Custom particle assets: `ptfxAssetName` in weaponarchetypes (musket `wpn_musket`) + a `PTFXASSETINFO_FILE` — (unverified) for add-ons; reuse vanilla effect names.

## 3. Audio

- `<Audio>AUDIO_ITEM_*</Audio>` reuses a vanilla weapon sound set; pick one with the same fire mode — the Qbox weapon-audio docs warn that single-fire sounds on automatic weapons sound wrong (docs.qbox.re/tebex/weapon-audio; the product itself is **(paid)**). For a bolt rifle try `AUDIO_ITEM_HEAVYSNIPER` / `AUDIO_ITEM_SNIPERRIFLE` / `AUDIO_ITEM_MUSKET` (names follow the vanilla pattern; confirm in game).
- New sounds need a dat151 game-data item (`AUDIO_GAMEDATA`), dat54 sounds (`AUDIO_SOUNDDATA`) and an `AUDIO_WAVEPACK`; citizenfx/fivem issue #2496 reports FiveM is picky about dat151 and can crash — **no verified recipe**. Package checks: `fivem-audio-package-check`; the vehicle-sound workflow (`fivem-vehicle-sound`) is the closest documented pattern. Ask before using either.
- Sound packs ripped from other games fall under the same licensing rule as models.

## 4. Unverified

- Custom ycd clipsets for weapons, custom weapon ptfx assets, custom dat151 weapon audio — all untested here.
- Which vanilla clipset gives the best Type 38 bolt cycle (heavy sniper vs musket vs marksman) — test in game.
