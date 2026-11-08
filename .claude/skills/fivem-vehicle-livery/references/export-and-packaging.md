# Export, packaging and in-game testing

Meta files (FLAG_HAS_LIVERY, carcols kits, VMT_LIVERY_MOD entries, carvariations, police job config) are owned by `fivem-vehicle-mod` — see its `references/modkits-liveries-sirens.md` and `references/police-emergency.md`. This file covers the texture and where it goes.

## 1. Export settings

Default: **design at 4096 (or 2× the target), export 2048×2048, BC3/DXT5, full mip chain.**
- DXT5 keeps alpha: transparent = spawn paint shows. DXT1 (BC1) only if the livery covers the whole UV with no transparency (half the memory).
- 4096 only for a hero car and never uncompressed (4096 A8R8G8B8 ≈ 85 MiB with mips). TEG: 4K liveries made "trees … start disappearing" (0JALZnODuag 16:58). Xclusive Designs recommends A8R8G8B8 + max mips "for the highest fidelity" (0eCBJCMn_Jg 31:08) — that is 4× the memory of DXT5; don't follow it.
- Power-of-two sizes (GIMP docs: "game engines usually need dimensions that are a power of two"). The user's CChallengerBLFpd / 18CDemonTTChallengerpd carry a 5792² sign — the checker flags it.
- **Keep mips.** The "set mipmaps from 11 to 1 in OpenIV to fix blurry liveries" tip (Paul Modifications 0zsOz1bWgJI 01:02; K.Gilbert 2yz2qMRc1aU 01:44) makes it sharp up close but shimmers/aliases at distance and keeps the full texture resident. Fix blur with size, placement and less total livery memory instead (troubleshooting.md).
- sRGB: export colour textures as sRGB / non-linear (tool default); a "linear" BC7 option gives washed-out colours.

## 2. Free tools

| Tool | How |
|---|---|
| **GIMP** | File ‣ Export As `.dds` → Compression **BC3 / DXT5** (BC1 without alpha; BC7 available), Mipmaps **Generate mipmaps**, leave "Flip image vertically" off; save type "All visible layers" merges (GIMP 3.2 docs, DDS export) |
| **paint.net** | Bundled DDS FileType Plus: BC1/BC2/BC3/BC4/BC7 (linear/sRGB), "Generate mipmaps" (pdn-ddsfiletype-plus README). Xclusive Designs does the whole job in paint.net |
| **texconv** (Microsoft, MIT) | batch: `texconv -f BC3_UNORM -m 0 -dx9 -y -o out livery.png` (`-f BC3_UNORM` = DXT5, `DXT5` is an alias; `-m 0` = full mip chain; `-dx9` writes the classic DDS header; `-pow2` fits power of two; `-sepalpha` separate alpha mips) (DirectXTex wiki). Install `winget install Microsoft.DirectXTex.Texconv` — **ask before installing**. Whether CodeWalker imports DX10-header DDS files was not tested, hence `-dx9` |
| **Krita / Inkscape** | design only; export PNG, then GIMP/paint.net/texconv for DDS |
| **ImageMagick** (installed: `magick`) | preview DDS (`magick livery.dds preview.png`); its DXT5 writing flags are unverified |

## 3. Method A — into the car's .ytd

