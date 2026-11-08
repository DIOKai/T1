# Sources

Studied 2026-11-08. Video facts come from the original-language English captions (`en-orig`); notes are original summaries. Watch URL: `https://www.youtube.com/watch?v=<id>`.

## Vanilla and local evidence (read-only)

- GTA V at `G:\SteamLibrary\steamapps\common\Grand Theft Auto V`, read with CodeWalker.Core (`CodeWalker30_dev46`): `x64e.rpf\models\cdimages\weapons.rpf` (carbine, assault rifle, pistol, SMG, micro SMG, pump shotgun, sniper rifle, heavy sniper, knife, mags, `w_at_ar_supp/flsh/afgrip`, `w_at_scope_medium`), `update.rpf\dlc_patch\mpindependence` (musket), `update.rpf\common\data\ai\weapons.meta`, `weaponcomponents.meta`, `weaponanimations.meta`, `loadouts.meta`, `update.rpf\common\data\weaponarchetypes.meta`, mpbusiness `weaponspecialcarbine.meta`. Skeletons, tags, triangle counts, shaders (names recovered by joaat lookup), collision boxes, texture sizes and RSC7 headers (ydr version 165, ytd 13) come from these.
- The user's server (read-only): ox_inventory 2.48.0 `data/weapons.lua`, `modules/items/shared.lua`, `modules/weapon/client.lua`; qbx_core `shared/weapons.lua` (deprecation header). Escrow-encrypted files on the server start with `FXAP`.

## Web

- FiveM docs, Data Files: https://docs.fivem.net/docs/game-references/data-files/
- FiveM docs, Resource manifest (`files`, `data_file`, globbing): https://docs.fivem.net/docs/scripting-reference/resource-manifest/
- Sollumz docs, Rigging (armature + vertex groups named like bones): https://docs.sollumz.org/documentation/drawables.ydr/rigging.md
- Sollumz docs, LOD editing (Very High is YFT-only): https://docs.sollumz.org/documentation/drawables.ydr/level-of-detail-lods-editing.md
- Sollumz docs, "Creating Weapons [TODO]": https://docs.sollumz.org/tutorials/creating-weapons-todo.md
- Sollumz source (master, read 2026-11-08): `ydr/ydrimport.py`, `ydr/ydrexport.py` (`create_bone`, `get_bone_flags`, bone tag round-trip, limit constraints): https://github.com/Sollumz/Sollumz
- gtamods wiki, Weapons.meta (edited 6 Jan 2022): https://gtamods.com/wiki/Weapons.meta
- ImTrevorTbh, "How to stream add-on weapons" (2019, load order, names must match, HD-only cannot be streamed, mag archetype crash, CWeaponManager crash on reconnect, component pool): https://forum.cfx.re/t/how-to-stream-add-on-weapons/293807
- Add-on melee guide (2019, OrderNumber collisions, +hi.ytd): https://forum.cfx.re/t/246436
- Weapon wheel icons / weapon missing after reconnect (2020–2021): https://forum.cfx.re/t/1309791
- Damage not applying (artifact report): https://forum.cfx.re/t/2603053
- Streaming size tiers (unofficial): https://forum.cfx.re/t/1689728
- Cfx.re "Community Pulse – October 2023" (no third-party IP, no assets combined from other games): https://forum.cfx.re/t/5176467
- citizenfx natives (`WEAPON/SetPedWeaponTintIndex.md`, GiveWeaponToPed, SetWeaponDamageModifier…): https://github.com/citizenfx/natives
- citizenfx/fivem `ext/natives/rpc_spec_natives.lua` (server RPC weapon natives) and `ext/native-decls` (GET_SELECTED_PED_WEAPON): https://github.com/citizenfx/fivem
- citizenfx/fivem issue #2496 (dat151 audio crashes): https://github.com/citizenfx/fivem/issues/2496
- ox_inventory `data/weapons.lua` upstream: https://raw.githubusercontent.com/overextended/ox_inventory/main/data/weapons.lua
- qb-core `shared/items.lua`, `shared/weapons.lua`; qb-weapons `config.lua`: https://github.com/qbcore-framework
- Qbox weapon-audio docs (product **(paid)**): https://docs.qbox.re/tebex/weapon-audio
- Public add-on example metas: https://github.com/NoobySloth/Custom-Weapons (`metas/m4/*`); manifests of SOZ pickaxe (`SOZ-Faut-etre-Sub/SOZ-FiveM-Server`, `resources/[weapon]/soz-weapon-pickaxe`) and TrevorBarns/ProLaser4.
- vWeaponsToolkit (closed-source exe, no licence, v1.0–1.0.5, last push 2023-12-15): https://github.com/rubbertoe98/vWeaponsToolkit

## Videos — GTA / FiveM pipeline

