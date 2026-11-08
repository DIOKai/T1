# Car modeling workflow (subdivision, step by step)

Citations: `KG<part> <videoId> mm:ss` = Kevin Gallant series, `JY` = JOYCE 3D (Rs_w0CSDWJ8), "(from frames)" = read off the video image. Video list in `sources.md`.

Contents: 1. Reference and blueprint setup · 2. Blockout and base-mesh strategy · 3. Topology and edge-flow rules (KG4, KG6, KG7) · 4. Subdivision, support loops and panel lines · 5. Matcap and reflection checks · 6. Component recipes · 7. Materials, lighting and rendering (KG20 U40IczuCI8M) · 8. Common mistakes the tutors warn about

**Blender version note.** KG uses 2.7x keys. Modern equivalents:

| KG (2.7x) | Blender 4.x / 5.x |
|---|---|
| right-click select | left-click select |
| Shift+Alt+RMB | Alt+click edge loop |
| W specials menu | right-click context menu |
| Remove Doubles | Merge by Distance (M) |
| Ctrl+N recalc normals | Shift+N |
| layers | collections |
| Blender Internal | EEVEE / Cycles |
| Edge Split modifier | Smooth by Angle modifier (4.1+) or Edge Split |
| N-panel "Background Images" | Image Empties / Reference images |

---

## 1. Reference and blueprint setup

1. **KG2 yD4TTW2ke5M** gives the blueprint alignment method.
   - Put one blueprint sheet (side, top, front, rear) in each orthographic view. Background images only show in **orthographic**, so toggle with numpad 5 (3:49-4:12).
   - Rotate the top view image by exactly **-90°** in the R field (9:30).
   - **Use the default cube as an alignment gauge** (5:27-11:36). In the side view, move the cube's front and back faces to the wheel/bumper extremes and its top face to the roof. That fixes length and height. Then line up the top, front and rear images to the cube. Width can only be set from the top or front view, so scale the cube on X (S X) to match the body width (10:20).
   - Opposite views are Ctrl+numpad (Ctrl+1 rear, Ctrl+3 left, Ctrl+7 bottom) (11:36).
2. **Warning: blueprints never agree perfectly between views** (KG2 12:24). Eyeball the differences and keep **real photos** open on a second monitor. KG looks up close-up photos for every tricky part: trunk (KG10 8:38), side window trim (KG11 17:38), tail lights (KG13 0:24), lip (KG12 19:52).
3. **JY (from frames, 0:20-3:40):** each view is an image empty scaled to a reference cube. Together they form an open box of planes around the origin, and the blueprint comes from the-blueprints.com. Front and rear images are set to display "front side only" so they don't overlap in X-ray (JY 27:51). The add-ons **LoopTools** and **Modifier Tools** are enabled first (JY 3:08; on-screen caption at 3:00).
4. **KS (from frames, 0:40-1:30):** photos of the real helicopter, not line blueprints, are set up as image planes in 3D: side, front and top. Photo planes stay visible all session and are re-shown next to whichever part is being built.

**bpy:** `bpy.ops.object.empty_add(type='IMAGE')`, then set `empty_display_size`, `empty_image_offset`, `show_empty_image_orthographic=True`, `show_empty_image_perspective=False`, `empty_image_side='FRONT'`. Add a 1×1×1 gauge cube and scale the empties to it.

---

## 2. Blockout and base-mesh strategy

There are two proven approaches.

**A. KG: grow from the roof outward, panel by panel**
1. Add a plane in the top view, add a **Mirror modifier**, and enable **Clipping** (KG3 2:20-3:50).
2. Shape the roof with 3 loop cuts (Ctrl+R, mouse-wheel to set the count) (KG3 5:07).
3. Extrude edges down to the A, B and C pillars (KG4).
4. Extrude the door, rear fender and front fender as separate "sections", split along real panel lines (KG6 13:55: "splitting this car up into manageable sections… according to the panel lines").
5. Hood (KG7), then bumpers (KG8).
6. KG calls the result the "**low poly base mesh**": about 1,000 vertices before Subdivision (KG9 3:29).

**B. JY: trace character lines with edges, then fill (from frames)**
1. Merge a plane to **a single vertex** and extrude it along the side profile line. Subdivide that edge to get evenly spaced points (JY 3:08-3:33).
2. Move the points so they follow the body lines in all three views ("align them to match the flow of the lines in the reference images", 3:33).
3. Fill the surface between the traced lines. Cut new edges with the **Knife (K)** and with **Vertex Connect Path (J)** (frames 7:38-9:40). **K then C** cuts straight through (10:00).
4. Leave the wheel-arch openings early: "to make room for the tires" (5:05).

