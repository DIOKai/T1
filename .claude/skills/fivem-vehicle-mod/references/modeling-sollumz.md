# How modded vehicles are built (Blender + Sollumz)

Sources: Sollumz wiki (Creating Vehicles tutorial; Fragments → Vehicle Setup: import/export settings, windows, light IDs, paint colours, wheels; Vehicle Shaders), Sollumz source (`sollumz_properties.py` light ids), muto-atlas bone tags.

Most add-on cars are built one of two ways:
1. **Edit a vanilla car** — import a similar vanilla `.yft` (its armature, bones, collisions and shaders are already right), then swap or reshape parts. Fastest, fewest bugs, and the usual start for police cars.
2. **Custom model on a vanilla skeleton** — model in Blender (or import an FBX you have the rights to), then fit it to a vanilla car's armature: move bones to the new geometry, assign vertex groups, shaders, collisions, LODs.

Ripped models from other games or paid mods are not the user's to distribute; avoid them for a public server.

## 1. Import a base

- Export the vanilla car from **the user's own game** with CodeWalker (`.yft` + `_hi.yft` + `.ytd`) to XML; put textures in a folder with the **same name as the fragment** next to it.
- Sollumz import settings: **Split By Group** (one object per vertex group, each with an Armature modifier — what you want for vehicles) and **Import with _hi** (puts the `_hi.yft` mesh into the *Very High* LOD so you edit both files at once; select the non-hi file when importing).
- Wheels: only `wheel_lf` is a mesh; the game instances it for the others. Wheel meshes are rigged with a Child Of constraint and have *Is Wheel Mesh* ticked. *Generate Wheel Instances* previews the rest.

## 2. Model parts and rig them

- New part → material from the vehicle shader list → **vertex group named after the bone** (e.g. `bonnet`), assign all its faces → move the Drawable Model under the car's `.mesh` object → **Armature modifier** targeting the car's armature. Delete the replaced vanilla part.
- Fully custom body: in Edit Mode (Solid + X-Ray) move the bones to the new geometry — doors to their hinge axis, wheels to the wheel centres, seats, steering, exhausts.
- **Bone names must be GTA's exact names** (`door_dside_f`, `wheel_lf`, `bonnet`, `boot`, `siren1`…, `extra_1`…) — look them up with muto-atlas `/vehicle` or its `trunk/bone-tags.md`. Pitfalls recorded there: **extra 10 is `extra_ten`**, `extra_11`/`extra_12` sit in a separate tag block, `mod_col_10` breaks the pattern. Don't use the generic `SM_Vehicle_*` names from game-art skills.
- If you **added** bones (e.g. rear doors on a 2-door base), tick *Auto Calculate Bonetags* on export; if you changed collision shapes, tick *Auto Calculate Inertia* and *Auto Calculate Volume*. Leave them off otherwise.

## 3. Shaders, paint, lights, glass

- Body: `vehicle_paint1` family (diffuse, dirt, specular; UV0 diffuse/specular, UV1 dirt). In *Material → Sollumz → Fragment (Vehicle Paint)* choose the paint layer: Primary, Secondary, Pearlescent (colour only), Wheel, Interior Trim, Dashboard, or not paintable. Only shaders with `matDiffuseColor` are paintable.
- Vehicle vertex colours mean something different from map ones: **R = ambient occlusion, G = body deformation, B = burn level**.
- Lights: meshes with `vehicle_lightsemissive` glow all the time unless faces get a **light ID** (*Sollumz Tools → Fragment → Vehicle Light IDs*): 0 always on, 1/2 headlight L/R, 3/4 taillight L/R, 5–8 indicators LF/RF/LR/RR, 9/10/11 brake L/R/middle, 12/13 reversing L/R, 14–17 extralight 1–4.
- Windows: glass mesh with `VEHICLE VEHGLASS` (inner pane `VEHGLASS INNER`), skinned to a bone with physics and a collision using a *Car Glass* material; shattermap mode **Auto** (needs the optional PyMateria dependency), **Simple** for siren glass (breaks completely, no shattermap), **Manual** only with your own shattermap image. Blue vertex channel marks glass edges attached to the frame.

## 4. LODs and export

- *Data → Sollumz LOD*: give every part High, Medium, Low (and Very High for the `_hi.yft`). Real reduced meshes for Medium/Low save a lot of performance; copying the High mesh into all levels works but costs FPS in traffic. Keep LOD0 under ~50k triangles (project rule).
- *Export Codewalker XML → Fragment → Toggle LODs* exports the hi file, the non-hi file or both. Compile the XML in CodeWalker RPF Explorer, then build the resource per `resource-and-meta.md` and run `check_vehicle_resource.py`.
- After export, test: doors, bonnet and boot open; wheels turn and steer; lights match their switches; windows break; paint changes the right panels; damage deforms.