| id | Title — channel (length, date) | Used for |
|---|---|---|
| 0lSk_4pWP0U | [UPDATED] How To Create Add-On Weapons FiveM / GTA V — ook_3D (15:19, 2023-10) | template export [00:21], align [01:02], vertex groups = bones [01:42]–[04:31], Armature modifier [04:53], mag AAPClip [06:19], normal_spec [07:23], Folders to YTD [08:46], vWeaponsToolkit 1.0.3 [09:48], WAPClip fix [12:33], reload [14:29] |
| TBma7x7FlCI | Create custom animated weapons using Sollumz Blender — Anurag Verma (18:09, 2022-07) | base + _hi [00:41], base has collision [01:22], keep empty vertex groups [04:55], move bones in both [10:26], limit flags [12:19], first-person muzzle [16:43] |
| 2B1Dnb9LaiY | Addon weapon – How to add any weapon to FiveM — Desertos (44:35, 2023-11; 3ds Max **(paid)**) | template [01:03], sight height [06:57], skinning [09:12], mag [17:16], muzzle bone [17:59], DXT [22:48], shared txd [28:08], AttachPoints [31:18], `_hi` / `+hi.ytd` [33:26] (his "+hi required" is contradicted by vanilla) |
| 5m-wn-zD-bg | Adding addon weapons to FiveM Server — TaterTot (18:08, 2022-05) | replacement vs add-on naming [02:13]–[05:42], toolkit fields [04:41], clips [07:45], QBCore [11:58] |
| -iYB4CQIwvc | QBCore – How to Install Add-on Weapons — Kamaryn (14:48, 2024-05) | folder layout [00:24], dlc.rpf [02:08], every QBCore list [03:34]–[11:50] |
| 8gV077l0qPk | Custom Weapons with Ox Inventory — Kamaryn (5:15, 2025-02) | ox entry [00:22], components list [01:48], image [03:01] |
| p33vuz4FZYQ | How To Add Custom Weapons to Ox Inventory – QBCore — QbDork (21:10, 2025-09) | free vs escrow packs, images [07:50], image name [16:18] |
| vPFcvAx9BU0 | Add Custom Guns and Ammo Using ox_inventory — Zeroskyrim Productions (6:40) | Name into ox [01:06], ammo type ≠ damage [02:11], ammo item [03:04] |
| lujygaTTOI8 | Install ANY Custom Weapon in FiveM — FiveDevTechGaming (8:31) | typical pack layout [01:24]–[04:51] (licence unknown) |
| BJDGewBykCc | How to install custom guns for free — HighwayTrooper (5:55, 2022) | category folder + ensure [01:03], vMenu list [02:50] |
| 64tDogV3GW8 | How To Add Custom Weapons To Your QBcore — Bizarre Tutorials (3:45) | replacement, slow first draw [03:10] |
| Xrj_y_lzq9g | FiveM Basics – Vehicle and Guns Metas — JSP Coding (11:36) | meta-only re-tune [01:22], damage balancing [02:02] |
| 7zqjwPxOuBo | How to get Custom Gun Animations — bozoteko (1:46) | animation packs (no detail) |
| 9jZWAlGoEbI | How to Make a Custom Weapon Skin — Dizzy (17:12, 2024-06) | retexture route [05:00]–[11:47] |
| Hqgt0MDKZLI | Wireframe Weapon Skins — Dizzy (15:16, 2026-01) | optimisation steps [01:31]–[09:34] |
| YHJi0F1q_T8 | How To Create Reflective Guns — Blacksite Tutorials (10:49) | Sollumz Shader Tools [04:56] |
| z3omPQsi48I | How To Create Animated Weapon Skins — Amply (12:12) | UV-animated skins [01:03]–[11:04] (unverified) |

## Videos — Blender modelling method

| id | Title — channel (length, date) | Used for |
|---|---|---|
| oZT-m1Yqi9s | How to Model Any Gun in Blender – Overview — Creo Solus (23:06, 2023-06) | references [01:42], blockout [04:49], outline extrude [06:15], subsurf [08:02], naming [17:28], materials [18:54] |
| VLBiY_bG9d8 | M21 Winchester Rifle 3D Modeling – Part 1 — DIMENSION 3D (1:21:00, 2026-08) | wooden-stock rifle method: scale refs [00:45], ref visibility [02:02], barrel [03:08], mirror [04:04], LoopTools [05:11], stock [06:34], bevel [08:33]; part 2 uses Substance **(paid)** |
| fN6TrRs2I7U | Game Ready Weapon Tutorial pt1 — Mindev (1:00:13, 2023-07) | pipeline [00:22] (Marmoset, Substance **(paid)**), reference planes [01:03], milling plans [56:16] |
| f-jUxzHr11Q | Game Ready WEAPON Tutorial — Artof JoseVega (18:06, 2025-12; Plasticity **(paid)**) | silhouette first [06:43] |
| TXw01CZ4MdU | Low Poly Gun from Reference — CG Smoothie (11:52, 2020-07) | counter-example only (box method) |

No captions, not analysed: `aUScfYp22Os` (GTA PLUG, export GTA V guns to Blender), `8KGtETzhbQQ` (Poly Bevel, Glock 17), `NxOEroVS7p4` (DIMENSION 3D, M4A1), `eawJa9osZoQ` (Wyatt's Workshop), `Ml2t8uxPAQU` (CG Boost).