1. Back up first; never touch the original in `ori\` (user rule).
2. Open `<car>.ytd` in **CodeWalker** (free): RPF Explorer / Folder → open the ytd → Texture dictionary editor. OpenIV (free) also edits loose ytds; tutorials use it (Twisle m4CqhT70M-k 02:56; JkdthK3tHgo 06:11; iCoobik tykBBo3oI4I 02:32–03:12).
3. **Replace** `_sign_N` keeping the exact name, or **add** `_sign_(N+1)` for a new livery (biOmm5KPsFU 06:18). The name must equal what the shader expects (Radit wrac7MJR0Uk 07:48: "Make sure its name matches the diffuse sampler texture exactly").
4. If the car also has `<car>+hi.ytd` with the same `_sign_N`, replace it **there too** — the high-detail dictionary is what you see up close (K.Gilbert 2yz2qMRc1aU 01:02; BigPilotGuy U8vTQpWMn9Q 54:32; the user's uncampd has `23cam_sign_1` in both).
5. Programmatic route (the user already has it): CodeWalker.Core via PowerShell, like `H:\FiveM\vanilla_ref\tools\*`; build ytd from XML + DDS folder. Memory note `gta-half-float-uvs.md` documents the `build_ytd` NameHash pitfall — set and verify the hash.
6. Meta: `FLAG_HAS_LIVERY` in vehicles.meta (→ fivem-vehicle-mod). Livery names: carcols kit `<liveryNames>` + `AddTextEntry` per key.

## 4. Method B — a livery .yft per livery

1. Start from the vanilla layout (`polgauntlet_livery1`: dummy 4-vertex quad, bone `<name>_ng`, embedded texture dictionary with one texture, one `vehicle_paint3` shader with `DiffuseSampler2` = that texture). Copy an existing livery yft's XML (CodeWalker Export XML), rename **all three**: the embedded texture name, the XML `<FileName>`/DDS, and the `DiffuseSampler2` name, to `<model>_liveryN`; put the DDS next to the XML; CodeWalker Import XML to compile (HK Works c6vuOk4SOxA 03:58–05:45).
2. File name `<model>_liveryN.yft` = carcols `modelName`.
3. carcols kit `visibleMods` item: `modelName`, `modShopLabel`, `<type>VMT_LIVERY_MOD</type>`, `<bone>chassis</bone>`; kit id unique (fivem-vehicle-mod registry); the model's carvariations `<kits>` lists that kit. `modShopLabel` is a text **label** — "you can literally name anything" (HK Works 07:06) but add `AddTextEntry` or the menu shows the key/NULL.
4. Remove `FLAG_HAS_LIVERY` unless you deliberately keep both systems (Curiosity-GitHub/addon-liveries guide; vanilla 2023+ police cars have no flag).
5. Do not copy vanilla `polgauntlet_livery*` files into the server — make your own texture and yft.

## 5. Converting someone else's car

Their textures stay 1:1: don't recompress, resize or strip mips (user rule). Only the user's **new** livery textures are sized by this guide. Oversized or uncompressed existing textures are **reported**, not fixed, unless the user asks. `check_livery.py` words its findings that way.

## 6. Testing in game (dev server only)

```lua
-- Method A
local n = GetVehicleLiveryCount(veh)        -- -1 = no livery support
SetVehicleLivery(veh, 0)                     -- index 0 = first livery (community, unverified)
-- Method B
SetVehicleModKit(veh, 0)
local m = GetNumVehicleMods(veh, 48)         -- 48 = VMT_LIVERY_MOD
SetVehicleMod(veh, 48, 0, false)
print(GetLabelText(GetModTextLabel(veh, 48, 0)))
-- roof livery (vehicle_paint3_lvr)
SetVehicleRoofLivery(veh, 1)
```
Natives: citizenfx/natives SetVehicleLivery, GetVehicleLiveryCount, GetLiveryName, SetVehicleMod, GetModTextLabel, SetVehicleRoofLivery. vMenu-style menus put mod liveries in the livery section, not stickers (HK Works 08:11). qbx_police applies `vehicleSettings[model] = { livery = 1 }` on spawn (fivem-vehicle-mod police-emergency.md).

Checklist:
- [ ] every livery index / mod index
- [ ] both sides: text readable, not mirrored or upside down
- [ ] roof from above, hood, trunk/tailgate
- [ ] all LODs: walk away — the livery must not disappear (each LOD needs the livery shader + UV1; vanilla polgauntlet has paint3 in every LOD)
- [ ] day and night; every spawn colour from the job config
- [ ] extras (lightbar, push bar) don't cover text; extras with their own paint3 material carry the livery too (unverified per car)
- [ ] dirt level 0 and 15 (`SetVehicleDirtLevel`)
- [ ] menus show names, not NULL
- [ ] `check_livery.py` clean; server console shows no oversized-asset warning for the ytd
