# Product modeling techniques

Timestamps cite the source videos (ids in `sources.md`). "(from frames)" = read off the video image, not narrated.

## 1. References and real dimensions

1. Take dimensions from the maker's spec sheet (height × width × depth in mm, display diagonal). Take positions of buttons, lenses and lugs from orthographic product photos. Neither video does this. 8UKNKSnminQ just scales the body to a reference image, which gave nonsense units: a 0.72 m corner bevel and a 0.36 m thickness (from frames, 2:48). **Mistake to avoid:** set Scene Units = Metric with Length = Millimeters, and model at real size, e.g. phone 163.4 × 78.0 mm (iPhone 18 Pro Max per the user's own phone spec). A GTA prop must end at real metres anyway.
2. Reference setup:
   - iPhone (0:50–1:14): Shift+A > Image > Reference. One image holding front, back and side views is pushed back on Y. Work in X-ray (Alt+Z) in front ortho (Numpad 1).
   - Watch (0:00–4:00, from frames): separate image empties for front, back, left and right in a `reference` collection.
   - Scale each reference image so its outline matches the spec dimensions. Do not scale the model to fit the image.
3. Apply transforms before anything mirrors or bevels. The watch's Z mirror failed because rotation was not applied. Fix: Ctrl+A > Rotation & Scale (Rg8kUXj842w 2:14).

## 2. Body blockout: rounded rectangle (slab devices: phone, tablet, remote)

Method A, modifier-only (8UKNKSnminQ 1:14–2:58):
1. Add a Cube. In Edit mode, face select (3), delete every face except the front one, so you get a quad plane. Ctrl+A > All Transforms, then Set Origin > Origin to Geometry. Scale it to the outline (S Z, etc.) and apply scale again.
2. Add a **Bevel modifier set to Vertices**, which rounds the 4 corners of the plane into a rounded rectangle. On screen: Offset 0.72 m, Segments 10, Limit Angle 30° (from frames). In mm units, use the real corner radius and 8–12 segments.
3. Add **Solidify**: Mode Simple, Offset −1, **Even Thickness ON**, Rim Fill (from frames: 0.36 m). For a real product, thickness = spec depth minus the camera bump.
4. Right-click > Shade Auto Smooth. In 4.1+ this adds a "Smooth by Angle" modifier at 30° (from frames).
5. Add a second **Bevel (Edges)** to round the rim edges: "take your time to adjust all the segments" (2:58).
6. Apply all (Ctrl+A over each modifier, 7:07) before the screen inset and the booleans.

Method B, SubD-ready (watch case, Rg8kUXj842w 0:00–3:40):
- Start from a Cylinder with **48 segments** "to support the details" (0:06).
- Block out the lugs: Ctrl+R loop cut, slide verts (G G), extrude faces. Give the longer side one extra loop "to keep the face sizes balanced", and finish with a **diamond quad** (0:25–1:18).
- Build one lug, then a Mirror modifier on X and Z (2:14).
- Re-round loops that got distorted with **LoopTools > Circle** (2:36).
- Close the round back/top with Poke (triangle fan) or **Grid Fill** for quads (3:38).
- For ports, sensors and slots use **Knife Project** (an outline object projected straight down, 4:31) or a boolean, then fix the topology on one half only because the mesh is symmetric. Turn **Auto Merge Vertices** on when sliding verts together to merge them (5:28).

Choose by target: A is fast and accurate for renders. B is needed when you will run SubD, and its flow is cleaner to decimate later for a game LOD.

## 3. Buttons, ports, slots

- iPhone (3:15–7:07): each button is the same plane → Bevel(vertices) → Solidify object. Shift+D to duplicate it, R Z 90 to stand it on the side, align in top view (Numpad 7). Then add a **Boolean modifier on the body, Object = the button**: the same object cuts its own slot and stays as the visible key. Do the USB-C port and speaker holes the same way. Apply all modifiers when done.
- Watch (7:45–12:23):
  - Keep cutters simple ("just eight segments", 7:45).
  - Snap the button origin to the world center so it can be spun around the round case (8:23).
  - After the cut, rebuild quads by hand with J (Vertex Connect Path) and vertex slide (from frames, 9:00–9:40).
  - Turn Auto Merge off, then duplicate the hole faces, Separate (P), and extrude them out to form the push-button.
  - Set Pivot = **Individual Origins**, then scale so each button tip tapers toward its own centre (12:23).
- Screen bezel (8UKNKSnminQ 7:22): select the front face, **I** to inset (this sets the bezel width), Alt+Shift-click to select the ring of faces, E to extrude them **inward** so the glass sits in a shallow cavity. The watch display: a separate disc of **16 segments** is enough (13:14).

## 4. Camera bump and lenses (8UKNKSnminQ 7:58–12:41)

1. Camera plateau: the same plane → Bevel(vertices) → Solidify block. Place it on the back and apply.
2. Ctrl+R loop cut, then scale the innermost edge loop. Alt-click the middle loop and **Ctrl+B with the mouse wheel to add bevel loops**, which gives the soft rise from the back glass (9:27).
3. Add **Subdivision (Catmull-Clark, 2/2)**, followed by **Bevel (Edges): Offset 0.05 m, 15 segments, Limit Angle 30°** (from frames, 9:49). Inset (I) any face that pinches after SubD.
4. Lens ring: add a Cylinder and rotate it 90° on X. Select the front and back cap loops, then **Edge > Bridge Edge Loops** to make a tube. Add Bevel + SubD, then on the front faces Inset (I) and Extrude (E) outward (10:19–11:16).
5. Shift+D the ring to the other two positions, Ctrl+J to join them into one object, then G Y to sit them on the plateau.
6. Antenna-band lines on the frame: four small boxes mark the positions, then in X-ray use the Knife (K) with **X to constrain the cut to the X axis** on the top and bottom edges. These cuts only exist to carry a different material (12:11).
7. Flash and LiDAR are booleans like the buttons.

