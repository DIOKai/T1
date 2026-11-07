# Components, props, flags, hair hiding and female specifics

Researched 2026-11-08. Citations: YouTube id [mm:ss] or URL. "(unverified)" = one source or an inference. Code read: grzyClothTool `Models/Drawable/GDrawable.cs`, `Helpers/BuildResourceHelper.cs` 872–946 and 1163–1240, `Enums.cs` (https://github.com/grzybeek/grzyClothTool). Docs: https://docs.gta.clothing/game-mechanics/ (drawable-types-and-textures, behaviour-flags, ped-expression-flags, model-alternations, prop-mask-models, skin-tone-data, game-limits-and-crashes) and https://docs.gta.clothing/basics/essential-knowledge/cutting-hairs.md.

## 1. Component ids (`SetPedComponentVariation`)

| id | code | holds | notes |
|---|---|---|---|
| 0 | head | face | own skin workflow |
| 1 | berd | masks, big masks | hair cut via alternate hair models, not expression mods |
| 2 | hair | hair | needs `MH_Hair_Scale` bone for hats to shrink it |
| 3 | uppr | torso skin, arms, gloves ("arms" in menus) | `_r` common |
| 4 | lowr | legs, pants | `_r` when legs/skin are modelled |
| 5 | hand | bags, backpacks | alternates `_1`…`_28` fit over outfits |
| 6 | feet | shoes | `_r` when ankle skin shows; heels via creature metadata |
| 7 | teef | chains, scarves, parachutes, scuba tanks | first-person `_1` possible |
| 8 | accs | undershirts (worn under a top) | first-person `_1` possible |
| 9 | task | body armour, vests | first-person `_1` possible |
| 10 | decl | decals, shirt prints, emblems | |
| 11 | jbib | tops, jackets | first-person `_1` possible |

Sources: grzyClothTool Enums.cs; DCT drawable-types page. Old YMT XML lists components in this fixed order (Gu1vkyzbCy4 [13:29]).

## 2. Props (`SetPedPropIndex`)

| id | anchor | shown in pickers |
|---|---|---|
| 0 | p_head (hats, helmets) | yes |
| 1 | p_eyes (glasses) | yes |
| 2 | p_ears (earrings, earpieces) | yes |
| 6 | p_lwrist (watches) | yes |
| 7 | p_rwrist (bracelets) | yes |
| 3, 4, 5, 8–12 | p_mouth, p_lhand, p_rhand, p_hip, p_lfoot, p_rfoot, p_ph_l_hand, p_ph_r_hand | exist, not shown in pickers |

Props specifics:
- **One UV map only**; UVMap 1 is not needed (UyXC-6PEbkg [8:16]).
- A prop attaches at its anchor bone. To fit a hat, snap the prop's drawable dictionary to `SKEL_Head` (Shift+S cursor to selected, then selection to cursor) and rotate (UyXC-6PEbkg [6:36–7:43]). Swap the mesh by Ctrl+J into the vanilla object and delete the vanilla faces (same trick as Druu's).
- Textures: the diffuse is the external `p_<anchor>_diff_NNN_<letter>.ytd`; normal and spec are embedded in the YDD (Gu1vkyzbCy4 [9:21–9:58]).
- A visor uses the `ped_alpha` shader and the shell `ped` (UyXC-6PEbkg [11:34]). Props get colour0 `#FF8000` and black colour1 like components (UyXC-6PEbkg [8:16]).
- CodeWalker may fail to preview Sollumz-exported props that still work in game (UyXC-6PEbkg [9:56]; unverified).
- **Dummy slot 000**: a tiny plane weighted to the head, hidden inside the ped, so the real accessory (001) is off by default (UyXC-6PEbkg [20:22–21:58]). DCT calls these "Reservation Dummy" placeholders.
- Hats physically fall off when the ped is hit (UyXC-6PEbkg [11:34]); this is probably tied to `USE_PHYSICS_HAT_2` (unverified link).
- Single-player only: add-on hats need the "Ped Prop Limit Adjuster" ASI (9ZzSo1kdGjc [1:06–2:15]); FiveM fixed the global prop-index 8-bit issue in PR #2421 (DCT game-limits).

## 3. What the tool writes into the YMT (grzyClothTool source)

| Field | Value | Lines |
|---|---|---|
| `propMask` | 17 if the drawable has skin (`_r`), else 1 (CFX how-to: 17/19/21 for `_r`) | 872–882 |
| per-texture `texId` | 1 with skin, else 0 | 872–882 |
| `distribution` | 255 | 872–882 |
| `numAlternatives` | 1 when a first-person `_1` model is set | 873 |
| `clothData.ownsCloth` | 1 when a `.yld` is set | 874 |
| component `expressionMods` | `[0,0,0,0, heel]`: index 4 = HighHeelsValue (default 1.0) when EnableHighHeels | 901; GDrawable.cs 321 |
| prop `expressionMods` | `[-hairScale, 0,0,0,0]`: index 0 = minus HairScaleValue (default 0.5) when EnableHairScale | 923; GDrawable.cs 311 |
| component `flags` / prop `propFlags` | sum of the selected ePedCompFlags | 899–946 |
| `audioID` | JenkHash of the audio preset (mostly shoes) | 899–946 |

