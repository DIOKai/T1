# Livery template and painting (free tools)

Tools here are free: Blender + Sollumz, GIMP, Krita, Inkscape, paint.net, CodeWalker. Photoshop and ZModeler 3 are **(paid)** — mentioned only because tutorials use them, never required. Anything that runs in the user's Blender goes through the `blender` MCP — ask first.

## 1. Get the UV1 layout

### Route 1 — `scripts/livery_template.py` (no Blender)
1. CodeWalker → open the car's `.yft` → Export XML (`<car>.yft.xml`). Sollumz XML exports work too.
2. `py -3 scripts/livery_template.py <car>.yft.xml --size 2048 --checker`
3. Output: `<car>_template.png/.svg`, `<car>_checker.png`, and a report.
   - Red = driver side (x < 0), blue = passenger side, green = roof/hood/trunk/bumpers. Sides are decided per triangle by panel direction, because a body unwrap that runs over the roof is one connected UV island.
   - Yellow arrow = toward the car's front; white arrow = up (vertical panels). Text must be typed so its top follows the white arrow.
   - `M` = mirrored island (normal text appears backwards on the car).
   - The report lists rotated islands ("字要转 180°"), mirrored islands, islands that share pixels (left/right sharing with or without a mirror), UVs outside 0..1, px/cm per side, and LODs without the livery layer.
   - `--sampler 3` = roof livery template (separate texture). `--lod med` = check the Medium LOD layout.
4. Tested on vanilla polgauntlet (passenger side rotated 180°, not mirrored, 4.0 px/cm at 2048), police (door strips share pixels left/right without mirror), tornado5 (body sides share pixels and one side is mirrored — symmetric art only), and the user's shelby20pd and 23DChargerHenPEpd (110 MB XML, 3 s).

### Route 2 — Blender + Sollumz (verified sources)
1. Import the `.yft` with Sollumz (Sollumz 2.9 imports binary yft or CodeWalker XML).
2. Find the livery materials: `vehicle_paint3/4/…` with `DiffuseSampler2`. Their UVs on **UVMap 1** are the template. FueryMloGuy (7q6utSsPZwA 01:52–02:38) sets UV map 1 active on every body part, selects linked faces with L (03:39) and exports (05:44).
3. UV Editor (Edit Mode) → **UV ‣ Export UV Layout**: All UVs (otherwise only faces selected in the viewport), Format PNG/EPS/SVG, Size, Fill Opacity. Only the 0..1 range is exported (Blender manual, UV editing → Export UV Layout). SVG keeps lines sharp; PNG at the livery size.
4. No UV1 unwrap (or a bad one): unwrap the body into UVMap 1 ("project from view or smart UV project", then arrange islands — Radit wrac7MJR0Uk 02:17), set the body materials to `vehicle_paint3`, export with Sollumz, put the livery in the ytd with the **exact** sampler name (07:48). Give every LOD (High/Med/Low) the same UV1 + livery shader, or the livery vanishes at distance. Keep the two sides as separate, non-overlapping, non-mirrored islands, so each side can carry its own text.

ZModeler 3 can render templates too (paid; rxMCWoEc-1g, F9CPbEhGB5M, B6ozIUFIXT4) — note only.

## 2. Orientation: the classic mistake

- The two sides are **not always mirrored the same way**. Vanilla polgauntlet: driver side upright, passenger side **rotated 180°** (its "911" sits upside down in the texture); roof number and trunk number rotated 90° (verified with the script and the vanilla texture). shelby20pd: both sides upright but facing opposite directions.
- Copying one side to the other: duplicate + flip horizontally works for **shapes**; **text must never be flipped** — re-type it or rotate it (0JALZnODuag 12:01 flips the group then re-places text; 0eCBJCMn_Jg 11:41 flips only the stripe; HK Works c6vuOk4SOxA 02:52 "Yes, it's going to be backwards").
- Exception: a truly mirrored island (`M` in the template) needs mirrored text to read correctly — or fix the island in Blender.
- Left and right sharing the same pixels (vanilla police, tornado5): with no mirror, text reads on both sides but is identical, and arrows/swooshes point forward on one side and backward on the other; with one side mirrored, text reads backwards on that side → put only symmetric, text-free art there.
- Reverse lettering on purpose only for front panels read in mirrors (ambulance hood — vanilla `ambulance_sign_1` has a mirrored "AMBULANCE").

