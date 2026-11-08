# Sources

Research 2026-11-08. Vanilla files were exported read-only from the user's GTA V (G:) with CodeWalker.Core and read with CodeWalker XML export and this skill's parser. Timestamps are mm:ss in the English subtitle track.

## Vanilla files read (verified)
- `polgauntlet.yft/.ytd`, `polgauntlet_livery1/2.yft`, `polcaracara(_livery1).yft`, `police5`, `police`, `police2`, `police_hi`, `sheriff`, `ambulance`, `firetruk`, `lguard`, `sanchez`, `tornado5` (yft + ytd); `police4.ytd`, `vehshare.ytd`.
- `update.rpf` vehicles.meta (FLAG_HAS_LIVERY list); `mp2023_01/02` carcols.meta, carvariations.meta, vehicles.meta (VMT_LIVERY_MOD kits, POLSHARED_LIV labels, police spawn colours); `mplowrider2` carcols.meta (liveryNames).

## Documentation
- Sollumz vehicle shaders — https://docs.sollumz.org/documentation/fragments.yft/vehicle-shaders ; Sollumz 2.9 source on the user's PC (`szio/gta5/Shaders.xml`, `ydr/shader_materials.py`, `yft/properties.py`).
- Cfx docs, vehicle flags — https://docs.fivem.net/docs/game-references/vehicle-references/vehicle-flags/
- citizenfx/natives (VEHICLE): SetVehicleLivery, GetVehicleLiveryCount, GetLiveryName, SetVehicleRoofLivery, GetVehicleRoofLiveryCount, SetVehicleMod, SetVehicleModKit, GetNumVehicleMods, GetModTextLabel — https://github.com/citizenfx/natives
- CodeWalker source (Drawable.cs, ShaderGroup/ShaderFX, Texture.cs, TextureFormat enum, RpfFile.GetSizeFromFlags) — layout used by `check_livery.py`, checked against vanilla files.
- Blender manual: UV editing → Export UV Layout; Texture Paint slots; brush texture (Stencil); Cycles baking — https://docs.blender.org/manual/en/latest/
- GIMP 3.2 DDS export — https://docs.gimp.org/3.2/en/file-dds-export.html
- DirectXTex texconv — https://github.com/microsoft/DirectXTex/wiki/Texconv
- paint.net DDS FileType Plus — https://github.com/0xC0000054/pdn-ddsfiletype-plus
- Curiosity-GitHub/addon-liveries (VMT_LIVERY_MOD guide, via fivem-vehicle-mod).
- cfx.re forum, "[Release] Vehicle Livery Menu" page 2 (AddTextEntry per livery label, 2019) — https://forum.cfx.re/t/release-vehicle-livery-menu/40524?page=2
- Wikipedia, Battenburg markings (citation warnings) — https://en.wikipedia.org/wiki/Battenburg_markings
- NFPA 1901 rear chevrons — secondary summaries only; check the current edition.
- FHWA legibility research — https://www.fhwa.dot.gov/publications/research/safety/15027/004.cfm ; US Access Board VMS legibility — https://www.access-board.gov/research/communication/variable-message-signing/vms-legibility/
- Cfx.re real-brand rule, press coverage: https://hitmarker.net/news/gta-rp-players-advised-to-remove-any-content-relating-to-real-world-third-party-ips-2338960 ; https://www.gamesradar.com/gta-5s-biggest-rp-mod-ignites-a-huge-copyright-purge-of-real-world-cars-just-2-months-after-joining-rockstar (read fivem.net/terms for the current text).

