---
name: fivem-clothing-creator
description: Use when the user makes, fits, fixes, packages or installs GTA V / FiveM freemode clothing or accessories (mp_m/mp_f_freemode_01) — tops, jackets, pants, shoes, masks, bags, hats, glasses, watches; add-on or replacement clothing packs; YMT, shop meta, creaturemetadata or fxmanifest; grzyClothTool or YMTEditor; Sollumz clothing export; cloth physics (YLD); adding clothes to illenium-appearance or another appearance menu; or when clothes are invisible, stretched, clipping, missing textures, in the wrong slot, crash on load, or a hat does not hide hair. Triggers include 做衣服, 自制衣服, 衣服不显示, 帽子, 眼镜, 配件, ymt, 衣服包, illenium-appearance 加衣服, 女角衣服.
---

# FiveM Clothing Creator

Clothing that fits the freemode body, deforms with the GTA skeleton, renders at every LOD, and loads into the menu.

> **Before you start: streaming entitlement**
> Cfx lists **"Stream custom clothing"** as a perk of the paid Element Club tiers (**Argentum** and above, https://fivem.net/server-hosting). If the server key lacks it, streamed clothing does not appear on the live server; the user must check their own key. Local test servers with a small player cap are reported to work without it (10 slots per DCT/forum, 8 in older sources; unverified). State it as a fact to check and **do not recommend buying a tier** (T1: no paid services).

## Define the contract first

Male/female, component or prop slot (`components-props-and-flags.md`), add-on or replacement, Legacy or Enhanced, texture variants, skin showing (`_r`) or not (`_u`), the appearance script. Keep originals untouched; confirm the user may modify them.

## Workflow

1. **Base assets.** CodeWalker: export the freemode YFT, a vanilla donor of similar type and shape, and nude body parts; import with Sollumz **Import External Skeleton** (`clothing-step-by-step.md` §1–2).
2. **Model or fit.** Free routes: sewing sim, mask extract, manual retopo (`cloth-physics-and-extras.md` §5). Fit to the vanilla body with Grab/Snake Hook/Elastic/Blob; leave breathing room; fit tops over the base arms (uppr).
3. **Weights.** Transfer from the vanilla donor (Transfer Weights or a Data Transfer modifier), smooth, max 4 influences, Merge by Distance for seams. Pose-test, ideally with a real GTA clip on the NLA (`cloth-physics-and-extras.md` §6).
4. **Textures and variants.** Diffuse per letter a–z (≤ 26), normal and spec embedded, never the diffuse. 1024 default, skin diffuse ≤ 512, power of two, mipmaps; BC7 for dark fabric (BC1 blocks), BC3 for alpha. Keep UVMap 0 (textures) and UVMap 1 (blood/tattoos). Vertex colours `#FF8000` a1 / `#000000` a0.
5. **LODs and export.** High/Med/Low (Sollumz LOD Tools or manual decimate), shader `ped`/`ped_alpha`, export (current Sollumz: File > Export > RAGE Asset, CW XML + Gen8), convert in CodeWalker and preview there.
6. **YMT, meta, resource — free tool.** **grzyClothTool** (free, GPL-3.0) writes the YMT, shop metas, fxmanifest, creaturemetadata (heels, hat hair scale), first-person/alternate metas, and splits oversized packs. YMTEditor (free, no licence file, last release 2023-12) clamps expressionMods to ±2 and once wiped props on re-save; make new YMTs. Durty Cloth Tool is **paid**: do not recommend.
7. **Naming and fxmanifest.** `stream/<ped>_<pack>.ymt`, `<ped>_<pack>^jbib_000_u.ydd`, `…^jbib_diff_000_a_uni.ytd`, props `<ped>_p_<pack>^p_head_000.ydd` + `…^p_head_diff_000_a.ytd`; lowercase, no spaces, contiguous from 000, unique pack name. Metas in `files {}` plus `data_file 'SHOP_PED_APPAREL_META_FILE'` (and `PED_FIRST_PERSON_ALTERNATE_DATA` / `ALTERNATE_VARIATIONS_FILE` when used). Full table: `addon-pack-naming-and-manifest.md`.
8. **Appearance script.** Add-on items appear at the end of each category with no registration. Blacklists and job outfits use absolute numbers that shift with build and `ensure` order; illenium-appearance's blacklist is a client-side filter only (`appearance-integration.md`).
9. **Test.** Checker, then the local test server: start the pack before joining, check every variant, poses, LODs, first person, vehicles.

## Checks

- `py -3 -I scripts/check_clothing_resource.py <resource or folder>` — read-only, standard library: names, manifest ↔ meta ↔ YMT ↔ files, drawable/texture pairing, `_u`↔`uni` / `_r`↔`whi`, letters, numbering, 128/256 counts, RSC7 memory (16/48 MiB), escrow, cross-pack collisions. It cannot read texture formats, weights or YMT contents. Once the user agrees to this skill, run it directly.
- Unit tests: `py -3 -I scripts/test_check_clothing_resource.py`.
- Acceptance: starts without errors; right slot; every variant resolves; no pink, checkerboard, holes, wrong skin tint or bad clipping in walk, run, crouch, sit and arms-raised poses; LODs coherent; same after restart and reconnect.

Report ped, slot id, pack name, drawable/texture numbers seen in the menu, build tested, and what was not tested.

## Common mistakes

| Symptom | Likely cause | Fix |
|---|---|---|
| Works locally, nothing on the live server | key lacks the clothing-streaming perk | user checks their tier; do not push a purchase |
| Nothing shows at all | YMT / meta `fullDlcName` / file prefix differ, uppercase, missing `data_file`, YMT slot budget, another pack with the same name | run the checker; one YMT per gender |
| Item invisible | not rigged / no vertex groups, top drawable dictionary not exported, backfaces | re-import with external skeleton; Backface Culling on |
| Stretching or parts flying off | bad weights, unweighted vertices, more than 4 influences | re-transfer, smooth, pose-test on a real clip |
| See-through arms or torso with a top | matching arms (uppr) not selected | pair an arms value per top |
| Pink or checkerboard | missing diffuse / embedded normal or spec | embed normal+spec, diffuse as YTD |
| Pants look like skin | `_r`/`_u` vs `whi`/`uni` mismatch | checker SKIN_MISMATCH |
| Green/purple blocks on dark fabric | BC1 compression | BC7 |
| Hat doesn't hide hair | hair lacks `MH_Hair_Scale`, hair id < 36, creaturemetadata missing or not referenced | hair scale on the prop; test hair ≥ 36 |
| Heels sink or float | heel value untuned, creaturemetadata missing | grzyClothTool EnableHighHeels, 0.1 steps |
| Crash while loading packs | YMT slots, shop-meta 65,520, TxdStore, alternate-variation caps, oversized textures | `addon-pack-naming-and-manifest.md` §6 |
| Cloth piece falls away or crashes | unpinned top row in the YLD | pin the top row |
| Wrong number in the menu | menus differ; numbers shift with build/ensure | read numbers on the test server |

## References

- `references/clothing-step-by-step.md` — click path: CodeWalker export, fitting, weights, DDS, vertex colours, LODs, export.
- `references/addon-pack-naming-and-manifest.md` — entitlement, file names, replacement, meta, fxmanifest, limits, build/Enhanced, test.
- `references/components-props-and-flags.md` — ids, props, YMT fields, ePedCompFlags, hair hiding, first person, female, YMT tools.
- `references/cloth-physics-and-extras.md` — YLD, UVs, vertex colours, compression, garment creation, weights, Sollumz LODs.
- `references/appearance-integration.md` — illenium-appearance blacklist and config, shifting numbers.
- `references/sollumz-clothing.md` (diagnostic order), `references/video-study.md` (sources).
- Shoes: `blender-shoe-modeling` → `gta-feet-component.md`. Peds/skins: `fivem-ped-character`. Final gate: `fivem-asset-acceptance`.

## Boundaries

Use only files the user may modify. Never decrypt escrowed assets or bypass entitlements. Ask before live Blender or FiveM MCP actions, before installing tools, and before touching server files. Recommend free tools only; name paid ones as paid.
