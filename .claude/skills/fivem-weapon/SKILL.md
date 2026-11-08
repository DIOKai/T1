---
name: fivem-weapon
description: Use when making, converting, installing or debugging a GTA V / FiveM weapon — modelling a gun in Blender for GTA (w_*.ydr, _hi.ydr, .ytd, Gun_Root, WAP and AAP bones), Sollumz export, weapons.meta, weaponcomponents, weaponarchetypes, weaponanimations, pedpersonality, fxmanifest data_file, attachments (magazine, scope, suppressor, flashlight, grip), tints, replacement vs add-on packs, ox_inventory / Qbox / QBCore weapon items, or a gun that is invisible in hand, floats, sits offset, does no damage, crashes on reload or is missing from the weapon wheel. Also 自制武器, 加枪, 武器模组, 枪械建模, 配件, 瞄准镜, 消音器, weapons.meta, 武器没伤害, 枪不显示, 三八式.
---

# FiveM weapons (add-on and replacement)

A GTA weapon is a skinned drawable on a fixed bone set plus five metas that must agree on every name. Most "invisible / floating / no damage" bugs are name or bone mismatches, so work from vanilla templates and run the checker. (V) = read from vanilla files.

## Pick the route

| Goal | Route | What ships |
|---|---|---|
| Change stats of a vanilla gun | meta-only re-tune | edited `CWeaponInfo` in a `WEAPONINFO_FILE`, no models |
| New look for a vanilla gun | replacement | same file names as vanilla (`w_pi_pistol.ydr`, `_hi.ydr`, `.ytd`, `_mag1…`); changes it for everyone |
| A new gun next to vanilla | add-on | new names everywhere + metas + framework item |

Downloaded packs: licence gate first, then treat as add-on or replacement.

## Gates (user rules)

- **Free tools only** (Blender + Sollumz, CodeWalker, OpenIV, Photopea); paid ones are marked "(paid)" and not recommended. vWeaponsToolkit is an unlicensed closed-source exe: ask before downloading or running it.
- **Before modelling**: study a YouTube tutorial of the same kind of gun, trace real side/front photos (silhouette → curves → edge-loop holes → bevel last). Never build from boxes — the Type 38 was rejected for that.
- **Licensing**: packs ripped from other games must not be redistributed or sold (Cfx.re, Oct 2023); real brand logos become GTA names.
- **Server authority**: only the server inventory gives weapons and ammo; damage is checked server-side (`fivem-security` `rules/net-game-events.md`).
- Ask before using related skills: `blender-product-modeling` / `hard-surface`, the `blender` MCP, `fivem-animation`, `ox-inventory`, `fivem-security`, `qbox-economy-integrity`, `qbox-lua-check`.

## Order of work

