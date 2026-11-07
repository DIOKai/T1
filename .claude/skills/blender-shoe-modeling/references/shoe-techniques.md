# Shoe and sneaker modeling techniques

Citations: [P] PixelicaCG KznMWG1QywM, [J] J Derinor NwOR2A3eKjE, [B] Blacknest pEj7T4j_y_0 (from frames), [T] twobidona OGSo28XLkHM, [D] Druu Pl703WrlCnE, [DCT] Durty Cloth Tool docs. Full list in `sources.md`.

## 1. References and the "last"

- Collect **side, top, bottom (sole) and back** photos. Add them as **Shift+A > Image > Reference** and scale and rotate them to the blockout. You can also dock an Image Editor window or use PureRef (P 0:22, 1:53).
- **Build a sculpted base form first.** This plays the role of the shoemaker's *last*. J sculpts the overall volume before modeling any panel, then snaps every panel onto it: "sculpting the base mesh always helps… all I need to worry about is snapping it onto our base mesh" (J 5:17–5:43).
- **Shoes are asymmetric.** Left and right differ, and the inner (medial) side is straighter than the outer side. Mirror only to start. Then turn **X-mirror off** and reshape from a **bottom-view sole reference** (P 9:13–9:37; J 10:53–11:17).

## 2. Blockout from a cube (P 0:22–3:35; J 0:47–1:33)

1. Start from the default cube, Tab into Edit Mode, and squash it. From the side view, extrude faces where the shoe bends (toe spring, instep), then extrude the top twice for the collar.
2. Use **few vertices**, because a Subdivision modifier goes on top. Preview with **Ctrl+1** (P 1:08; J 1:33).
3. Subdivision makes things blobby. Fix it with **support loops (Ctrl+R) close to edges** you want crisp: heel top and bottom, sole edge, toe (P 1:30; J 6:30, 8:27).
4. Sculpt Mode **Grab** to match the side reference (P 1:53).
5. Once the form is right, set Subdivision to 1 and **apply it (Ctrl+A over the modifier)**. This gives an even, dense base for snapping and sculpting (P 3:35).

## 3. Sole, heel and midsole

- **Boot heel, integrated (P 1:08):** extrude the bottom, scale down, extrude and scale again. Add a loop near the top of the heel.
- **Boot heel, separate (P 2:17–3:35):**
  - Select the bottom face row, Shift+D, Esc, P > Selection.
  - Extrude the bottom edges down and add **Solidify placed above Subdivision** in the stack.
  - Flatten the back edge row with **S, 0** (then the axis), and extrude down to the ground.
  - Fill the bottom: Alt-click the loops, Ctrl-deselect the two front edges, then **Bridge Edge Loops**. Add a middle loop and **merge (M)** the end vertices.
  - Crisp the sole edge with Ctrl+R loops.
- **Lip along the sole edge (P 2:17):** Alt-click the bottom face ring, then **Extrude Region > Extrude Along Normals** and drag the yellow handle.
- **Sneaker cup sole with tread (J 1:33–4:31):**
  - Shape the outsole outline from the top/side reference.
  - For circular pivot/tread patterns, place **circles first** and inset them to match the grooves. Connect them to the surrounding mesh with the **Knife (K)** so edge flow stays continuous. J: "having good topology… will make or break your sneaker".
  - **Select every tread face at once and extrude together**, so all grooves have the same depth. One-by-one extrusions end up uneven.
- **Midsole (J 4:31–4:55):** extrude the outer sole ring **up** and align it with the reference. For the **slit/groove** around the midsole, add two loop cuts, push them in, and extrude those faces.

## 4. Upper panels: the core sneaker technique (J 5:17–15:00; P 3:58–4:22)

- **Each leather panel is its own object:** a plane extruded to the panel outline (or faces duplicated off the base with Shift+D, P), **snapped to the base** with face snapping on, then given thickness with **Solidify** and smoothed by Subdivision (J 5:43; P 3:58).
- **Panels stack, they don't intersect.** "The real tricky thing… is layering each panel where they're not intersecting… but sitting right on top of each other." Separate them with **Proportional Editing (O)** or sculpt Grab, and extend a panel slightly **under** its neighbour where it tucks behind, such as the heel counter (J 6:07, 9:19).
- **Toe box:** duplicate the dense base mesh and delete everything except the toe. You need that density later for perforation booleans (J 9:42, 26:11).
- **Mirror workflow (J 7:17–13:14):**
  - Straighten the centre-line vertices first (no V-shape) so the halves merge cleanly.
  - **Copy and mirror before you add support loops.** Mirroring after the loops is "a nightmare and a mess".
  - Duplicate, **Mirror > X Global**, then **snap the mirrored copy back onto the base piece by piece**: side, then front, then odd angles. A shoe is asymmetric, and snapping everything at once from one view scatters the vertices.
  - **Ctrl+J**, merge the centre seam, then **Recalculate Normals Outside**. Mirror plus join flips normals.
  - Only then add support loops.
- **Clean topology: all quads, no triangles** on every panel (J 14:09–15:00). The Modifier Tools add-on helps toggle modifiers quickly (J 8:56).
- **Boot outer layer (P 3:58):** duplicate the faces of the cover areas, separate them, add Mirror, sculpt-Grab them outward from the shoe, then add Solidify on top of the stack.

## 5. Collar, ankle cushion, tongue and heel tab

