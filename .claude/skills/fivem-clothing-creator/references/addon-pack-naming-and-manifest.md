# Add-on clothing packs: file names, fxmanifest, limits, entitlement

Researched 2026-11-08. Citations: YouTube id [mm:ss] (auto-caption timestamps, ±10 s) or URL. "(unverified)" = one source, a forum claim, or an inference. "(paid)" = a paid tool or service; T1 rule: mention for context only, never recommend.

Primary code read: grzyClothTool `Helpers/BuildResourceHelper.cs` lines 96–135, 186–187, 250–296, 995–1025 (https://github.com/grzybeek/grzyClothTool). Docs: CFX how-to https://forum.cfx.re/t/how-to-stream-clothes-and-props-as-addons-for-mp-freemode-models/3345474, DCT docs https://docs.gta.clothing/ (files-naming, game-limits-and-crashes, testing-addon-clothes, shop-meta-file), https://docs.fivem.net/docs/game-references/data-files/.

## 1. Entitlement first (the number-one "clothes don't show" cause)

- https://fivem.net/server-hosting lists **"Stream custom clothing"** as a perk of the Element Club **Argentum, Aurum and Platinum** tiers (paid). The perk is tied to the server's license key.
- Without it, streamed freemode clothing does not appear for players on the live server.
- Community and tool docs say a server with a small player cap streams clothing without the perk, which is how people test locally. DCT testing page: set player slots to 10, and if clothing works there but not in production, check the key's entitlement. Same in ba86DBN396k [59:57–60:31] and forum https://forum.cfx.re/t/i-have-payed-for-element-club-but-cant-stream-clothing/5278247. Older sources say 8 (3klwlNCH7XA [9:20]) or a $15 Patreon (Gu1vkyzbCy4 [0:39], 2019). **The exact slot number is not on an official page (unverified).**
- What to tell the user: check their own key's tier on the Cfx portal; test on the local test server with a small `sv_maxclients`; do **not** recommend buying a tier (T1: no paid services). If they already have the perk, nothing changes.

## 2. Add-on file names (exact patterns)

`<ped>` is `mp_m_freemode_01` (male) or `mp_f_freemode_01` (female). `<dlc>` is the pack name: **lowercase, no spaces, unique on the server** (CFX: "Your ymt name should be all lowercase!"; DCT says uppercase has reportedly caused issues; hVjXvs0jizs [1:41], [3:20]).

| File | Pattern | Example |
|---|---|---|
| Collection YMT (one per gender) | `stream/<ped>_<dlc>.ymt` | `mp_m_freemode_01_mypack.ymt` |
| Component model | `<ped>_<dlc>^<comp>_<NNN>_<u\|r>.ydd` | `mp_m_freemode_01_mypack^jbib_000_u.ydd` |
| Component texture | `<ped>_<dlc>^<comp>_diff_<NNN>_<a-z>_<uni\|whi>.ytd` | `…^jbib_diff_000_a_uni.ytd` |
| Prop model | `<ped>_p_<dlc>^p_<anchor>_<NNN>.ydd` | `mp_m_freemode_01_p_mypack^p_head_000.ydd` |
| Prop texture | `<ped>_p_<dlc>^p_<anchor>_diff_<NNN>_<a-z>.ytd` (**no `_uni`**) | `…_p_mypack^p_head_diff_000_a.ytd` |
| Cloth physics | same base name as the model, `.yld` | `…^jbib_000_u.yld` |
| First-person alternate | base name + `_1.ydd` | `…^jbib_000_u_1.ydd` |
| Shop meta (resource root) | `<ped>_<dlc>.meta` (grzyClothTool name; the content is what counts) | `mp_m_freemode_01_mypack.meta` |
| Creature metadata | grzyClothTool: `stream/mp_creaturemetadata_<m\|f>_<dlc>.ymt`; DCT: `mp_creaturemetadata_<dlc>.ymt`; CFX template: `MP_CreatureMetadata_<dlc>` | — |

- Sources: BuildResourceHelper.cs 96–135; CFX how-to; DCT files-naming; videos uBBHJ4vG4fM [19:34–21:50], G3sLt5WFqtg [5:05–5:40], ey_YiqZoMOQ [42:24–43:34].
- The creature metadata name is tool-specific. What matters: the meta's `<creatureMetaData>` value equals the streamed YMT's base name (forum https://forum.cfx.re/t/how-to-create-addon-heels-or-hide-hair-with-addon-hat/4209989). grzyClothTool writes the line in every meta but only generates the YMT when heels or hat hair-scale are enabled (lines 186–187, 1005), so a missing creature YMT is normal when neither is used.
- `_u` + `_uni` = no skin; `_r` + `_whi` = contains skin. The face/skin preview labels `whi, ara, chi, lat, bla, pak` also appear on vanilla head textures (DCT skin-tone page).
- Numbers are three digits, start at `000` and stay contiguous (G3sLt5WFqtg [1:37–2:13], ey_YiqZoMOQ [30:19–30:54]). A gap shows as a blank item in single-player packs (M4jwYOIVM6s [10:29–11:08]; unverified for FiveM).
- `stream/` may have subfolders; grzyClothTool sorts by gender/category (hVjXvs0jizs [2:16–2:48]; YrsNjOoeqL0 [3:24]).
- "You need YDD files; YTD alone is useless" for a new item (YrsNjOoeqL0 [1:08]; 5UhBgr9TsrM [9:23]).

## 3. Replacement instead of add-on

- Base-game slot: `mp_f_freemode_01^<file>`. DLC slot: `mp_f_freemode_01_<dlc folder, e.g. mp_f_xmas_…>^<file>`. The DLC prefix comes from tobii.space or the mod description (3klwlNCH7XA [3:31–4:58], [7:58–8:31]).
- Converting a single-player mod: "the folder it installs into in story mode + `^` + filename" in `stream/` plus an fxmanifest (-Ys6AaEXsf8 [1:04–2:40], [4:22–4:57]).
- DCT warns that replacing takes over **the whole collection**, can remove original items and can shift global drawable IDs (game-limits page). Streaming a vanilla `mp_?_freemode_01.ymt` replaces the base collection (seen in the user's ONX face packs).
- Extending a vanilla drawable's texture count (for example to 26) by editing and streaming the vanilla YMT is a replacement too (p929w_ZfICA [2:49–6:09]).
- DCT's Enhanced output supports add-on only; replacement packs get no Enhanced output (testing page).

## 4. Shop meta (`ShopPedApparel`)

grzyClothTool writes (BuildResourceHelper.cs 995–1025):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ShopPedApparel>
    <pedName>mp_m_freemode_01</pedName>
    <dlcName>mypack</dlcName>
    <fullDlcName>mp_m_freemode_01_mypack</fullDlcName>
    <eCharacter>SCR_CHAR_MULTIPLAYER</eCharacter>          <!-- female: SCR_CHAR_MULTIPLAYER_F -->
    <creatureMetaData>mp_creaturemetadata_m_mypack</creatureMetaData>
    <pedOutfits></pedOutfits>
    <pedComponents></pedComponents>
    <pedProps></pedProps>
</ShopPedApparel>
```

`fullDlcName` = `pedName_dlcName` = the YMT base name = the file prefix before `^`. One meta per gender.

## 5. fxmanifest

grzyClothTool output (BuildResourceHelper.cs 250–296):

```lua
fx_version 'cerulean'
game 'gta5'

files {
  'mp_m_freemode_01_mypack.meta',
  'mp_f_freemode_01_mypack.meta',
  'first_person_alternates_mypack.meta',      -- only if _1 models exist
  'pedalternativevariations_mypack.meta',     -- only if alternates exist
}

data_file 'SHOP_PED_APPAREL_META_FILE' 'mp_m_freemode_01_mypack.meta'
data_file 'SHOP_PED_APPAREL_META_FILE' 'mp_f_freemode_01_mypack.meta'
data_file 'PED_FIRST_PERSON_ALTERNATE_DATA' 'first_person_alternates_mypack.meta'
data_file 'ALTERNATE_VARIATIONS_FILE' 'pedalternativevariations_mypack.meta'
```

- Meta files sit in the resource root and are listed in `files`. YMT/YDD/YTD/YLD go in `stream/` and need no listing (CFX how-to; uBBHJ4vG4fM [22:22–24:39]).
- docs.fivem.net data-files: `SHOP_PED_APPAREL_META_FILE` (CExtraMetaDataFileMounter); `ALTERNATE_VARIATIONS_FILE` and `PED_FIRST_PERSON_ALTERNATE_DATA` (CPedVariationStreamFileMounter). Also listed: `PED_FIRST_PERSON_ASSET_DATA`, `PEDSTREAM_FILE`, `PED_OVERLAY_FILE`, `PED_METADATA_FILE`.

## 6. Limits per collection and per server

| Limit | Value | Source |
|---|---|---|
| Textures per drawable | 26 (a–z) | DCT; Sollumz |
| Drawables per type per gender | 128 is legacy guidance; FiveM sync 0–255 needs current client and server | DCT game-limits; Anurag "strict limit of 127… not well synced" uBBHJ4vG4fM [24:39–25:13] |
| Usable per collection | 255; at 256 the collection reports zero | DCT game-limits |
| grzyClothTool | v1.3.0 (2026-07-14) supports 256 per type, 128 still selectable, auto-splits into several add-ons | release notes |
| Add-on YMT slots | few, and the free count changes per game build (about 3–5 on b3717–b3889 per the DCT table). "After each game update the custom limit decreases by one" (uBBHJ4vG4fM [25:13]; 4hbtnxOxi9k [24:42]) is roughly, not literally, true. "Fifth people start to crash" (p929w_ZfICA [1:45–2:17], older build, unverified) | DCT game-limits |
| Shop meta global list | 65,520 entries (one per item and texture). Left for clothing: 44,552 at b1604 down to 29,084 at b3889. Overflow can crash clients while the pack loads | DCT game-limits |
| TxdStore pool | 95,500 entries | DCT game-limits |
| Legacy streamer budget | 65,535 assets per streamer | DCT game-limits |
| pedalternatevariations | 128 before b2189, 160 from b2189, 512 on FiveM with the fix; over = ERR_MEM_MULTI_ALLOC_FREE | DCT game-limits |
| Asset memory | warnings above 16 MiB, tiers at 32/48/64 MiB (warnings, not caps) | DCT; Cfx forum https://forum.cfx.re/t/oversized-assets-can-and-will-lead-to-streaming-issues/1761205 (unofficial) |

- Put everything in one YMT per gender instead of many small packs.
- A 4096² badge diffuse took 64 MiB in the txAdmin console; keep assets around 32 MiB or less (AEy2Rr66l40 [4:53–5:29], unverified crash threshold).
- Server owners often cap textures themselves, for example 1000 or 2000 px (5UhBgr9TsrM [13:18]).

## 7. Order, IDs and collisions

- Add-on items appear after vanilla, at the end of each list (YrsNjOoeqL0 [3:58]; DCT testing page). `ensure` order sets the order between packs.
- Global drawable IDs depend on game build and `ensure` order. Store the collection name plus the local ID (DCT shop-meta-file, placeholders-dummy-ids). DCT shows "R" (relative) and "A" (actual) numbers; "A" changes with the build (ba86DBN396k [56:37–57:43]).
- Two packs with the same `dlcName`/YMT name collide; only one loads (concept from 6MY-PDRLrac [0:33–1:06], a paid promo; unverified mechanism). The same stream file name in two resources: only one wins.
- Starting a clothing resource on a running server needs players to reconnect, and can crash; restart the whole server (DCT game-limits; hVjXvs0jizs [3:20]).

## 8. Game build and Enhanced

- FiveM for GTA V Enhanced runs only the latest build (b3889 at research time) with pure mode always on; older builds are Legacy-only (https://docs.fivem.net/docs/server-manual/server-commands/).
- Legacy and Enhanced packs are not interchangeable. DCT outputs Gen9 for add-on packs only.
- Cfx Alchemist (free, Windows 11, Cfx Portal) converts YDR/YTD/YFT/YPT/YDD from Legacy to Enhanced: `AlchemistCli.exe <in> <out> [--refine] [--relaxed] [-f] [-jN] [--fail-on-error]`. Nothing clothing-specific is documented (https://docs.fivem.net/docs/alchemist/); converting a clothing pack is unverified.
- The checker reports `RSC8` files as probably Enhanced (unverified magic mapping).

## 9. Test procedure

1. Clean local test server with vMenu (or the appearance menu) and `ensure <pack>`; small `sv_maxclients` when the key lacks the perk.
2. Start the pack before players join; reconnect after changes.
3. Connect to localhost. New items are at the end of each category or in the last DLC section (DCT testing page; G3sLt5WFqtg [6:14]: chain count 177 → 181 after adding 4).
4. Menus can show a different index (off by one) or miss add-ons; Simple Trainer missed them, EUP menu and Skin Control showed them (9ZzSo1kdGjc [7:51–8:59]; p929w_ZfICA [6:43]).