**Rules from both tutors**
- Fix the edge budget at the low-poly stage. KG adds edges in the base mesh **wherever a panel line or accent line will be cut later**, so the cuts become simple loop cuts (KG10 0:48).
- Matching edge counts matter. When two surfaces meet (window frame and roof), they need the **same number of vertices on both sides**. Otherwise you get triangles (KG11 6:23, 8:32).
- **Straighten an edge row:** scale on one axis and type 0 (S Z 0, S Y 0, S X 0). KG uses this for pillar bottoms, bumper edges and markers (KG4 13:40, KG8 1:35).
- **Edge slide (G G)** moves geometry without changing the shape. Use it to make faces evenly sized (KG4 4:14, KG4 9:48).
- **Hide what you aren't working on.** Box-select and press H, then Alt+H to unhide (KG8 17:32). Or duplicate the border (Shift+D, right-click to cancel the move), separate it with **P → Selection**, then Ctrl+I and H to work on only that piece (KG11 1:36).
- **Back up before destructive steps:** Shift+D a copy to another layer/collection before applying modifiers (KG9 2:34, KG17 0:49).
- Undo in Edit Mode. Ctrl+Z in Object Mode throws away large chunks of edit-mode work (KG6 10:54).
- **JY: Flatten (LoopTools)** levels surfaces and straightens edge flow. **Shrink/Fatten (Alt+S)** pushes points along normals, for example to make a surface bulge (JY 16:04-17:11). Where density gets too high, cut and dissolve edges to reduce it (JY 26:26).
- Keep normals consistent. Blue face-orientation overlay means correct, red means flipped; recalculate with Shift+N (JY 48:13; KG uses Ctrl+N in 2.7x, KG9 22:46).

---

## 3. Topology and edge-flow rules (KG4, KG6, KG7)

- Use **quads in an even "grid-square" pattern** (KG6 8:42: "if you learn anything from this video just remember grid squares"). Stretched trapezoids distort when moved and make curves deform badly (KG6 14:50).
- **Keep density uniform across the body.** Add density only where detail needs it, such as pillars (KG6 9:10). A low-poly base should be "as minimalist as possible" (KG7 3:43).
- **Triangles break loop cuts.** Ctrl+R stops at a triangle, and so does the later panel-line work (KG5 8:04, KG10 23:33). Two ways to fix them:
  - **Two-triangle trick:** fill a second triangle next to the first. Then select the 4 vertices of the two triangles and press F, and Blender replaces them with one quad (KG6 1:38-2:27).
  - **Knife plus merge:** Knife (K) from the triangle tip across the next edge, then **Alt+M merge at last** to carry the loop through (KG10 24:21-25:08).
- **Where triangles are acceptable:** hide them on flat or barely visible areas (JY 60:42). The forum consensus agrees: a triangle inside a perfectly flat surface is harmless. KG accepts small triangles where a vent fades into the hood (KG7 13:08).
- **Wheel arches:** a circle cut into a grid always stretches where it meets the vertical and horizontal flow. Minimize that stretching, but don't remove the crossing loops (KG6 4:37-8:17).
- **Holes and vents:** always put **one edge loop all the way around a cutout**. Either inset (I) the face, or extrude and scale in, before deleting the hole face. This keeps Subdivision from pulling the surrounding surface into the hole (KG7 24:15-26:17, KG8 5:20, KG8 14:32). The same loop goes around the wheel well (extrude, scale, align) (KG8 14:32, KG8 23:24).
- **Choosing which side gets the extra loop:** put the support loop on the side where it ends cleanly. For example, the roof panel line gets its loop on the roof side so it doesn't run down the A-pillar (KG10 17:49).

---

## 4. Subdivision, support loops and panel lines

- **Subdivision Surface:** Viewport level **2**, Render level **3** (or 4 for close-ups). The faceting you see at level 2 disappears at level 3 (KG10 15:36-16:29). For scale: about 1k verts becomes 3.5k at level 1 and about 14k at level 2 (KG9 3:54). Toggle the modifier's eye icon off while editing tight areas (KG9 12:02).
- **Sharpening:** sharpen an edge by adding a loop close to it, or by beveling the edge (Ctrl+B) before applying Subdivision (KG9 18:37, KG18 12:31, KG18 18:01).

