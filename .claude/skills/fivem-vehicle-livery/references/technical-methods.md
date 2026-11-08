# How GTA V liveries work: shaders, UV1 and the three methods

Legend: **(verified: vanilla)** = read from vanilla files exported read-only with CodeWalker.Core and from this skill's binary parser; **(verified: Sollumz)** = Sollumz 2.9 source on the user's PC (`szio/gta5/Shaders.xml`, `shader_materials.py`); **(unverified)** = community claim or inference. Source list: `sources.md`.

## 1. The livery layer is a second diffuse texture on UV channel 1

- Paint shaders with a livery layer have a sampler **`DiffuseSampler2`** read with **TexCoord1** (Sollumz name **"UVMap 1"**): `vehicle_paint3`, `vehicle_paint3_enveff`, `vehicle_paint4`, `vehicle_paint4_enveff`, `vehicle_paint4_emissive`, `vehicle_paint5_enveff`, `vehicle_paint6(_enveff)`, `vehicle_paint7(_enveff)`, `vehicle_paint8`, `vehicle_paint9`. **`vehicle_paint1` and `vehicle_paint2` have no livery sampler** (verified: Sollumz `DiffuseSampler2 … uv="1"`; Sollumz docs "vehicle_paint3: Used for liveries on a car").
- Which other maps share UV1 differs: in `vehicle_paint8` the main diffuse is also on UV1 and dirt on UV2; in `vehicle_paint9` the livery is UV1 and diffuse/spec are UV2. "Livery = UV1" holds for all of them (verified: Sollumz).
- Radit (wrac7MJR0Uk 00:46): "vehicle paint one uses UV map zero, while vehicle paint 3 uses UV map 1".
- The material's paint colour comes from `matDiffuseColor`: x = 2 means paintable, y = z = layer (1 primary, 2 secondary, 3 pearlescent, 4 wheel, 5 interior trim, 6 dashboard) (verified: Sollumz `get/set_vehicle_material_paint_layer`). The livery is drawn **over** that paint colour.
- **Alpha decides coverage.** Modern vanilla liveries are DXT5; transparent pixels let the spawn paint colour show. `polgauntlet_livery1` is 2048² DXT5 and ~98 % transparent (only numbers, badges, "DIAL 911") (verified: vanilla + ImageMagick stats). That the shader lerps paint → livery by alpha is the standard reading, not checked in shader bytecode (unverified detail, consistent with every tutorial).
- `diffuse2SpecMod` (0.8 in `polgauntlet_livery1`) is a livery-related spec parameter (value verified; exact effect unverified).

### Roof liveries: `vehicle_paint3_lvr` + `DiffuseSampler3`
- Vanilla `tornado5` (Tornado Custom): roof mesh uses `vehicle_paint3_lvr` with `DiffuseSampler3 = lowrider_lvr_1`; the ytd holds `lowrider_lvr_1 … _7` (256² DXT1, 7 mips) (verified: vanilla). Native `_SET_VEHICLE_ROOF_LIVERY` "Used to set the tornado custom (convertible) rooftop livery"; `GetVehicleRoofLiveryCount` returns −1 when none (citizenfx/natives).
- It is a **separate texture with its own UV1 layout** — make a second template (`livery_template.py --sampler 3`). On tornado5 the roof UVs run outside 0..1 (tiled), so the template only shows part of it.
- That the game cycles `_lvr_1…_N` by name like `_sign_N` is inferred from the files (unverified).

## 2. Method A — `_sign_N` texture liveries (`FLAG_HAS_LIVERY`)

- vehicles.meta `FLAG_HAS_LIVERY`: "Cycles liveries from vehicle's texture dictionary, up to 30 liveries" (Cfx docs vehicle flags). Vanilla cars with the flag include ambulance, police, police2, police3, sheriff, sheriff2, pony, rumpo, sanchez, polmav, frogger2 … (verified: update.rpf vehicles.meta).
- The yft material references only **`<prefix>_sign_1`** in `DiffuseSampler2`; the ytd carries `_sign_1 … _sign_N`; livery index k shows `_sign_(k+1)`. The prefix does **not** have to be the model name (verified: police.yft → `policenew_sign_1`, police.ytd has `policenew_sign_1…6`; sheriff → `police_sign_1…4`; ambulance.ytd `ambulance_sign_1…3` 512×256 DXT1; sanchez → `sanchez_sign_1…5`).
- Count = consecutive `_sign_N` textures: community knowledge (unverified). Gaps and `_sign_0` are untested — the user's 23DChargerHenPEpd shader points at `redeyesuperstockscv2_sign_0`, unverified whether that cycles.
- Tutorials: never rename; the car and the model viewer show `_sign_1` by default; replace with exactly the same name (JkdthK3tHgo 06:11–06:52; 0JALZnODuag 15:55; Gh1TLTZaxOc 07:36, 14:29). Adding a livery = add `_sign_(N+1)` (biOmm5KPsFU 06:18).
- **Old-gen vanilla style** (police / sheriff / ambulance): the `vehicle_paint3` mesh is only a few decal patches (police.yft: 140 triangles — roof number, door strips, "Keep Your Distance") on a 256² DXT1 atlas; each livery = another atlas with different unit numbers (verified: vanilla + `livery_template.py`). On police the left and right door strips **share the same pixels without mirroring**, so text reads correctly on both sides but is identical. Cheap, but no free design.
- **Modern add-on style**: the whole body is one `vehicle_paint3/4` material with a full UV1 unwrap and one 1024–4096 `_sign_N` per livery (user files: shelby20pd `20gt500_sign_1…6`, GwopJailbreakRedeyepd `char_sign_1…7` 4096 DXT5).
- A first livery that is a tiny transparent texture (8×8, 64×64, 200×200) = "unmarked" livery 0 (iCoobik tykBBo3oI4I 02:32–02:52; seen on several user cars). Vanilla `tornado5_sign_1` is a 4×4 DXT5 placeholder (verified: vanilla).
- **Livery names**: `GetLiveryName(vehicle, index)` returns a text label (Sanchez → `SANC_LV1…5`); "You may need to set the vehicle's modKit to 0 … otherwise this native may return NULL" (citizenfx/natives GetLiveryName). Labels come from the kit's `<liveryNames>` in carcols (vanilla mplowrider2: `SLVAN3_SIGN0…8`) (verified: vanilla). Add-on labels are not in the game's text → `AddTextEntry('LSCSO_LV1', 'LSCSO Patrol')` client-side or menus show NULL (cfx forum livery-menu thread, 2019). `<livery2Names>`: probably roof-livery labels (unverified).

