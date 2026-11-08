# Livery troubleshooting

Run `py -3 scripts/check_livery.py <resource>` first — it catches most causes in the "files" column. Codes in brackets are its finding codes.

| Symptom | Likely cause | Fix |
|---|---|---|
| Livery doesn't show at all | Texture name ≠ the shader's `DiffuseSampler2` name [LIVERY_TEX_MISSING] — on the user's server 18CDemonTTChallengerpd and CChallengerBLFpd point at `redeye_sign_1` but ship `23HennesseyChallenger_sign_N` | Rename the texture to the sampler name (or fix the shader in Sollumz) |
| | Texture is in another ytd [LIVERY_TEX_OTHER_YTD] | Move it into `<car>.ytd`, or a txdRelationships parent |
| | Body is `vehicle_paint1/2`, no livery layer [FLAG_NO_LIVERY_LAYER] | Unwrap UVMap 1, switch to `vehicle_paint3`, re-export (template-and-painting.md §1) |
| | Sign used as the main diffuse = baked (method C) [BAKED_LIVERY] | Expected: fixed livery. For switching, rebuild as method A |
| | Method B: part yft missing, kit not in carvariations, embedded texture name ≠ sampler [LIVERY_MOD_*] | Fix names; kit in `<kits>`; recompile the livery yft |
| Only one livery / can't cycle | No `FLAG_HAS_LIVERY` [SIGNS_NO_FLAG]; only `_sign_1` in the ytd [FLAG_ONE_SIGN]; gap in `_sign_N` [SIGN_GAP] (unverified); menu uses `SetVehicleLivery` on a mod-livery car | Add the flag (fivem-vehicle-mod); number signs 1…N; use `SetVehicleMod(veh, 48, i)` for method B |
| First livery is blank | `_sign_1` is a tiny transparent placeholder (unmarked) [SIGN_1_PLACEHOLDER] | Intended on many packs; set `livery = 1` (or the right index) in the police job config |
| Text backwards | Island mirrored in UV1, or text flipped when copying a side | Template `M` islands: mirror the text there; never flip text when copying sides |
| Text upside down / sideways on one side | That side's island is rotated (vanilla polgauntlet passenger side = 180°) | Rotate the text per island (template white arrow = up) |
| Livery on one side only | The other side's panels are not on the livery material, or have no UV1; or the art was placed only in one side's island | Check both red and blue islands in the template; checker test |
| Same unit number on both sides, arrows point backward on one side | Left/right share the same pixels (vanilla police door strips) | Expected with that template; to differ, separate the islands in Blender |
| Blurry / grainy | Texture too small for the island (≈ 2 px/cm at 1024), text < ~40 px tall, repeated rescaling of badges, DXT artefacts on fine text, or the game shows a **lower mip** because texture memory is full (too many 4K/uncompressed liveries, low texture setting) [TEX_OVER_2048, TEX_UNCOMPRESSED, LIVERY_MEMORY] | Export 2048 DXT5 from a 4096 design; bigger text on flat panels; scale badges once; cut total livery memory. Don't use the "mip 11 → 1" trick (shimmer at distance) [TEX_NO_MIPS] |
| Changed the livery, old one still shows | `<car>+hi.ytd` holds the same `_sign_N` [HI_DUPLICATE]; or the client cache | Replace in both ytds; restart the resource / clear the client cache |
| Livery disappears at a distance | Medium/Low LOD has no livery shader or no UV1 [LOD_NO_LIVERY] | Give every LOD body `vehicle_paint3/4` + UVMap 1 |
| Looks flat, "primer grey", colours lighter than in the editor | Livery pixels replace metallic paint; game lighting brightens (BigPilotGuy 35:12, 41:29) | Leave body areas transparent so the paint shows; darken livery colours a bit; test in game |
| Whole car turns one colour | Alpha is opaque where the paint should show; exported DXT1/without alpha | Transparent background, DXT5 |
| Colours wrong / banded | Linear vs sRGB export, gradients on DXT, wrong paint layer (`matDiffuseColor`) | sRGB, flat colours, check the material's paint layer |
| Hairline seams | No bleed past island edges; mips mix in the black background | Paint 2–4 px past edges |
| Livery made for another car doesn't fit | Every model has its own UV1 layout (Kelly Rock ojLmRr8PErI 00:41–01:01) | Make it from that car's template |
| Trees/textures vanish, stutter near the car | Livery memory over budget (4096 / A8R8G8B8) (0JALZnODuag 16:58) | 2048 DXT5; for the user's existing cars report only (1:1 rule) |
| Livery missing on extras (lightbar, push bar) | Extras have their own material without paint3/UV1 (unverified per car) | Give the extra a livery material or keep text off it |
| Menu shows NULL | No `AddTextEntry` for `liveryNames` / `modShopLabel` [LABEL_NO_TEXT]; modKit not set before `GetLiveryName` | `AddTextEntry('<KEY>', 'LSCSO Patrol')`; `SetVehicleModKit(veh, 0)` first |
| BC7 livery looks broken | BC7 on Legacy unverified [TEX_BC7] | Re-export DXT5 |

## Real findings on the user's server (2026-11-08, read-only run, not fixed)

`check_livery.py` on `resources/[assets]/[vehicles]` (43 resources, 7 s): 3 errors, 90 warnings. Highlights:
- **Livery texture missing**: 18CDemonTTChallengerpd, CChallengerBLFpd (`redeye_sign_1` not in ytd), camaro18bbpd (`zl1_sign_1`).
- **FLAG_HAS_LIVERY without a livery layer**: 2019rtrpd, 23RTShakerWBpd, 24mustdhpd, challengerhawkpd, fmgtpd, um21yukonpd (um21yukonpd uses `yukon_sign_1` as the main diffuse = baked).
- **Memory**: GwopJailbreakRedeyepd and its V2 (~131 MiB each, same set duplicated), hellcatgkpd (~123 MiB), chaltrxleopd / chartrxleopd (4096 A8R8G8B8 ≈ 65 MiB each).
- **Leftovers**: "Untitled design - 2023-08-29…" ×2 in hellcatgkpd, "untitled" in chaltrxleopd, "Untitled" in 23DChargerHenPEpd.
- `_sign_0` / sign numbering oddities: 23DChargerHenPEpd (shader → `_sign_0`), 18CDemonTTChallengerpd, CChallengerBLFpd, 23HennesseyChallengerpd.
- Non-power-of-two signs (200×200, 5792×5792); mach1pd VLow LOD without livery layer; uncampd `23cam_sign_1` BC7 in both ytd and +hi.ytd; kits with `shaker_sign_N` livery names but no AddTextEntry.
Per the 1:1 rule these are reported to the user, not changed.