**Panel-line recipe (KG10 uzC3Q-xkeIA 0:48-5:23 and 9:38-10:50)**
1. Ctrl+R a loop **very close to** the panel line position.
2. Ctrl+R again with **2 cuts** (scroll once) so there are two **reinforcement edges**. These are the outer boundaries that keep each panel sharp.
3. Add **one more loop in the middle**. This is the divider.
4. Select the middle loop and push it slightly **inward**, along an axis or by hand to follow the pillar angle (KG10 17:14).
5. **Ctrl+B** bevel it slightly, then **X → Faces** to delete the strip. The panels are now separate islands; L selects a whole panel.
6. Don't fuss over making every gap the same width; the difference is hard to see (KG10 19:06).

- **L-shaped panel lines (bumper/trunk corner) (KG10 11:09-12:56, 20:25):** delete the corner face, add loops that stop at that face, extrude a vertex at an angle, fill the corner faces and refill the quad. The loop then turns the corner without running through the whole car.
- **Thickness at the gaps:** select the border edges, extrude them inward (E, then move along the normal or axis) and add a support loop. This makes panels look like metal sheet, not a paper shell (KG12 5:24, KG16 2:03).
- **Wheel wells:** extrude the arch border edges inward 2-3 times, adding a sharpening loop each time (KG16 2:03-2:51).
- **JY variant, non-destructive (JY 22:31, 62:29-65:19):**
  - **Bevel weight** the border lines before separating panels.
  - Run **Select Sharp Edges** to mark sharp edges.
  - Add a **Bevel modifier with Limit Method = Weight**, then Subdivision (Ctrl+3).
  - Gaps at seams come from unweighted edges, so fix their weights.
  - The **Mirror** modifier must be **first in the stack**. Raise the **merge distance** to stop flashing at the seam (JY 65:40).
  - **Ctrl+L → Copy Modifiers** to other objects; select the targets first (JY 65:40).
  - **Symmetrize** to mirror one edited side onto the other (JY 66:33).
- **Web point (Ebal Studios):** make trims and cuts **after** the large surface is final. Trims on a low-poly surface distort curvature most around door handles, and once trims are in you can't go back to the base mesh. Polycount advice says the same: model the whole body without cuts, subdivide once, then cut.

---

## 5. Matcap and reflection checks

- **Viewport Shading → MatCap.** Pick a very shiny, car-paint or chrome-like matcap and orbit the model. Bumps, dents and pinches show up as wobbling highlights (KG12 UE239-dIy5Y 1:40-2:52, KG16 6:09, KG17 1:39). Iterate: "these matcaps really help you see what's wrong with your model" (KG12 16:40). KG found a door-handle inset bending the reflection with the "reflection blue" matcap (KG15 3:27).
- Use Shift+Z (2.7x rendered preview) with a single Sun light to check panel gaps (KG10 5:47, KG12 6:18).
- KG recommends a more advanced subdivision workflow video for adding depth with smooth reflections: youtube.com/watch?v=3rlMzsBWtPY (KG12 0:24, linked in the description). Not verified.
- **Web point:** the targets are G0 (no gaps), G1 (no creases) and G2 (highlights read as one surface). A polygon cage can't reach true G2. Aim for clean reflection stripes on the big panels: side, roof, bonnet. Place loops evenly or change density gradually, and use the fewest vertices that hold the shape.

---

## 6. Component recipes

**Grille (array + lattice, KG9 HRWYa25jF1s 4:46-13:22)**
1. Model one small tileable cell as a separate object.
2. Array 1 on X with **count about 39**. Array 2 with **Relative Offset (0, -1, 0)** to stack rows.
3. To curve the grid without applying the arrays, add a **Lattice** with resolution **U=5, V=1, W=2**. Add a **Lattice modifier** after the arrays and edit the lattice points.
4. Move both sides' lattice points together so the result stays symmetric, and tuck the grille edges into the bumper.
5. Put a black **"backsplash" plane** behind the grille so the car isn't hollow (KG9 25:33).

**Round headlights (KG9 15:09-19:04)**
1. Cylinder with **12 vertices**, not 32 (set in the Adjust Last Operation panel).
2. Face → extrude → scale in, repeated to build the bezel, lens recess and lens.
3. Add Subdivision, then sharpen with extra loops.

**Tail lights and general light method (KG13 f7JLeAL-CWg description, 6:58-8:12, 22:36-26:14)**
1. Model the **outer housing** (glossy black).
2. Model the **clear coloured lens** as a duplicate of the inner opening, extruded to give it a frame.
3. Model a **clear reverse-light lens** the same way.
4. **Duplicate and shrink the interior pieces** with **Shrink/Fatten (Alt+S)** so they sit behind the lens. These get an **emission** material.
5. A light looks real only when the emitter is visible through a clear lens.
6. Split the lens with the panel-line recipe.
7. KG forgot the **back cover** of the lights. Close the housing.
8. Proportional editing (O, mouse-wheel sets the radius) is handy for gentle reshaping but messy (KG13 14:36).