## 5. Straps and bands (Rg8kUXj842w 13:58–26:23)

- "Addition, not subtraction" (13:58): don't punch holes in a strip. Build **one** strap module around a single slot: a circle split in half and extruded into a stadium shape, then quad faces built around it (from frames, 14:00–14:40). Add **Mirror + Array** (Fixed Count, Relative Offset along the length, Merge on; from frames, 15:00) to repeat it.
- After applying the array: select one of the duplicate seam edges > **Select Similar > Length** > Dissolve them all at once (15:39).
- Taper the tail with Ctrl+R loops and slides. Use fewer edges where the area is simple.
- When the shading looks wrong, show face orientation and **Recalculate Normals** (Shift+N) (17:01).
- Use **Extrude Manifold** instead of plain E, because it doesn't add useless loops (17:27).
- Ctrl+J join works like a Boolean Union for pieces that only need to touch (20:20).
- Add support loops by hand where a rounding looks too soft (21:34). Redirect the edge flow at transitions so SubD shades cleanly (23:48).
- The second strap is a duplicate with adjustments (22:49).
- Curl the strap around the wrist with a **Simple Deform modifier set to Bend**. Set the origin first, then dial the angle (25:27). The keeper loop is a Solidify ring (from frames, 26:40).

## 6. Edge treatment: bevel weights + SubD vs bevel + weighted normals

Watch stack (Rg8kUXj842w 10:07–11:42, values from frames):
1. Mesh > Select Sharp Edges, then also hand-pick a few. Set **Bevel Weight = 1** on them (N panel > Edge Data).
2. Add Bevel: **Edges, Limit Method = Weight (`bevel_weight_edge`), Segments 2**. Then Ctrl+2 adds **Subdivision Catmull-Clark, Viewport 2 / Render 2**.
3. An Offset width "looked overdone / unrealistic". Switch to **Width Type = Percent, 10 %** for the case and **14 %** for the strap (from frames, 24:40).
4. Geometry: **Miter Outer = Arc** (fixes an artifact at a corner), Inner = Sharp, Intersections = Grid Fill, Clamp Overlap ON, Loop Slide ON.
5. A soft or blobby transition means the support edges are too far apart: add an edge loop (11:21). A shading dent at a triangle fan: inset the fan and pull it to the centre (11:42).

For a game prop, SubD is too heavy (the case alone reached roughly 100–190k triangles; read from the stats overlay in frames around 11:00–13:20). Use instead: Bevel with 1–3 segments → **Harden Normals** (the Bevel option; Blender adds the custom normal attribute automatically) or a **Weighted Normal** modifier (Keep Sharp) placed after the bevel. The bevel makes the highlight; the weighted normals fix the flat-face shading. See the sources list for documentation.

## 7. Materials and render (8UKNKSnminQ 12:54–17:50)

Name materials; Ctrl+L > Link Materials copies one to the selected objects.

| Part | Principled settings |
|---|---|
| Silver/titanium frame and camera plateau | Metallic 1, low roughness |
| Inner cavities / port walls ("black rough") | Black, roughness 1, assigned to inner faces in Edit mode |
| Lens, LiDAR, camera glass | Black, **roughness 0, IOR 1.4, Transmission 0.8**, plus a Ctrl+B bevel on the glass edge |
| Screen | Black, low roughness (frames: about #282828, roughness 0.5). For a lit screen, add an Emission image with strength about 1–3 (not in the video) |
| Flash | Wave Texture set to **Rings** → Metallic, with Ctrl+T (Node Wrangler) Mapping to size and centre the rings |
| Back glass ("ceramic") | Duplicate of silver, brighter base colour |
| Antenna bands | Duplicate of silver, slightly darker |

- Logo: Shift+A > Image > Mesh Plane with a transparent PNG (16:15). For FiveM, replace real brands with GTA equivalents, e.g. Apple → iFruit, per the user's branding rule.
- Fake lens interior: an Image Texture of real lenses. On the glass, U > **Project from View**, then line up the three circles in the UV editor (16:37).
- Organisation: Shift+A > Empty > Cube, select all parts and then the empty last, **Ctrl+P > Object (Keep Transform)**. One handle then moves the whole product for turntables (17:26).
- Lighting is an HDRI world in Material Preview (from frames). Anodized or brushed metal is not shown in either video. Use Metallic 1 + coloured base + Anisotropic 0.5–0.8 with a tangent along the brush direction (standard Principled options; not from these videos).

---

## 9. Common mistakes (consolidated)

- Modeling to image scale instead of spec mm (8UKNKSnminQ). Unapplied rotation/scale breaking Mirror (Rg8kUXj842w 2:14).
- Uniform Offset bevel looks fake: use Percent width + Miter Outer Arc. Blobby SubD means support loops are too far apart.
- Messy boolean topology on a SubD mesh: keep cutters low-segment (8), clean up with J or vertex slide, and keep Auto Merge on while sliding.
- Normals flipped after extrudes (Shift+N). Plain extrude adding junk loops (use Extrude Manifold).
- Shipping raw AI meshes (about 590k triangles) or using them as collision. Forgetting the collision Flag Preset. Not saving packed textures before export.
- A real brand logo on a FiveM prop: swap it for the GTA in-universe brand.
