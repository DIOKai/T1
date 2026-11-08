---
name: fivem-vehicle-livery
description: Use when designing, painting or fixing a livery (decals, stripes, agency markings) for a GTA V / FiveM car - making a UV1 livery template, choosing _sign_N texture liveries vs VMT_LIVERY_MOD livery yfts vs a baked body texture, police / sheriff / state / federal livery design, exporting DDS, putting it into the ytd or livery yft, and fixing liveries that do not show, look blurry, read backwards, appear on one side only, keep the old design or show NULL names. Also for 涂装, 警车涂装, 车身贴花, 拉花, livery 模板, 涂装不显示, 涂装模糊, 换涂装, sign_1. Meta files (FLAG_HAS_LIVERY, carcols kits) live in fivem-vehicle-mod.
---

# FiveM vehicle liveries

A GTA livery is a second texture drawn over the paint. Paint shaders `vehicle_paint3`…`9` read it through **`DiffuseSampler2` on UV channel 1** ("UVMap 1" in Sollumz); transparent pixels let the spawn colour show. `vehicle_paint1/2` have no livery layer. Roof liveries are a separate texture (`vehicle_paint3_lvr`, `DiffuseSampler3`). Almost every livery bug is a name mismatch, a missing layer, or art placed on a UV island that is rotated or mirrored. This skill owns the design and texture side; meta files belong to `fivem-vehicle-mod` (`references/modkits-liveries-sirens.md`, `police-emergency.md`).

Ask first (CLAUDE.md): Blender work goes through the `blender` MCP; installing texconv; pairing with `branding`, `color-theory`, `typography`, `texture-workflow`. The two scripts are local and only read files — run them once the user agrees to this skill. Free tools only: GIMP, Krita, Inkscape, paint.net, Blender + Sollumz, CodeWalker, texconv. Photoshop and ZModeler 3 are paid — never required.

## 1. Inspect the car

`py -3 scripts/check_livery.py <resource or [vehicles] folder>` — reads binary yft/ytd (Legacy RSC7), XML exports and the meta files. It reports which texture the livery shader wants, whether it exists, `_sign_N` vs `FLAG_HAS_LIVERY`, LODs without the livery layer, VMT_LIVERY_MOD parts, missing `AddTextEntry` labels, size/format/mips, `+hi.ytd` duplicates, leftovers like "Untitled design". Exit 1 = errors. It cannot judge the artwork.

## 2. Pick the method

| Method | How it works | Use when |
|---|---|---|
| **A** `_sign_N` + `FLAG_HAS_LIVERY` | Shader points at `<prefix>_sign_1`; the ytd holds `_sign_1…_N` (≤ 30); livery k shows `_sign_(k+1)` | The car already has a body template and `_sign_1`; simple fleets |
| **B** `VMT_LIVERY_MOD` livery yft | One tiny `<model>_liveryN.yft` per livery: dummy quad + embedded texture + `vehicle_paint3`; fitting mod 48 swaps the body's livery layer. All 2023–25 vanilla police cars use this, with no `FLAG_HAS_LIVERY` | Department fleets that grow, > 30 liveries, mod-based menus |
| **C** baked | Design painted into the body's main diffuse (vanilla `firetruk`) | One fixed design, never switched |

Car with only `vehicle_paint1/2`: unwrap UVMap 1 and switch the body to `vehicle_paint3` first. Details and vanilla evidence: `references/technical-methods.md`.

## 3. Template

`py -3 scripts/livery_template.py <car>.yft.xml --size 2048 --checker` (CodeWalker → Export XML). Writes a PNG/SVG template (red = driver side x < 0, blue = passenger, green = roof/hood/bumpers; yellow arrow = car front, white = up, `M` = mirrored island), an orientation checker texture, and a report: rotated or mirrored islands, left/right islands sharing pixels, UVs outside 0..1, px/cm, LODs without the layer. `--sampler 3` = roof livery. Blender route (Export UV Layout on UVMap 1): `references/template-and-painting.md`.