**Exhaust pipe (curve) and tip (KG14 meBJL9UTijY 1:35-13:42)**
1. Add a Bézier curve. Set **Fill = Full**, raise **Bevel Depth** to the pipe radius and raise **Resolution** to round it. Bend it with the handles under the car.
2. Model the tip separately: inset, extrude back, then cut a round hole into quads.
3. Turn quads into circles with **LoopTools → Circle** (W menu).
4. Scale the circles with **Pivot = Individual Origins**.
5. Delete the faces and join with **LoopTools → Bridge**.

**Antenna, spoiler, mirrors, handles, side markers: "attach to body" trick (KG14 14:11-18:43, KG15)**
1. Model the part as its own object, usually duplicated from body faces.
2. Make a **vertex group** of only the vertices that touch the body, for example "bottom".
3. Add a **Shrinkwrap** modifier with Target = body and **Vertex Group = bottom**.
4. Give the parts that get shrink-wrapped enough edge loops for the modifier to follow (KG16 9:01).
5. Apply modifiers top-down (KG14 18:13).
6. Restart a part when fixing it costs more than redoing it (KG14 24:22).

**Side markers ("lazy" method, KG15 18:38-22:19)**
1. Duplicate body faces, square them with S Y 0 / S Z 0, shrinkwrap them onto the body.
2. Add **Solidify with negative thickness** so the marker pops out just enough.
3. Add **Edge Split at about 70°**.
4. The marker reads through a different material, so there's no need to cut into the bodywork.

**Door handles (KG15 0:52-8:12):** edge-slide existing loops to the handle boundaries, inset (I), extrude in, then make the grip a separate shrink-wrapped piece.

**Mirrors (KG15 8:37-13:26):** start from a cube. Inset the glass faces and extrude them in twice to keep the edge sharp. Model the arm as a separate cube, delete its end faces and shrinkwrap it to the door.

**Windows and trim (KG11 KEjSA-iO3C0)**
1. Extrude the window-opening edges slightly **inward** for depth (0:46).
2. Duplicate and separate the edges as the glass object.
3. Delete the panel-line vertices inside the glass outline and fill.
4. Match the vertex counts on the top and bottom edges. Bevel a single edge to add vertices where needed (4:40).
5. Inset (I) the whole windshield so there is a border. Delete the back faces of the inset (mirror seam).
6. Knife small triangles at the corners so they sharpen without loops running across the glass (13:42-14:30).
7. **Trim:** extrude the edge, extrude it outward on X for depth, and add one reinforcement loop plus an inward-pushed loop for the indent (18:51-22:16).
8. Hide gaps by making the glass slightly larger than the opening (33:24).
9. Separate small window panes from the main glass with the panel-line recipe, without depth (30:53).

**Lip and diffuser (KG12 19:00-28:02):** duplicate the bottom border and build down from it. Rip (V) to separate an edge for depth. Repeated F on a selected edge continues filling along the row (KG12 24:31). LoopTools Bridge also works.

**Wheels (KG18 rumh7P0wRNQ, KG19 TN52oH2WxjU, JY)**
1. Center the wheel photo on the origin. Add a circle with **42 vertices** so vertices land on the spoke centres; KG's 7-spoke rim (KG18 3:08-3:33).
2. Delete everything but one spoke's span. Model **half a spoke** with Pivot = 3D cursor, then mirror and apply.
3. Add an Empty at the origin named "wheel control", **Apply Rotation & Scale** (Ctrl+A), and add an **Array, count 7, Object Offset = empty**. Rotating the empty sets the step. Enable **Merge** and **First/Last** (KG18 8:06-9:55).
4. JY does the same with 5 spokes and **72°** (360 / 5) (JY 70:40).
5. Keep the single spoke low-poly: its count is multiplied by the number of spokes, then again by Subdivision (KG18 5:48).
6. **Spin alternative** (Alt+R / Spin tool): Angle **360**, **Dupli/Duplicate on**, steps = spoke count, about **51.42°** per spoke for 7. Then **Merge by Distance**, which removed 190 duplicate vertices (KG19 1:07-2:57).
7. **Lug nuts:** loop-cut a grid, LoopTools → Circle, rotate each circle straight with Individual Origins, extrude down, scale in, extrude out (KG18 13:50-16:13).