## Videos (transcribed)
| id | title / channel | tools | used for |
|---|---|---|---|
| m4CqhT70M-k | How To Make Custom Car Liveries – FiveM / Twisle | OpenIV, Photoshop (paid) | find `sign` in ytd, replace same name 01:08–02:56 |
| 7q6utSsPZwA | How to export livery template for FiveM / FueryMloGuy | CodeWalker, Blender, Sollumz | UVMap 1 active, select linked, Export UV Layout 01:52–05:44 |
| wrac7MJR0Uk | Make a GTA 5 Vehicle UV Map Template in Blender, Sollumz / Radit | Blender + Sollumz | paint1 = UV0, paint3 = UV1 00:46; unwrap 02:17; export layout 04:23; name = sampler 07:48 |
| 0JALZnODuag | Police Car Liveries for GTA 5/LSPDFR in GIMP / TEG | GIMP | 4K → 2K 00:21, 17:19; reference 01:22; Paths + Stroke 02:25–04:50; scale badge once 07:13; flip copy 12:01; 4K made textures vanish 16:58 |
| JkdthK3tHgo | How to add liveries for FiveM using GIMP / BrendonSapp157 | GIMP, OpenIV | no IRL cars 02:44; body lines 03:45; base layer 05:09; DDS + `_sign_1` naming 05:50–06:52 |
| 0eCBJCMn_Jg | Custom Vehicle Liveries for FiveM Absolutely FREE / Xclusive Designs | paint.net, OpenIV | layer plan 03:46; closed shapes 10:18; flip graphic 11:41; text off black areas 23:57; 4096 → 2048 29:44; A8R8G8B8 advice 31:08 (memory-heavy) |
| Gh1TLTZaxOc | Create Your Own CUSTOM Car Liveries / Lil DizNick | OpenIV, Photoshop (paid) | resource layout 06:53; guides 09:40; black area never shows 12:46; sign one/two/three 14:29 |
| dgVnz0Inf78 | FiveM Livery Tutorial / Mr. Green | Photoshop (paid) | layer order 05:39, 15:34; outline text 17:40; all panels 18:22 |
| WsFXPXmIIDw | Create your own police texture, PAINT.NET / Patrol One | paint.net | 2048 → 4096 to work 02:03; colour-pick reference 03:27; roof unit number 29:22 |
| biOmm5KPsFU | Add extra liveries or edit liveries / TuxedoJericho | OpenIV, Photoshop (paid) | add `sign_2` 06:18; dark template areas don't matter 07:00 |
| tykBBo3oI4I | Add a Livery Using OpenIV / iCoobik | OpenIV | sign 1 design, sign 2 = 8×8 transparent 02:32–02:52 |
| ojLmRr8PErI | Installing Vehicle Liveries / Geoffrey_Gamer (Kelly Rock) | OpenIV | a livery only fits its own model 00:41; wrong-model demo 10:07 |
| U8vTQpWMn9Q | Custom Liveries for LSPDFR & FiveM (in-depth) / BigPilotGuy | Photoshop (paid) | panel map 05:55; layers 07:38; bleed 14:36–15:37; decal size vs quality 23:02; "primer grey" 35:12; lighter in game 41:29; exact sign name 42:52; `_hi` ytd 54:32 |
| c6vuOk4SOxA | How to create a YFT livery / HK Works | CodeWalker, Photoshop (paid) | VMT_LIVERY_MOD yft `<spawn>_livery<N>` 01:46; DXT5 + mips 03:35; rename + compile 04:44–05:45; carcols label 07:06; backwards text 02:52; menu section 08:11 |
| 0zsOz1bWgJI | Optimize / Fix Grainy Liveries / Paul Modifications | OpenIV | mip 11 → 1 "fix" 01:02 (not recommended) |
| 2yz2qMRc1aU | How to Fix Blurry 4k Liveries / K.Gilbert | OpenIV | same mip "fix" 01:44 (not recommended); `+hi` ytd 01:02 |

Found, not transcribed (HTTP 429, paid tool, or not needed): VYnIsCJm1Q4 Walejaw 3D "Liverys in Blender 4.0 – when Shrinkwrap isn't the answer"; qOQm2vs48hQ McGinlay "Reflective liveries | ZModeler 3" (paid); rxMCWoEc-1g / F9CPbEhGB5M / B6ozIUFIXT4 ZModeler 3 templates (paid); _NEI_LiSBbU "Battenburg Tutorial"; Wgr_qGxdbe8 "Know Your Battenburgs"; MZ_RfqSiPCI "Export UV map in Blender". No usable speech: jUmd39kzi2U, TpvFpUNuMpo, -vba9H_KBCs.

## Not verified
- In game: alpha blend behaviour, `_sign_0`, the consecutive-numbering rule, BC7 on Legacy and Enhanced, whether VMT_LIVERY_MOD textures stream only when fitted, whether `_lvr_N` roof liveries cycle by name on add-ons, `livery2Names`.
- Livery spec/reflective behaviour (`diffuse2SpecMod`).
- The Blender projection-and-bake workflow for liveries (manual only).
- Exact current Cfx.re licence wording; real-world police livery rules (tutorials and reference sites only).
- GTA V Enhanced (RSC8): `check_livery.py` skips those files; no livery-specific differences checked.
