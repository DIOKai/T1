# Modelling a weapon for GTA V (Blender → Sollumz → ydr)

Contents: 1 Method · 2 Vanilla template · 3 Skeleton and tags · 4 Skinning and moving parts · 5 Magazines and attachments · 6 Base, `_hi`, LOD · 7 Collision · 8 Shaders, textures, tints · 9 Budgets · 10 Export and hot reload · 11 Re-skins (no new model) · 12 Unverified

Legend: (V) read from vanilla files with CodeWalker.Core (read-only, 2026-11-08); (video id [mm:ss]) see `sources.md`; (unverified).

## 1. Method (user rule + tutorials)

1. **Watch a tutorial of the same kind of gun first** (user lesson 2026-11-05). For a wooden-stock bolt rifle such as a Type 38, DIMENSION 3D `VLBiY_bG9d8` (M21 Winchester) is the closest; Creo Solus `oZT-m1Yqi9s` for the general gun method. CG Smoothie `TXw01CZ4MdU` is a cube-extrude low-poly method — the box approach the user rejected; use it only as a counter-example.
2. **References**: real side and front photos (or milling plans/blueprints for accuracy, Mindev `fN6TrRs2I7U` [56:16]). Scale all images to one known length (overall length or barrel) [VLBiY_bG9d8 00:45]; each reference visible only from its own view and unselectable [02:02]–[02:48].
3. **Blockout big shapes first** — receiver, barrel, stock, magazine/trigger guard (oZT-m1Yqi9s [04:49]–[05:31]); silhouette before detail (f-jUxzHr11Q [06:43]).
4. **Trace, don't box**: stock and grip by extruding along the side outline with axis lock [oZT-m1Yqi9s 06:15]; barrel as a 16-vertex cylinder [VLBiY_bG9d8 03:08]; Mirror on the width axis [04:04]; LoopTools (free, bundled extension) to round loops [05:11].
5. Holes (ejection port, bolt slot, sling swivels) with edge loops around them; **apply scale before bevel**, clamp overlap [VLBiY_bG9d8 08:33]; solidify/bevel last.
6. Part collections and names per piece; 2–6 materials (primary/secondary/accent) for previews [oZT-m1Yqi9s 17:28]–[20:00]. For GTA, bake down to one texture set (or a few) — §8.
7. Hard-surface techniques in general: `hard-surface` (its "Weapon Specifics": grip pivot at hand contact, sight line, moving parts separate) and `blender-product-modeling` for exact millimetre parts. Ask before using them and before running code through the `blender` MCP.

Paid tools seen in tutorials — 3ds Max + GIMS Evo (Desertos), Substance Painter, Marmoset Toolbag, Plasticity — are **(paid)**; free equivalents are Blender baking and texture painting.

## 2. Start from a vanilla template

- Export the closest vanilla weapon **and** its `_hi` and `_mag1` with CodeWalker (RPF Explorer → export XML), import in Sollumz (ook_3D `0lSk_4pWP0U` [00:21]–[01:22]; Anurag Verma `TBma7x7FlCI` [00:41]–[01:01]). The user's exporter `cw_export.ps1` (memory `gta-vanilla-export.md`) also works. Weapons live in `x64e.rpf\models\cdimages\weapons.rpf\` and DLC packs (e.g. musket in `update.rpf\dlc_patch\mpindependence\x64\models\cdimages\weapons.rpf`) (V).
- Line your mesh up with the vanilla mesh so grip, sight height and muzzle land where the animations expect (Desertos `2B1Dnb9LaiY` [06:57]–[07:47] "keep it at the same height"); apply transforms (Ctrl+A) before skinning [TBma7x7FlCI 02:51].
- Template choice (V, bone lists from the exported skeletons):