- **Ankle cushion (J 13:45–15:00):** this was the slowest part for J. Build it piece by piece with snapping (back piece first, then the inward curve), and keep the topology clean.
- **Tongue (J 16:45–19:18):**
  - Start from a simple symmetric shape, then extrude it to full length and curve it back.
  - Tuck the edges **inside** the side panels.
  - Make the padded ribs: knife a cut, straighten it with S 0, **bevel the selected edge rows with extra supporting segments, then scale them inward**. Under Subdivision this gives quilted padding grooves.
  - Tongue flap/label: duplicate the top section of the tongue (J 24:10).
- **Heel tab:** a plane with Subdivision and Solidify, snapped where it should hug, with snapping off where it should stand free (J 19:18).

## 6. Logos

- **Flat logo panel (J 15:27–16:45):** duplicate part of a panel and reshape it to the logo outline, keeping all quads. Mirror and snap it on. To tuck it under the heel panel, **turn snapping off**, because snapping won't let vertices pass behind a surface.
- **3D emblem (J 24:33–25:47):** extrude a cube's points in X-ray along the outline and duplicate segments to finish the shape. Subdivision "crumbles" it without support loops, so either add loops or **drop Subdivision** for small emblems.
- **Label decal (B, from frames, ~27:00):** an image texture with alpha on a separate plane on the tongue, roughness about 0.3.
- **For GTA: put logos in the texture**, and swap real brands for in-game brands, following the user's vehicle-badge rule in LESSONS.

## 7. Eyelets and perforations

- **J method 1 (19:40–21:15):** select vertices, **Vertex Bevel (Ctrl+Shift+B)** to make a ring, and delete the centre. With modifiers **off**, knife a **support loop around the hole** so Subdivision shading stays clean. Round the hole with GG (vertex slide).
- **J method 2 (21:38):** bevel the vertices, then **Inset (I)**, then delete. This gives the support ring directly.
- **P method (4:22–4:45):** don't cut holes. Place a smoothed **torus** with **snap to Face** on so it sticks to the surface. Thin it with **Alt+S** in Edit Mode, duplicate it up the row, then **Ctrl+M, X** to mirror the row to the other side. This is cheap and good for boots.
- **Toe-box perforations (J 26:11–27:54):** use subdivided cubes as cutters, duplicated over the pattern and extruded long enough to pierce the shoe. Run **Bool Tool > Brush Boolean > Difference** on the dense toe copy. Subdivision fails afterwards, so leave it off. Add a **duplicate inner layer** so the holes don't look into an empty shoe.

## 8. Laces

- **P (6:39–8:49):**
  - A scaled-down plane with snapping on, extruded from hole to hole.
  - **Flip normals (Alt+N)** where the faces aren't blue, then add **Solidify**.
  - Grab-sculpt it so it passes through the eyelet. Use **Alt+Q** to switch to the shoe and **push the upper inward under the laces**, because tight laces pull the leather in.
  - Duplicate onto the next holes and delete hidden lace parts underneath.
  - **Knot:** duplicate a lace segment, bend two loops and two tails, then extrude-scale the aglet ends.
- **J (22:38–23:32):** model one lace segment, then copy-paste it for the left side, then the right, and adjust each one. J asks for a faster method.
- **Not from the videos (general Blender):** a Bezier curve with Geometry Bevel depth, or Curve to Mesh in Geometry Nodes, is faster for long laces.

## 9. Stitching

- **Sculpted stitch lines (P 5:28–6:15):** **Crease brush (Shift+C)** with **Stroke > Stabilize Stroke** on when using a mouse. Then run a **larger Crease brush with Ctrl (inverted)** along the same line to sharpen and pronounce the seam. Also add a stitch line close to the panel edges (P 9:37–10:04).
- **Geometry stitches (Array + Curve):**
  1. Model one stitch.
  2. Convert the seam edges to a curve (Separate, then Convert > Curve).
  3. Add Array (Fit Curve) and Curve modifiers.
  - To avoid stretching: **apply scale and rotation on both objects** and put the stitch origin at the curve start (r/blender).
  - B's finished model shows geometry dashed stitches running parallel to every panel edge (B 7:00–36:00, from frames).
- **For GTA: never ship geometry stitches.** Bake them into the normal map and diffuse (see §12).

## 10. Folds, wear and believability (P 5:05–6:39, 9:37)

- Add **Multires** and subdivide a few levels. Sculpt flex creases with **Draw** at the toe break and ankle, hold Ctrl for deeper grooves, and add irregularities with **Inflate**. Concentrate them where the shoe bends and around the lacing.
- Add volume beside the laces so the upper looks pulled tight.
- Final proportion pass in Sculpt: shorten the toe and heel with Grab (P 10:04).

## 11. Materials and render (B, from frames)

- **UV-unwrap every panel separately**, with seams along the panel borders. Lay each island over the leather normal map in the UV editor (B 3:00–12:00).
- **ambientCG leather PBR** (colour, normal, roughness) set up with Node Wrangler, Mapping **Scale about 2–3** (one frame shows 3/3/2).
- For black leather, mix the colour with a black RGB node, or set the base colour black and keep the leather normal (B 6:00–9:00, captions "Black Leather", "Just change the Color to Black").
- **Fabric** for the collar lining and tongue, a separate rubber/foam material for the midsole, and a **Noise texture into Bump** for the final micro-surface (B 42:00).
- Cycles studio render with a gradient backdrop (B 42:30).
- Normal bake for a game mesh (T 6:56, from frames): New Image **2048×2048**, Bake Type **Normal**, Space **Tangent**, **Selected to Active** with a **Cage** object, Target Image Textures.