1. Route, framework (user's server: Qbox + ox_inventory 2.48), licence.
2. Export the closest **vanilla template** (+ `_hi`, `_mag1`) with CodeWalker, import in Blender (`references/modelling-and-export.md`).
3. Model over it from references; keep grip, sights and muzzle where the template has them.
4. Skin to the **template armature** (vertex groups = bone names); mags/attachments are separate drawables.
5. Base `w_x.ydr` (collision boxes) + `w_x_hi.ydr`; external `w_x.ytd`.
6. Copy the template's meta entries and rename (`references/meta-files.md`).
7. fxmanifest, framework item (`references/framework-and-server.md`).
8. Run the checker, then the in-game test list (`references/troubleshooting.md`).

## Which vanilla template (V)

| Gun | Template | Notes |
|---|---|---|
| Pistol | `w_pi_pistol` | Gun_Hammer, Gun_Safety, Gun_Trigger_Pr |
| SMG | `w_sb_smg` | Gun_Cock2, Gun_Stock, WAPScop_2 |
| AR / carbine | `w_ar_carbinerifle`, `w_ar_assaultrifle` | full WAP set |
| Pump shotgun | `w_sg_pumpshotgun` | Gun_Shell; WAPFlshLasr, WAPSupp only |
| Bolt-action with scope | `w_sr_heavysniper` | Gun_Cock1 bolt, WAPClip, WAPScop, WAPFlshLasr |
| Single-shot / musket | `w_ar_musket` | **no WAP bones** → no attachments |
| Melee | `w_me_knife_01` | Gun_Root, Gun_GripR, Gun_Main_Bone only |

## Skeleton (V, `w_ar_carbinerifle`)

| Bone (tag) | Parent | Job |
|---|---|---|
| Gun_Root (0) | — | root |
| Gun_GripR (18308) | Root | right hand, held here |
| Gun_Main_Bone (3360) | GripR | all non-moving parts |
| Gun_Cock1 (39439) → Gun_Breach | Main | bolt / charging handle |
| Gun_Muzzle (17833), Gun_VFX_Eject (28405) | Main | flash + bullet origin, shells |
| WAPClip, WAPScop, WAPSupp, WAPGrip, WAPFlshLasr | Main | attach points |
| Gun_Trigger (23712) | GripR | trigger |
| Gun_GripL (18302) | Root | left-hand IK |

Components have one root `AAPClip` / `AAPScop` / `AAPSupp` / `AAPGrip` / `AAPFlsh`. weapons.meta AttachPoints name the **WAP** bone, weaponcomponents.meta the **AAP** bone. +X forward, +Z up. Full table with tags: modelling reference §3.

## File facts (V)

- **No .ytyp**: archetypes live in `weaponarchetypes.meta`; every weapon, mag and attachment ydr needs an entry.
- External `.ytd` named by `txdName` (no vanilla weapon embeds textures).
- `w_x.ydr` + detailed `w_x_hi.ydr`, one LOD each; only `_hi` streamed = invisible.
- 1–5 `Box` collisions in the **base** ydr only. `+hi.ytd` is optional (some DLC guns).

## Budgets and shaders (V, rule of thumb)

| Part | Vanilla tris | Aim |
|---|---|---|
| Base ydr | 798–4,031 | 1–4k |
| `_hi.ydr` | 2,892–9,165 | 3–10k |
| Mag / attachment | 38–744 | < 800 |

Textures: rifles 2048² (ytd 16 MiB), pistol 1024²; DXT1, DXT5 only with alpha. Body shader `weapon_normal_spec_detail_palette` (tints via `_Dpal`); `normal_spec` if no tints; scope glass `weapon_emissivestrong_alpha`.

## Manifest

`data_file` order: `WEAPONCOMPONENTSINFO_FILE`, `WEAPON_METADATA_FILE`, `WEAPON_ANIMATIONS_FILE`, `PED_PERSONALITY_FILE`, then `WEAPONINFO_FILE` **last** (2019 community advice); every meta also in `files {}`. Name: `AddTextEntry('<HumanNameHash>', 'Label')` client-side. New `[weapons]` category needs its own `ensure` and a unique name.

## Framework

- **ox_inventory** (`data/weapons.lua`): item key (or `model`) = weapons.meta `Name`; `hash = joaat(model)`. Equip uses `GiveWeaponToPed` + `DoesWeaponTakeWeaponComponent`, so a component must be in the weapon's AttachPoints **and** in an ox Components `client.component` list. Image `web/images/<ITEM>.png`.
- **Qbox**: `qbx_core/shared/weapons.lua` is deprecated; ox_inventory is the source of truth. QBCore lists: framework reference §2.

## Checks

```
py -3 -I scripts/check_weapon_resource.py <resource> [--ox <ox_inventory>] [--xml <export folder>]
```
Read-only, exit 1 on errors: manifest types/globs/`files`, meta roots, Model → archetype → ydr → ytd, `_hi` without base, components, AttachBone prefixes, slots, AddTextEntry, animations, RSC7 size; `--xml` adds bones, bounds, triangles; `--ox` the item, ammo, image, components.

## Common mistakes

| Symptom | Cause → fix |
|---|---|
| In inventory, invisible in hand | ox key ≠ `Name`; meta not loaded (typo type, not in `files`); Model ≠ archetype ≠ ydr name; only `_hi` streamed |
| Floating / offset in hand | not aligned to the template; transforms not applied |
| Parts don't move / whole gun moves | vertex group names ≠ bone names; Armature modifier missing or on the mag |
| Muzzle flash wrong place | move `Gun_Muzzle`, not the mesh |
| Mag floats or jitters | move `WAPClip`, set limit constraints, export both armatures |
| Scope will not attach | no `WAPScop` bone (musket template) or not in ox components |
| Crash on reload | mag model missing from weaponarchetypes |
| Not in wheel / name NULL | Slot not in SlotNavigateOrder, duplicate OrderNumber, no AddTextEntry |
| Purple textures | `txdName` ≠ ytd name |

## References (`references/`)

- `modelling-and-export.md` — Blender + Sollumz, skinning, components, `_hi`, collision, shaders, re-skins.
- `meta-files.md` — CWeaponInfo (carbine), archetypes, components, animations, manifest, Type 38.
- `framework-and-server.md` — ox_inventory, Qbox, QBCore, natives, anti-exploit.
- `animation-effects-audio.md` — clipsets, ptfx, audio (partly unverified).
- `troubleshooting.md` — symptoms, in-game test list. `sources.md` — videos, web.