| Template | Bones worth knowing |
|---|---|
| `w_sr_heavysniper` | Gun_Trigger_Pr, Gun_Cock1 (bolt), Gun_VFX_Eject, Gun_Muzzle, WAPClip, WAPFlshLasr, WAPScop, NM_Butt_Marker, Gun_GripL |
| `w_sr_sniperrifle` | + Gun_Cock2, Gun_Safety, Gun_Hammer, WAPSupp |
| `w_ar_musket` | Gun_Cock1/2, Gun_Trigger_Pr, Gun_Feed (child of Gun_GripL) — **no WAP bones** |
| `w_sg_pumpshotgun` | Gun_Shell, Gun_Cock1 (pump), WAPFlshLasr, WAPSupp |
| `w_pi_pistol` | Gun_Hammer, Gun_Safety, Gun_Trigger_Pr |
| `w_sb_smg` | Gun_Cock2, Gun_Stock, WAPScop_2 |
| `w_ar_assaultrifle` | + WAPCover |
| `w_me_knife_01` | Gun_Root, Gun_GripR, Gun_Main_Bone only |

A Type 38 with a scope → heavy sniper skeleton (bolt + WAPScop + WAPClip). A musket skeleton cannot take a scope because it has no `WAPScop`.

## 3. Skeleton and tags (V, `w_ar_carbinerifle.ydr`; `_hi` identical)

| # | Bone | Tag | Parent |
|---|---|---|---|
| 0 | Gun_Root | 0 | — |
| 1 | Gun_GripR | 18308 | Gun_Root |
| 2 | Gun_Main_Bone | 3360 | Gun_GripR |
| 3 | Gun_Cock1 | 39439 | Gun_Main_Bone |
| 4 | Gun_Breach | 24367 | Gun_Cock1 |
| 5 | Gun_VFX_Eject | 28405 | Gun_Main_Bone |
| 6 | Gun_Muzzle | 17833 | Gun_Main_Bone |
| 7 | WAPFlshLasr | 4396 | Gun_Main_Bone |
| 8 | WAPSupp | 4230 | Gun_Main_Bone |
| 9 | WAPScop | 64805 | Gun_Main_Bone |
| 10 | WAPGrip | 19397 | Gun_Main_Bone |
| 11 | NM_Butt_Marker | 26613 | Gun_Main_Bone |
| 12 | Gun_Sight_front | 1830 | Gun_Main_Bone |
| 13 | Gun_Sight_rear | 31549 | Gun_Main_Bone |
| 14 | WAPClip | 1477 | Gun_Main_Bone |
| 15 | Gun_Trigger | 23712 | Gun_GripR |
| 16 | Gun_GripL | 18302 | Gun_Root |

Other tags: Gun_Trigger_Pr 56099, Gun_Hammer 24730, Gun_Safety 53712, Gun_Cock2 39440, Gun_Stock 5930, WAPScop_2 3634, WAPCover 27459, Gun_Feed 36598. Component roots: `AAPClip`, `AAPSupp` (+`Gun_SuMuzzle` 19851), `AAPFlsh` (+`Gun_FLMuzzle` 17662, `Bulb_Off` 54012, `Bulb_On` 37737), `AAPScop`, `AAPGrip` (V).

- Movable bones carry flags `RotX RotY RotZ TransX TransY TransZ` (+`Unk0` on Gun_Cock1) (V, XML).
- Orientation: barrel along +X, up +Z; muzzle ≈ 0.40 m (carbine), 0.83 m (musket), 0.12 m (pistol) from Gun_Root (V).
- Sollumz stores the imported tag in `bone_properties.tag` and writes it back on export (Sollumz source `ydr/ydrimport.py`, `ydr/ydrexport.py`). New bones need a tag typed by hand; how the game uses weapon bone tags is (unverified) — **keep the vanilla armature** so tags stay right.

## 4. Skinning and moving parts