Creature metadata (lines 1163–1240, "taken from ymteditor"):
- Heels: `pedCompExpressions` items with `pedCompID 6`, `pedCompVarIndex <n>`, `pedCompExpressionIndex 4`, `tracks 33`, `ids 28462`, `types 2`, `components 1`.
- Hats: `pedPropExpressions` with a first dummy item at `pedPropVarIndex -1` (code comment: "without it, fivem was sometimes crashing(?)"), then one per p_head prop with `ids 13201`, `pedPropExpressionIndex 0`.
- The meaning of ids 28462 and 13201 is unverified. The forum says two `-1` entries may crash (unverified).

## 4. ePedCompFlags (bit values)

grzyClothTool `Enums.cs`, citing alexguirre's rage-parser-dumps for build 3179. The flags field is the **sum** of the bits.

| Flag | Value | Flag | Value |
|---|---|---|---|
| BULKY | 1 | JOB | 2 |
| SUNNY | 4 | WET | 8 |
| COLD | 16 | NOT_IN_CAR | 32 |
| BIKE_ONLY | 64 | NOT_INDOORS | 128 |
| FIRE_RETARDENT | 256 | ARMOURED | 512 |
| LIGHTLY_ARMOURED | 1024 | HIGH_DETAIL | 2048 |
| DEFAULT_HELMET | 4096 | RANDOM_HELMET | 8192 |
| SCRIPT_HELMET | 16384 | FLIGHT_HELMET | 32768 |
| HIDE_IN_FIRST_PERSON | 65536 | USE_PHYSICS_HAT_2 | 131072 |
| PILOT_HELMET | 262144 | WET_MORE_WET | 524288 |
| WET_LESS_WET | 1048576 | | |