### Checker test before painting
Convert `<car>_checker.png` to DDS (export-and-packaging.md), load it as `_sign_1` (or as the livery-yft texture) and look at the car in game, CodeWalker or Blender:
- cell names (A1…H8) tell you which template area lands where;
- a letter that reads backwards → mirrored island; upside down → rotated island;
- every yellow arrow must point to the car's front;
- red must be on the driver side.
Fix orientation **in the template** (rotate/flip your art), not in the model, unless you are rebuilding the unwrap.

## 3. Stretch, seams, unused areas

- Curved panels (bumpers, flares, hood edges) are stretched in UV1 — on the checker, squares become rectangles. Keep text off stretched areas and seams; "watch the body lines" (JkdthK3tHgo 03:45); keep lettering on the used (coloured) area, not on the black unused part (0eCBJCMn_Jg 23:57).
- Black/unused template areas never show, so shapes may overrun into them (0eCBJCMn_Jg 10:39; Gh1TLTZaxOc 12:46; biOmm5KPsFU 07:00).
- Bleed: paint 2–4 px past island edges (more at 4096) so lower mips don't show a hairline of paint colour along seams (standard practice; Blender bake Margin does the same: "A margin is generated around UV islands … to avoid seam discontinuities" — Blender manual, Render Baking). BigPilotGuy controls bleed near edges (U8vTQpWMn9Q 14:36–15:37).

## 4. Layer file (XCF / KRA / PDN — all free)

Bottom → top (consensus of 0JALZnODuag, 0eCBJCMn_Jg, JkdthK3tHgo, dgVnz0Inf78):
1. `template` — UV wireframe, locked; never paint on it ("a lot of people ruin templates", JkdthK3tHgo 05:09).
2. `base` — body colour fill **only** if the livery must force a colour. For alpha liveries (DXT5) leave it empty so the spawn paint shows.
3. `stripes / blocks` — vector-like shapes. GIMP: Paths + Edit ‣ Stroke Path (0JALZnODuag 02:25–04:50); paint.net line tool (0eCBJCMn_Jg 06:13); close shapes before filling (10:18). Inkscape is best for crisp stripes and text — export PNG at the livery size.
4. `text` — agency name, "SHERIFF", unit numbers as editable text layers, rotated per island.
5. `badges` — place from a large original (≥ 500×500 px, 0JALZnODuag 06:11) and scale **once**; repeated scaling blurs (07:13–07:53).
6. `reference` photo at ~50 % opacity for tracing (01:22) — hidden on export.
7. `guides` — panel names, FRONT arrows, L/R labels (or the script's template on top at low opacity) — hidden on export.

Keep every element on its own layer (BigPilotGuy 07:38) — moving one stripe later is common. Export: hide template/reference/guides, merge visible, export (export-and-packaging.md).

Work at 4096 (or 2× the target) and export 2048: TEG designs at 4K and ships 2K (0JALZnODuag 00:21, 17:19); Xclusive Designs 4096 → 2048 (0eCBJCMn_Jg 29:44); Patrol One upsizes 2048 → 4096 to work (WsFXPXmIIDw 02:03).

## 5. Decals across seams in Blender (free)

- Texture Paint with brush **Stencil** mapping: "the ideal option for stamping textures for projection painting … projecting the texture from the camera space on the mesh" (Blender manual, brush texture). Paint slot mode **Single Image** paints on "the active UV layer" — pick UVMap 1 (Blender manual, texture slots).
- Or model decals/text as planes (or a decal projector), then **bake** onto an image on UVMap 1: target = "the image data-block associated with the active and selected Image Texture node"; Emit / Diffuse colour only; Margin Extend (Blender manual, Cycles baking). That the bake writes to the active UV map in the list is community knowledge — verify in Blender.
- The Walejaw 3D video on Blender 4.0 liveries (VYnIsCJm1Q4, "when Shrinkwrap isn't the answer") was not transcribed (HTTP 429); the Blender steps above are from the manual only (unverified as a livery workflow).
- Pair with `texture-workflow` (bake/decals) — ask first; Blender work runs in the user's Blender via the `blender` MCP.