- The top-level drawable object must be an armature; mesh children get vertex groups named exactly like bones (Sollumz docs "Rigging"). Delete the vanilla mesh, parent your mesh to the vanilla armature, add an **Armature modifier pointing at the weapon armature (not the mag's)** (ook_3D [02:24]–[04:53]).
- Trigger → `Gun_Trigger_Pr` (or `Gun_Trigger`), bolt/slide/charging handle → `Gun_Cock1`, everything that does not move → `Gun_Main_Bone` (or root) so every vertex has a weight (ook_3D [03:07]–[04:31]; Desertos [09:32]–[14:20]). Capitals matter [03:07].
- Keep **every** vanilla vertex group, even empty ones ("let it be empty but it needs to be there", TBma7x7FlCI [04:55]).
- Vertex layout of vanilla weapons: `Position, BlendWeights, BlendIndices, Normal, Colour0, TexCoord0, Tangent`, `HasSkin=1` (V).

## 5. Magazines and attachments

- Separate drawable with its own armature: one bone `AAPClip` and one vertex group `AAPClip` holding all vertices (ook_3D [06:19]; Desertos [17:16]); vanilla mags have exactly that one bone (V). Scopes/suppressors/grips likewise with `AAPScop` / `AAPSupp` / `AAPGrip`.
- Mag sits wrong in game → move the weapon's `WAPClip` bone, not the mag mesh (ook_3D [12:33]–[14:09]); muzzle flash wrong → move `Gun_Muzzle` (Desertos [17:59]–[18:42]).
- Naming: `w_sr_type38_mag1`, attachments `w_at_<short>_<part>` like vanilla `w_at_ar_supp`, `w_at_scope_medium` (V).
- A mag can share the weapon's texture dictionary through `txdName` in weaponarchetypes (Desertos [28:08]–[28:49]).

## 6. Base, `_hi`, LOD

- Vanilla: each weapon ydr has only `DrawableModelsHigh`; the detailed copy is the separate `<model>_hi.ydr` (V). Which situations draw `_hi` (close / first person) is (unverified); the pairing is (V).
- Build both from the same armature; if you move a bone (GripL, muzzle) move it **identically in both** (TBma7x7FlCI [08:38]–[11:37]).
- Real draw distance comes from `lodDist` in weaponarchetypes.meta (vanilla 50–500); the ydr's own LodDist is 9998 (V).
- Sollumz LOD slots are High/Medium/Low/Very Low; "Very High" is YFT-only (Sollumz docs, LOD editing). Put each weapon mesh in High of its own drawable.

## 7. Collision

Base ydr only, embedded `Composite` of 1–5 `Box` children (V): carbine 5 boxes `METAL_SOLID_SMALL`; mags/attachments 1–2 boxes `METAL_HOLLOW_SMALL`; musket `WOOD_SOLID_MEDIUM`; foregrip plastic. `_hi` has none. This is what a dropped weapon lands on (Desertos [11:55]; TBma7x7FlCI [01:22] "base model always has collisions"). For a wooden rifle use a wood material on the stock box.

## 8. Shaders, textures, tints (V)

| Use | Shader | Textures |
|---|---|---|
| Body with tints | `weapon_normal_spec_detail_palette` | diffuse, `_n`, `_s`, detail `ENV_SMOOTH_CONCRETE2`, palette `_Dpal` (128×32 A8R8G8B8) |
| Knife body | `weapon_normal_spec_palette` | |
| Decals (bucket 2) | `normal_spec_decal` | shared `W_AT_WeaponDecals*` |
| Mags, attachments | `normal_spec` (small pistol mag `spec`) | |
| Scope glass | `weapon_emissivestrong_alpha` + `weapon_normal_spec_alpha` (bucket 1) | |
| Flashlight bulb | `default` | |

- Plain `normal_spec` is fine when tints are not needed (ook_3D [07:23]–[07:44]; Desertos [20:13]–[21:18]).
- Tints: `SET_PED_WEAPON_TINT_INDEX` 0–7 picks a palette row through the `_palette` shader (`paletteSelector`); MK2 has its own list (citizenfx natives). MK2 camo skins are separate drawables (`w_ar_carbineriflemk2_camo1…`) (V).
- Sizes: rifle/SMG/pump body 2048² (DXT5 diffuse, DXT1 `_n`/`_s`) → ytd exactly 16 MiB; pistol 1024²; sniper 1024×512; mags 128×256; attachments 512×256 (V). DXT1 unless alpha, no 4K (Desertos [22:48]–[23:33]).
- Reflective parts: Sollumz Shader Tools "create shader" with a reflective GTA shader (Blacksite `YHJi0F1q_T8` [04:56]–[06:18]).

## 9. Triangle budget (V)

| Weapon | Base | `_hi` |
|---|---|---|
| w_pi_pistol | 798 | 3,575 |
| w_sb_microsmg | 1,020 | 4,960 |
| w_sr_heavysniper | 1,176 | 2,892 |
| w_sb_smg | 1,427 | 5,589 |
| w_sg_pumpshotgun | 1,579 | 3,802 |
| w_ar_assaultrifle | 1,738 | 4,925 |
| w_sr_sniperrifle | 2,262 | 6,162 |
| w_ar_carbinerifle | 2,965 | 9,165 |
| w_ar_musket | 4,031 | 4,923 |

Mags 38–344, attachments 202–744. The checker warns above base 6,000 / `_hi` 15,000 / part 1,500 (≈1.5× the vanilla maximum, a rule of thumb, not an engine limit). Desertos' 20k is far above vanilla.

## 10. Export and hot reload

- Textures: ook_3D embeds then un-embeds textures so Sollumz writes DDS next to the XML, then builds the ytd with "Folders to YTD" [07:44]–[09:27] (community tool, licence not checked). The user's own pipeline (CodeWalker / `build_ytd`, memory `gta-half-float-uvs.md`) works too; keep the ytd name = `txdName` and texture names = shader parameters.
- **Bone limits in Sollumz 2.9**: the 2022 video removes flags and adds "limit rotation / limit translation" by name (TBma7x7FlCI [12:19]–[13:27]). Current Sollumz derives `HAS_ROTATE_LIMITS` / `HAS_TRANSLATE_LIMITS` from **Limit Rotation / Limit Location pose-bone constraints** (source `get_bone_flags`); import creates them in LOCAL space. Edit the constraints, not flag names. (Inferred from source, not tested in Blender.)
- Sollumz has no weapon tutorial yet ("Creating Weapons [TODO]" in docs).
- Hot reload: remove the weapon from the ped, `restart <resource>`, flush streaming; ook_3D [14:29] says "str request flush" may need a Canary client (command name unverified). Reconnecting always works.

## 11. Re-skins without a new model

- Retexture a vanilla or add-on gun: export ydr XML + ytd, import XML in Sollumz, edit in Photopea (free) → DDS, assign to the existing GTA shader; the `_hi` needs the same textures (Dizzy `9jZWAlGoEbI` [05:00]–[11:47]).
- Light "wireframe" skins: start from `_hi` + ytd, delete decal geometry, tris → quads (Alt+J), decimate planar 43k → 28k, tiny 64 px solid texture (Dizzy `Hqgt0MDKZLI`).
- Animated UV skins need an extra model + clip dictionary + ytyp flag + ymap (Amply `z3omPQsi48I`); the uploader is unsure about several steps — (unverified), advanced.

## 12. Unverified / gaps

- No official Sollumz weapon workflow; the constraint-based bone limits are read from source code. Cheapest proof: import `w_ar_carbinerifle.ydr`, export unchanged, diff the XML.
- Whether new bones need specific tags; whether `_hi` is first-person-only.
- Five relevant videos have no captions (GTA PLUG weapon export `aUScfYp22Os`, Poly Bevel Glock, DIMENSION 3D M4A1) — not analysed.
