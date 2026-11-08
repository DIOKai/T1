# LODs, textures, budgets (measured)

## Three different distances

1. **Drawable LOD distances** inside the YDR/YFT (LodDistHigh/Med/Low/Vlow): when the model swaps High → Medium → Low. 9998 = no switch (single-LOD drawables). Sollumz LOD panel (Shift+V preview), `Sollumz Tools > Drawable > LOD Tools` can decimate and extract levels.
2. **Archetype lodDist** (ytyp): the distance at which the object unloads. Plus **hdTextureDist**: when `+hi.ytd` textures load. Sollumz defaults are lodDist 200 / hdTextureDist 100 (`ytyp.py`) — leaving them is a sign nobody tuned the prop.
3. **Entity lodDist** (ymap): override, -1 = use archetype. Parent/child LOD chains (HD → LOD → SLOD, `LOD in Parented YMAP`, ChildLodDist) are only for big landmark pieces (Cfx part 6; Stumpy Mason m6H6tBL3CQ8 [15:34]). A single placed prop uses LOD level ORPHANHD + archetype lodDist.

If the drawable switches to Medium farther away than the archetype lodDist, Medium is never seen (checker `LOD_SWITCH_BEYOND_UNLOAD`).

## Vanilla Legacy props (CodeWalker.Core, user's own G: install, 2026-11-08)

| Prop (size) | asset | archetype lodDist | H→M switch | tris High / Med / Low | textures |
|---|---|---|---|---|---|
| prop_cs_ciggy_01 (0.09 m) | ydr | 20 | single | 64 | 128–256 DXT1 |
| prop_cs_burger_01 (0.17 m) | ydr | 10 | single | 300 | 512×256 DXT1 + 256² DXT5 |
| p_amb_coffeecup_01 | ydr | 30 | 10 m | 144 / 58 | 256² DXT1 |
| prop_npc_phone_02 | ydr | 10 | single | 437 | 512×256 DXT1, 128² A8R8G8B8 |
| prop_amb_beer_bottle | ydr | 100 | single | 226 | 128–256 DXT1 |
| prop_ld_shovel / prop_tool_hammer | ydr | 30 | single | 308 / 322 | ≤512×256 DXT1 |
| prop_roadcone01a (0.9 m) | ydr | 100 | 20 m | 152 / 40 | 256² DXT1 |
| prop_chair_01a (0.95 m) | ydr | 60 | 20 m | 936 / 130 | 256² DXT1 |
| prop_table_06 (1.4 m) | ydr | 60 | 20 m | 620 / 136 | 256² DXT1 |
| prop_patio_heater_01 (2.5 m) | ydr | 60 | 20 m | 726 / 109 | ≤256×512 DXT1 |
| prop_bin_01a | yft | 100 | 25 m | 725 / 152 | ≤256² + 256×4 tint |
| prop_crate_11e | yft | 50 | 15 m | 778 / 202 | 256² |
| prop_fire_hydrant_1 | yft | 100 | 45 m | 1254 / 560 | 256² DXT1 |
| prop_bench_01a (2.4 m) | yft | 120 | 30 / 100 m | 1882 / 924 / 80 | 256×512 DXT1 |
| prop_vend_soda_01 (1.9 m) | yft | 140 | 40 / 80 m | 492 / 194 / 96 | ≤512² DXT1 |
| prop_dumpster_01a | yft | 110 | 50 m | 1098 / 111 | ≤512×256 |
| prop_gas_pump_1a | yft | 120 | 50 m | 2278 / 338 | ≤256×512 |
| prop_streetlight_01 (9.4 m) | yft | 120 | 20 / 70 m | 1022 / 310 / 132 | ≤512², 128×1024 |
| prop_traffic_01a (9.5 m) | yft | 140 | 50 / 65 m | 2126 / 456 / 206 | ≤512² |
| prop_container_05a | yft | 250 | 80 / 160 m | 2116 / 242 / 12 | 1024² DXT1 |
| prop_rub_carwreck_3 (5 m) | yft | 100 | 30 m | 3702 / 1102 | ≤512² |
| prop_tree_birch_02 (12 m) | ydr | 260 | 50 m | 5298 / 1630 | ≤1024² |
| prop_ferris_car_01 | ydr | 60 | single | 5321 | ≤1024×512 |
| apa_mp_h_stn_sofacorn_05 (MLO sofa) | ydr | 30 | single | 4047 | ≤512² |
| apa_mp_h_lit_lamptable_02 (MLO lamp) | ydr | 30 | single | 1372 | ≤256², 1 light |
| prop_tv_flat_01 | ydr | 20 | single | 386 | 512×256 A8R8G8B8 screen |

Summary by class:

| Class | High tris | LODs | lodDist | textures | collision |
|---|---|---|---|---|---|
| hand-held | 60–450 | High only | 10–30 | 128–512 px | one Bound Box |
| small world prop | 150–800 | + Med 25–30% at 10–25 m | 50–100 | 256 | box(es) |
| furniture / street furniture | 600–1,900 | + Med 15–50% at 20–30 m | 60–120 | 256–512 | 5–20 boxes/cylinders |
| large street prop | 1,000–2,300 | + Med (+ Low) at 20–50 / 65–100 m | 110–140 | ≤512 | boxes + small poly |
| big / hero | 2,100–5,300 | 2–3 levels | 100–260 | ≤1024 | boxes / small BVH |
| MLO furniture | 1,300–4,000 | High only | 30 | ≤512 | boxes, Static flag |

The "rule of thumb" in `free-3d-assets/references/to-gta.md` (hand-held 300–2,000, furniture 1,000–5,000) is far above what Rockstar shipped; use this table. Tutor values for drawable switch distances (ook_3D c8gAgKEFDtw: High 50–100, Medium 150; Stumpy Mason 50/100/150) are much farther than vanilla 15–50 m — fine for hero props, wasteful for clutter.

## Textures

- 256² is the norm; 512² for large faces; 1024² only on container, tree, ferris car. No 2048/4096 on any measured prop. Sollumz FAQ allows up to 2048.
- DXT1 opaque, DXT5 alpha, ATI2/BC5 for some normals, A8R8G8B8 only for 256×4 tint palettes and a TV screen. Every texture has a full mip chain (7 levels at 256²).
- Memory (RSC header): hand props 8–40 KB virtual + 0–350 KB physical; street props 40–380 KB + 100–770 KB; container 256 KB + 3 MB. FXServer warns over 16 MiB and says over 48 MiB "WILL lead to streaming issues" (ResourceStreamComponent.cpp). One uncompressed 2048² texture with mips is 21 MiB on its own.
- The user's `wood_table` (2048² A8R8G8B8, 32 MiB) and `wood_table_v2` (two of them, 64 MiB) are the anti-example; vanilla prop_table_06 uses one 256² DXT1 (128 KB). Report, do not re-compress without asking.

## Measuring a reference yourself

CodeWalker (free): RPF Explorer → find the vanilla prop → view model (LOD slider, collision view) or export XML. Or extract the `.ydr/.ytd/.ytyp` and run `py -3 -I scripts/rsc_probe.py <files>`; it reads the same numbers with the Python standard library (layout checked against CodeWalker.Core on prop_table_06, the sofa, the birch tree and prop_pots.ytd).