## 3. Method B — modkit livery parts (`VMT_LIVERY_MOD`) — what 2023–25 vanilla police cars use

- polgauntlet, police5, polcaracara, polcoquette4, poldominator10, polgreenwood, polimpaler5/6, polterminus, polbuffalo … have **no `FLAG_HAS_LIVERY`**; liveries are `<model>_liveryN.yft` in `vehiclemods\<model>_mods.rpf`, listed in the kit as `<type>VMT_LIVERY_MOD</type><bone>chassis</bone>` with `modShopLabel` `POLSHARED_LIV1…22` (verified: mp2023_02 carcols, kit `392_polgauntlet_modkit`; vehicles.meta flags only `FLAG_EXTRAS_REQUIRE FLAG_EXTRAS_STRONG`).
- **Inside a livery yft** (verified: `polgauntlet_livery1.yft` → XML): a dummy drawable with one ~2 cm quad (bounding radius 0.0156) on bone `polgauntlet_livery1_ng`, an **embedded texture dictionary** with one texture `polgauntlet_livery1` 2048² DXT5 10 mips, and one `vehicle_paint3` shader whose `DiffuseSampler2 = polgauntlet_livery1`. The body's own paint materials point at `blank` (4×4 DXT5). So the yft is a **texture carrier**: fitting the mod swaps the body's livery layer (behaviour inferred from the layout; matches HK Works c6vuOk4SOxA 01:46–05:45, who renames the texture + XML name and recompiles in CodeWalker).
- `polcaracara_livery1`: 1024² DXT5 9 mips (verified). Rockstar uses 1024–2048 DXT5 for full liveries.
- In game: `SetVehicleModKit(veh, 0)` then `SetVehicleMod(veh, 48, index, false)` — `VMT_LIVERY_MOD = 48` (citizenfx/natives SetVehicleMod). Label: `GetModTextLabel(veh, 48, i)`.
- Pros: one file per livery; add/remove liveries without touching the base ytd; more than 30 possible; works with mechanic/livery menus that use the mod system. That the texture only streams while that livery is fitted is plausible but unverified. Cons: needs a unique kit id (fivem-vehicle-mod registry), carcols + carvariations entries, menus must use `SetVehicleMod`, not `SetVehicleLivery`.

## 4. Method C — baked into the body diffuse

- `firetruk`: body material `vehicle_paint1` with `DiffuseSampler = firetruck_liveries` (512×256 DXT1 atlas: "LOS SANTOS COUNTY FIRE DEPT.", numbers, crest, KEEP BACK); `lguard` uses `lifeguard_body` the same way (verified: vanilla). No switching at all.
- User's um21yukonpd uses `yukon_sign_1` as the **main `DiffuseSampler`** of a non-livery material while vehicles.meta still has `FLAG_HAS_LIVERY` — a fixed livery; the flag does nothing (verified: binary read by `check_livery.py`). The user's 16chargerpd / camaro18bbpd have a `_sign_1` on a livery layer but no flag → also fixed.
- Use only for a one-off car that will never change livery.

## 5. Choosing

| Situation | Method |
|---|---|
| Add-on car that already has a full UV1 body template and `_sign_1` | A (keep it; add `_sign_2…`) |
| A department fleet that will get more liveries later, menus based on mods, > 30 liveries | B (copy the vanilla livery-yft layout) |
| One fixed design, no switching | C, or A with one sign and no flag |
| Car without any livery layer (paint1/2 only) | Rebuild: unwrap UVMap 1, switch body to `vehicle_paint3`, export with Sollumz (template-and-painting.md §1) |

## 6. Texture formats and sizes

- Vanilla: old-gen sign atlases 128–512 px DXT1; modern full liveries 1024–2048 DXT5 with a full mip chain (verified).
- CodeWalker's `TextureFormat` enum: A8R8G8B8, X8R8G8B8, A1R5G5B5, A8, A8B8G8R8, L8, BC7, ATI1, DXT1, ATI2, DXT3, DXT5 (verified: reflection). BC7 appears in the user's uncampd; in-game BC7 on Legacy is unverified.
- Memory incl. full mips (≈ base × 4/3): 2048² DXT1 ≈ 2.7 MiB, DXT5/BC7 ≈ 5.3 MiB, A8R8G8B8 ≈ 21.3 MiB; 4096² DXT5 ≈ 21.3 MiB, A8R8G8B8 ≈ 85 MiB (64 MiB without mips) (arithmetic; `check_livery.py` uses the same formula).
- A .ytd is one streamed resource: every livery inside it loads when the car loads, not just the one shown.

## 7. GTA axes

+Y = front, +Z = up, x < 0 = driver (left) side: vanilla polgauntlet `door_dside_f` x = −0.93, `door_pside_f` x = +0.93 (verified).