**Tires (KG19 3:20-15:23)**
1. Model **one tread segment** from a tread-pattern image (top view, mirrored). The top and bottom edges must interlock like a puzzle, or the array won't tile.
2. Extrude up the tread faces and shape the cross-section in the front view.
3. Add **Array, Relative Offset about 0.492** (just under 0.5), with Merge and First/Last.
4. Add a **Curve modifier** with a **Bézier circle** as target. Size the circle and the array count so the ring closes.
5. Use **Edge Split**, not Subdivision. Subdivision creates "way too much geometry" (KG19 9:33).
6. Apply in order **Mirror → Array → Curve**.
7. Copy and paste the location from the wheel (N panel, Ctrl+C / Ctrl+V on the field).
8. JY (from frames, 67:20-73:40): the tire is a ring with modifiers.
9. Put the wheel hub and tire into a **collection (M)** and use **Add → Collection Instance** for the other three corners, so edits propagate (JY 73:40).

**Logos and text (KG16 E3xQqNW2jKk 7:03-28:51)**
1. Load the vector logo as a background image. Trace it with a plane using minimal but even geometry, so a shrinkwrap can conform it.
2. Scale it and place it near the body. Add **Shrinkwrap** (target body), then **Solidify**, then **Subdivision**, then **Edge Split at 30°** for crisp corners.
3. **Text:** install a lookalike font in Windows, then Add → Text, align to view, and load the font in the Font tab.
4. Rotate the text and mirror it manually (Ctrl+M) instead of using the Mirror modifier. Text mirrored with the modifier reads backwards.
5. Solidify the text.
6. KG considered a displacement texture and rejected it because it gives ugly shapes.

**Underside and engine bay (KG16 32:40, KG19 16:14):** a plain plane filled from the outline hides the empty interior. KG never models the engine. Not enough for a shipped GTA car: see `engine-bay-and-underbody.md` and `interior.md`.

**Gas cap (KG17 AHbDrcFkCUs 0:49):** make it last, on a copy whose Mirror modifier has been applied, because it is asymmetric.

---

## 7. Materials, lighting and rendering (KG20 U40IczuCI8M)

**Materials**
- Use one material slot per surface type. KG's list (11:03-12:15): car paint, secondary paint, window, trim, clear lens, clear red lens, light emission, brake red, tire, wheel, chrome (lug nuts and exhaust), mirror, and a **"void" black diffuse** behind lights and under the car.
- Set each material's **Viewport Display colour** so slots can be told apart without rendering (7:44).
- To assign: in Edit Mode, select with L, then Assign.
- **Glass:** Transparent BSDF mixed with Glossy, not plain Glass (8:58-9:23). Modern equivalent: Principled with Transmission.
- Node setups are linked in the description: imgur.com/gallery/Ubsqyqc.
- For games or export, use **image textures / PBR** (base colour, metallic, roughness, normal), not procedural Cycles nodes, which don't transfer (13:08-16:25). Unwrap with U → Unwrap (17:39-18:50). KG paints in Substance Painter, which is **paid**; the free route is Blender texture paint.

**Lighting and rendering**
- Lighting is emission planes for studio reflections, plus a Sun, plus an **HDRI** world (Environment Texture). Free HDRIs: Poly Haven, formerly HDRI Haven (22:14-25:23).
- Use **Cycles**. Samples: **128 for preview, 512 for final** to remove fireflies. Turn on **Denoising** (26:09-27:52).
- Compositor: a **Glare** node for headlight glow and **RGB Curves** for the grade (27:52-28:40).

---

## 8. Common mistakes the tutors warn about

- Starting the first car without understanding topology. KG's first car "looked good in edit mode" but broke when smoothed (KG1 0:28).
- Triangles and n-gons on curved panels. They block loop cuts and panel lines (KG10 23:33) and bend reflections. Fix them as described in section 3.
- Uneven or stretched faces, especially at arch and pillar corners (KG4 15:55, KG6).
- Panel lines cut through the base without support loops. Subdivision rounds the panels into "mushy" edges (KG10 3:41, KG15 25:16).
- Blueprint misalignment trusted blindly (KG2 12:24, KG8 2:56). KG found a blueprint line that matched nothing in the photos and ignored it.
- Flipped normals showing up as dark patches after extrude or duplicate. Recalculate them (KG9 22:46, KG11 5:57, KG12 4:31).
- Mirror Clipping turned off by accident. Vertices then cross the centre and leave a seam (KG14 15:22, 22:30).
- Shrinkwrap affecting vertices outside the group (KG15 16:16). The workaround is to apply, then redo the part.
- Too dense a base mesh. Every extra loop makes clean reflections harder (KG7 3:43; Ebal Studios).

---