**Test orientation before painting**: put the checker texture in as the livery and look at the car. Backwards letters = mirrored island; upside down = rotated (vanilla polgauntlet's passenger side is 180°). Fix it in the art, per island.

## 4. Design

Layer file (XCF/KRA/PDN): locked template → optional base colour → stripes → text → badges → hidden reference/guides. Design at 4096, keep text editable, scale badges once.
- Text and badges use **only the server's fictional agencies**: LSPD, LSCSO, BCSO, RCSO, SASP, SAST, FIB, FFRB, NOOSE, FCBA, LSPA. No real agency names, badges, state seals, flags; no real car makes or models (GTA brands only).
- Never flip text when copying one side to the other — re-type or rotate it.
- Legibility: ≈ 4 px/cm at 2048 on a full-body template; keep letters ≥ ~40 px tall, fine print on flat, unstretched panels; roof numbers big and oriented for a helicopter.
- Leave the body transparent where the spawn colour should show; painted areas look flat and lighter in game.
Conventions (US patrol, sheriff, state, Battenburg, federal, fire chevrons, mirrored hood text): `references/design-guide.md`.

## 5. Export

Hide guides, merge, export **2048×2048 BC3/DXT5 with full mipmaps** (GIMP, paint.net or texconv). DXT1 only without transparency; 4096 only for a hero car; never uncompressed. Power of two. Paint 2–4 px past island edges.

| Size | px/cm (full-body template) | DXT5 memory with mips |
|---|---|---|
| 1024 | ≈ 2.0 | ≈ 1.3 MiB |
| 2048 | ≈ 4.0 | ≈ 5.3 MiB |
| 4096 | ≈ 7.9 | ≈ 21.3 MiB (A8R8G8B8 ≈ 85 MiB) |

Do not use the "set mipmaps to 1" blur fix — it shimmers at distance. `references/export-and-packaging.md`.

## 6. Package

- **A**: CodeWalker → replace/add `<prefix>_sign_N` in `<car>.ytd` with the exact name; also in `<car>+hi.ytd` if it has the same sign. Back up; `ori\` stays untouched.
- **B**: copy a livery-yft layout, rename texture + DDS + `DiffuseSampler2` to `<model>_liveryN`, compile in CodeWalker.
- Meta (`FLAG_HAS_LIVERY`, kit with `VMT_LIVERY_MOD`, carvariations `<kits>`, job config `livery = N`) → `fivem-vehicle-mod`. Every `liveryNames` / `modShopLabel` key needs `AddTextEntry`.
- Someone else's car: their textures stay 1:1 — report oversize, don't shrink unless the user asks.

## 7. Test and check

Dev server: `SetVehicleLivery(veh, i)` (A) or `SetVehicleModKit(veh, 0)` + `SetVehicleMod(veh, 48, i, false)` (B). Check every index, both sides, roof from above, hood/trunk, walking away (LODs), day/night, each spawn colour, extras, dirt. Rerun `check_livery.py`.

## Common mistakes

| Symptom | Cause → fix |
|---|---|
| Livery invisible | Texture name ≠ sampler name, wrong ytd, paint1/2 body, flag missing → match the name exactly |
| Can't switch liveries | No `FLAG_HAS_LIVERY`, only `_sign_1`, numbering gap; menu uses SetVehicleLivery on a mod-livery car |
| Text backwards / upside down | Mirrored or rotated island; text flipped when copying a side |
| Blurry | Small texture, tiny text, rescaled badges, texture budget full (4K/uncompressed) → 2048 DXT5 from a 4096 design |
| Old design still shows | Same sign in `+hi.ytd` → replace both |
| Vanishes at distance | Medium/Low LOD lacks paint3 + UV1 |
| Menu shows NULL | No `AddTextEntry` for the label |
| Flat "primer" look | Livery covers the paint → keep body transparent |

More symptoms and the user's own server findings: `references/troubleshooting.md`.

## References

- `references/technical-methods.md` — shaders, samplers, UV1, methods A/B/C with vanilla evidence, livery names, roof liveries, formats.
- `references/template-and-painting.md` — template script, Blender export, orientation and mirroring, checker test, stretch/bleed, layer file, projection painting.
- `references/design-guide.md` — fictional agencies, patterns, legibility table, colours in game.
- `references/export-and-packaging.md` — DDS settings and tools, ytd/livery-yft packaging, 1:1 rule, testing natives and checklist.
- `references/troubleshooting.md` — symptom table with checker codes; findings on the user's server.
- `references/sources.md` — vanilla files, docs, videos, what is unverified.
- `scripts/livery_template.py`, `scripts/check_livery.py` (+ `test_*.py`, run `py -3 -I <file>`).