- Example: NcProductions' motorcycle helmet uses **136193** (UyXC-6PEbkg [12:41]) = 131072 + 4096 + 1024 + 1 = USE_PHYSICS_HAT_2 + DEFAULT_HELMET + LIGHTLY_ARMOURED + BULKY (the decomposition is arithmetic, not stated in the video).
- DCT caveats (https://docs.gta.clothing/game-mechanics/behaviour-flags.md): "Bulky" does not remove the item in cars; "Armoured" is helmet-only. NOT_IN_CAR ("Remove in vehicle") and the helmet flags control vehicle behaviour (ba86DBN396k [20:02–20:36]).
- YMTEditor clamps `expressionMods` to −2…+2 while the game accepts about −8…+8; edit in CodeWalker for larger values (UyXC-6PEbkg [13:14]; game range unverified).

## 5. What hides what

**Hats (p_head) shrink hair** through the prop's `expressionMods[0]`:
- Values: Show 0, Cut −0.5, Remove −1, Custom 0…−1 (DCT cutting-hairs, ped-expression-flags; forum 4209989).
- Only works on hair rigged with the **`MH_Hair_Scale`** bone (bone tag 50788, scale X/Y/Z; UyXC-6PEbkg [4:23–4:57]). Base-game hair ids below 36 were patched and do not respond — test with id ≥ 36. DCT: "98% of custom made hair doesn't" have the bone.
- The pack also needs the creature metadata YMT, referenced by the meta's `creatureMetaData`. DCT's "disable extra YMT" option breaks it (ba86DBN396k [54:55]).
- Hair weighted fully to the scale bone with a big negative value also shrinks under car roofs; NcProductions weights it at 0.1 and uses −8 (UyXC-6PEbkg [13:46–14:50]).
- Free tool route: grzyClothTool hair-scale slider on the prop (u6V9MoEqwfw [2:58]); "has hair" option on head props (AEy2Rr66l40 [2:43]).

**Masks (berd)** do not use expression mods. Cut/Remove swaps the hair to predefined alternate models (`_2`, `_3`) through `pedalternatevariations.meta`, declared with `data_file 'ALTERNATE_VARIATIONS_FILE'` (DCT cutting-hairs, model-alternations).

**Hoodies (jbib) and undershirts (accs)** have a "hoodie hairs" option in DCT (ba86DBN396k [22:51–23:24]); probably alternate hair models too (unverified).

**First person**: `_1` models exist for teef, accs, task and jbib, declared through `first_person_alternates_<dlc>.meta` + `data_file 'PED_FIRST_PERSON_ALTERNATE_DATA'`. Prop mask models (`prop_mask_motobike`, `prop_mask_scuba01…04`, `prop_mask_specops`…) mask the first-person view for hats, eyes, masks and undershirts (DCT prop-mask-models). Flag HIDE_IN_FIRST_PERSON hides the item instead.

## 6. Arms (uppr) with tops

- A see-through gap at the arms or torso with a new top usually means the matching uppr ("arms") drawable is not selected (YrsNjOoeqL0 [2:49], [3:58]; 3klwlNCH7XA [10:11]).
- illenium-appearance job outfits pair each jacket with an arms value, for example torso2 55 + arms 19 (`shared/config.lua` 607–628).
- No authoritative jbib-to-uppr compatibility table was found. Best rule: fit tops so they work over the full uppr or the ~15 base uppr (Druu Pl703WrlCnE 32:34–33:49), and tell the user which arms value to pair.

## 7. Skin (`_r` / `whi`)

- The YMT side is propMask 17 and texId 1. Renaming to `_r` without that data "won't work" (M4jwYOIVM6s [5:55]).
- The diffuse should be the first and only texture in its YTD, alpha authored, with a correct embedded spec/blend mask. Preview labels `whi, ara, chi, lat, bla, pak` are for checking contrast and alpha coverage, not exact colours (DCT skin-tone page).
- Add-on pants showing hand/skin textures: "it's the naming" (p929w_ZfICA [8:23]); likely `_r`/`whi` versus `_u`/`uni` mismatch (unverified cause). The checker flags the mismatch.

## 8. Female (mp_f_freemode_01)

- Own YMT and meta: `pedName mp_f_freemode_01`, `eCharacter SCR_CHAR_MULTIPLAYER_F`, skeleton `mp_f_freemode_01.yft` (uBBHJ4vG4fM [3:29], [23:30–24:04]).
- **High heels (free route answered from source)**: grzyClothTool `EnableHighHeels` + HighHeelsValue writes component `expressionMods[4]` and the heel entry in `mp_creaturemetadata_f_<dlc>.ymt` (section 3). DCT (paid): default 1.0, 0.1 steps, maximum about 3.0; a low heel suits about 0.1 (ba86DBN396k [21:10–22:18]). Tune until the feet stop sinking or floating.
- Heel walking sound: in YMTEditor set `hash_2FD08CEF` to `shoe_heels` (forum 4209989).
- Custom non-freemode peds set heel height in the YMT itself (pumps −0.5, sandals −1.2; UyXC-6PEbkg [19:47–20:22]). Do not copy that to freemode.
- Breast jiggle: vertex groups `SPR_L_Breast` / `SPR_R_Breast`, painted lightly, not full red (YVk_rkkKS6o [56:22–57:36]; naming in the freemode skeleton unverified).
- Leave "breathing room" for other bust/body sizes (Druu 29:49–30:13). No further authoritative female fitting rules were found.

## 9. YMT tools (free first)

| Tool | Cost / licence | Notes |
|---|---|---|
| **grzyClothTool** (grzybeek) | Free, **GPL-3.0** | Active (v1.3.0 2026-07-14). Builds the whole resource for FiveM/alt:V/SP: YMT, metas, fxmanifest, creature metadata, first-person and alternate metas. Heels, hair scale, YLD per drawable, flags, audio, 3D preview with "keep preview" layering (u6V9MoEqwfw [5:03]), PNG/DDS import and conversion (u6V9MoEqwfw [1:45]), duplicate inspector, texture optimiser, 256/type with auto-split. README says "WORK IN PROGRESS"; Discord support only for Ko-fi supporters. An old version needed a manually created `build_output` folder for SP builds (9ZzSo1kdGjc [4:31–5:40]) |
| **YMTEditor** (grzybeek) | Free; **no licence file** (`license: null`) | Last release v1.4.1_hotfix 2023-12-04; effectively superseded (inference). Flow: File > New, gender + name, tick components, "+1 texture" per letter, "add new drawable", save into `stream/` (G3sLt5WFqtg [1:05–3:20]; uBBHJ4vG4fM [17:48–19:34]). Props: Props > p_head/p_eyes, "add new prop" (UyXC-6PEbkg [9:24], [12:08]). Caveats: expressionMods clamped to ±2; loading and re-saving an existing YMT wiped props (forum 4209989, 2021) — create new YMTs instead |
| Durty Cloth Tool | **Paid** (about €10/month; ba86DBN396k [1:04]) | Do not recommend. Its docs are useful for concepts |
| Vestium (alpha) | unknown | Not studied (no captions) |
| 3ds Max + GIMS EVO | 3ds Max is paid | Old route (ey_YiqZoMOQ [2:12–3:18]) |
